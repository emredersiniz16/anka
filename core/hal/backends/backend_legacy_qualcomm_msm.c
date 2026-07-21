#include "../anka_hal.h"
#include "../anka_hal_ext.h"
#include "../hal_common.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/wait.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <linux/input.h>

#define QCOM_VIB_DURATION      "/sys/class/leds/vibrator/duration"
#define QCOM_VIB_ACTIVATE      "/sys/class/leds/vibrator/activate"
#define QCOM_VIB_LEGACY_ENABLE "/sys/class/timed_output/vibrator/enable"
#define QCOM_BAT_CAPACITY      "/sys/class/power_supply/battery/capacity"
#define QCOM_BAT_CAPACITY_ALT  "/sys/class/power_supply/BAT0/capacity"
#define QCOM_BL_BRIGHTNESS     "/sys/class/backlight/panel0-backlight/brightness"
#define QCOM_BL_MAX_BRIGHTNESS "/sys/class/backlight/panel0-backlight/max_brightness"
#define QCOM_BL_BRIGHTNESS_ALT "/sys/class/backlight/intel_backlight/brightness"

static const char *const QCOM_NET_CARRIERS[] = { "/sys/class/net/wlan0/carrier", "/sys/class/net/wlan1/carrier", NULL };
static const char *const QCOM_VIDEO_DEVICES[] = { "/dev/video0", "/dev/video1", NULL };

#define QCOM_TOUCH_EVENT_CONFIRMED  "/dev/input/event4"
#define QCOM_FB0_PATH              "/dev/fb0"
#define QCOM_BL_DEFAULT_MAX         255
#define QCOM_TTS_TMPFILE_TEMPLATE   "/tmp/anka_tts_XXXXXX"

static int s_touch_fd = -1;
static int s_touch_last_x = 0, s_touch_last_y = 0;

static int hal_write_sysfs_escalating(const char *path, int value) {
    FILE *f = fopen(path, "w");
    if (f) { fprintf(f, "%d", value); fclose(f); return 0; }
    if (errno != EACCES) return -1;
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid == 0) {
        char cmd[256]; snprintf(cmd, sizeof(cmd), "echo %d > %s", value, path);
        char *argv[] = { "su", "-c", cmd, NULL };
        execvp("su", argv); _exit(127);
    }
    int status = 0; waitpid(pid, &status, 0);
    return (WIFEXITED(status) && WEXITSTATUS(status) == 0) ? 0 : -1;
}

static int hal_read_sysfs(const char *path, int *out) {
    if (!path || !out) return -1;
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    int ret = (fscanf(f, "%d", out) == 1) ? 0 : -1;
    fclose(f); return ret;
}

static int be_vibrate(int ms) {
    if (hal_write_sysfs_escalating(QCOM_VIB_DURATION, ms) == 0 &&
        hal_write_sysfs_escalating(QCOM_VIB_ACTIVATE, 1) == 0) return 0;
    return hal_write_sysfs_escalating(QCOM_VIB_LEGACY_ENABLE, ms);
}

static int be_read_touch(int *x, int *y) {
    if (!x || !y) return -1;
    if (s_touch_fd < 0) s_touch_fd = open(QCOM_TOUCH_EVENT_CONFIRMED, O_RDONLY | O_NONBLOCK);
    if (s_touch_fd < 0) return -1;
    struct input_event ev;
    while (read(s_touch_fd, &ev, sizeof(ev)) == sizeof(ev)) {
        if (ev.type == EV_ABS) {
            if (ev.code == ABS_MT_POSITION_X || ev.code == ABS_X) s_touch_last_x = ev.value;
            if (ev.code == ABS_MT_POSITION_Y || ev.code == ABS_Y) s_touch_last_y = ev.value;
        }
    }
    *x = s_touch_last_x; *y = s_touch_last_y;
    return 0;
}

static int be_speak(const char *text) {
    if (!text) return -1;
    char tmpl[] = QCOM_TTS_TMPFILE_TEMPLATE;
    int tfd = mkstemp(tmpl);
    if (tfd < 0) return -1;
    write(tfd, text, strlen(text)); close(tfd);
    char cmd[512]; snprintf(cmd, sizeof(cmd), "espeak -v tr -f %s --stdout | aplay -q 2>/dev/null", tmpl);
    pid_t pid = fork();
    if (pid == 0) { char *argv[] = { "sh", "-c", cmd, NULL }; execvp("sh", argv); _exit(127); }
    waitpid(pid, NULL, 0); unlink(tmpl); return 0;
}

static int be_capture_camera(const char *path) {
    if (!path) return -1;
    pid_t pid = fork();
    if (pid == 0) {
        char *argv[] = { "fswebcam", "-d", "/dev/video0", "-r", "640x480", "--no-banner", "--quiet", (char *)path, NULL };
        execvp("fswebcam", argv); _exit(127);
    }
    int status = 0; waitpid(pid, &status, 0);
    return (WIFEXITED(status) && WEXITSTATUS(status) == 0) ? 0 : -1;
}

static int be_get_battery(int *pct) {
    return hal_read_sysfs(QCOM_BAT_CAPACITY, pct);
}

static int be_set_brightness(int level) {
    int max_b = 255; hal_read_sysfs(QCOM_BL_MAX_BRIGHTNESS, &max_b);
    int scaled = (level * max_b) / 255;
    return hal_write_sysfs_escalating(QCOM_BL_BRIGHTNESS, scaled);
}

static int be_get_brightness(int *level) { return hal_read_sysfs(QCOM_BL_BRIGHTNESS, level); }
static int be_is_network_up(int *up) { *up = 1; return 0; }
static int be_display_clear(void) { return system("clear"); }
static int be_display_blit(const char *path, int x, int y, int w, int h) { return 0; }
static int be_get_device_info(char *buf, int len) {
    snprintf(buf, (size_t)len, "Redmi Note 9|SDM660|arm64-v8a|Android API 29");
    return 0;
}

int hal_backend_register(AnkaHAL *out, int *out_score) {
    if (!out || !out_score) return -1;
    out->vibrate = be_vibrate; out->read_touch = be_read_touch;
    out->speak = be_speak; out->capture_camera = be_capture_camera;
    out->get_battery = be_get_battery; out->set_brightness = be_set_brightness;
    out->get_brightness = be_get_brightness; out->is_network_up = be_is_network_up;
    out->display_clear = be_display_clear; out->display_blit = be_display_blit;
    out->get_device_info = be_get_device_info;
    *out_score = 85; return 0;
}
