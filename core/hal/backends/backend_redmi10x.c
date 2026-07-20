/* core/hal/backends/backend_redmi10x.c
 * 🪰 [HAL] Xiaomi Redmi 10X 4G (M2004J7AC) backend.
 * [SİSTEM]: Qualcomm Snapdragon 665 (SDM665/SDM660 sınıfı) SoC.
 *
 * Donanım notları:
 *   - SoC: Qualcomm Snapdragon 665 (SDM665 / SDM660 benzer sürücü ailesi)
 *   - Dokunmatik: /dev/input/event4
 *     (orijinal touch_engine.c yolu; açıklama: bu path touch_engine.c'den gelir)
 *   - Titreşim: /sys/class/leds/vibrator/ (Qualcomm LED sürücüsü)
 *     (Samsung'un timed_output'u değil — farklı sysfs yapısı)
 *   - ALSA: plughw:1,0 (Redmi Note 9 / 10X ses kartı farklı indeks kullanır)
 *   - Kamera: /dev/video0 via fswebcam
 *     (v4l2 quirk: bazı firmware sürümlerinde buffer VIDIOC_REQBUFS hatası verir;
 *      workaround: --no-timestamp flag eklenir)
 *   - Backlight: /sys/class/backlight/panel0-backlight/brightness
 *     (veya /sys/class/leds/lcd-backlight/brightness, firmware bağımlı)
 *   - Qualcomm MSM platform: /sys/bus/platform/drivers/msm
 *
 * UYARI: system() çağrısı YOK. Tüm harici araçlar fork()+execvp() ile çalıştırılır.
 */

#include "backend_table.h"
#include "../hal_common.h"
#include "../hal_input.h"
#include "../hal_audio.h"
#include "../hal_display.h"
#include "../hal_sensors.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/select.h>
#include <pthread.h>
#include <linux/input.h>

/* ─────────────────────────────────────────────
 * Redmi 10X donanım sabitleri
 * ───────────────────────────────────────────── */

/*
 * Dokunmatik: /dev/input/event4
 * Orijinal touch_engine.c'den gelen path; Qualcomm dokunmatik
 * J7'den farklı olarak event4 adresinde görünür.
 */
#define REDMI_TOUCH_DEV         "/dev/input/event4"

/*
 * Qualcomm LED sürücüsü titreşim yolu.
 * Samsung timed_output: /sys/class/timed_output/vibrator/enable
 * Qualcomm leds:        /sys/class/leds/vibrator/activate
 *                       /sys/class/leds/vibrator/duration
 */
#define REDMI_VIB_DURATION_PATH "/sys/class/leds/vibrator/duration"
#define REDMI_VIB_ACTIVATE_PATH "/sys/class/leds/vibrator/activate"

/*
 * ALSA: plughw:1,0 — Redmi'nin ses kartı index'i J7'den farklı.
 * Birden fazla ses kartı olduğunda kart 1 kullanılır.
 */
#define REDMI_ALSA_DEVICE       "plughw:1,0"

#define REDMI_CAMERA_DEV        "/dev/video0"
#define REDMI_DISPLAY_W         1080
#define REDMI_DISPLAY_H         2400
#define REDMI_DISPLAY_DPI       395

/* Backlight — firmware bağımlı; önce birincil yolu dene */
#define REDMI_BACKLIGHT_PRIMARY  "/sys/class/backlight/panel0-backlight/brightness"
#define REDMI_BACKLIGHT_ALT      "/sys/class/leds/lcd-backlight/brightness"

/* ─────────────────────────────────────────────
 * Durum
 * ───────────────────────────────────────────── */
static pthread_mutex_t redmi_mutex      = PTHREAD_MUTEX_INITIALIZER;
static int             redmi_touch_fd   = -1;
static int             redmi_streaming  = 0;
static int             redmi_brightness = 128;
static hal_point_t     redmi_last_touch = {0, 0};

/* ─────────────────────────────────────────────
 * Dahili yardımcılar
 * ───────────────────────────────────────────── */
static int _redmi_path_exists(const char *path)
{
    struct stat st;
    return (stat(path, &st) == 0) ? 1 : 0;
}

static int _redmi_cpuinfo_contains(const char *needle)
{
    FILE *f = fopen("/proc/cpuinfo", "r");
    if (!f) return 0;
    char line[256];
    int found = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strstr(line, needle)) { found = 1; break; }
    }
    fclose(f);
    return found;
}

static int _redmi_run(char *const argv[])
{
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid == 0) { execvp(argv[0], argv); _exit(127); }
    int status = 0;
    if (waitpid(pid, &status, 0) < 0) return -1;
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

/* Backlight yolu belirle (firmware bağımlı) */
static const char *_redmi_backlight_path(void)
{
    if (_redmi_path_exists(REDMI_BACKLIGHT_PRIMARY))
        return REDMI_BACKLIGHT_PRIMARY;
    return REDMI_BACKLIGHT_ALT;
}

/* ─────────────────────────────────────────────
 * probe
 * ───────────────────────────────────────────── */
static int redmi_probe(void)
{
    int score = 0;

    /* SDM660/665 CPU tespit */
    if (_redmi_cpuinfo_contains("SDM660") ||
        _redmi_cpuinfo_contains("SDM665") ||
        _redmi_cpuinfo_contains("Qualcomm") ||
        _redmi_cpuinfo_contains("sm6115")) {
        HAL_LOG_INFO("HAL:REDMI", "probe: Qualcomm SoC tespit edildi");
        score += 50;
    }

    /* Qualcomm MSM platform sürücüsü varlığı */
    if (_redmi_path_exists("/sys/bus/platform/drivers/msm")) {
        HAL_LOG_INFO("HAL:REDMI", "probe: MSM platform sürücüsü bulundu");
        score += 20;
    }

    /* Qualcomm LED titreşim sürücüsü (Samsung'dan ayrışma) */
    if (_redmi_path_exists("/sys/class/leds/vibrator")) {
        HAL_LOG_INFO("HAL:REDMI", "probe: Qualcomm LED vibrator bulundu");
        score += 15;
    }

    /* Samsung timed_output YOKSA ek puan (J7'den ayrışma) */
    if (!_redmi_path_exists("/sys/class/timed_output/vibrator")) {
        score += 10;
    }

    HAL_LOG_INFO("HAL:REDMI", "probe: güven=%d", score > 100 ? 100 : score);
    return score > 100 ? 100 : score;
}

/* ─────────────────────────────────────────────
 * init / shutdown
 * ───────────────────────────────────────────── */
static hal_status_t redmi_init(void)
{
    HAL_LOG_INFO("HAL:REDMI",
        "🪰 Redmi 10X 4G backend başlatılıyor (SDM660/665)");
    redmi_brightness = 128;
    redmi_streaming  = 0;
    return HAL_OK;
}

static void redmi_shutdown(void)
{
    HAL_LOG_INFO("HAL:REDMI", "Redmi 10X backend kapatılıyor");
    pthread_mutex_lock(&redmi_mutex);
    if (redmi_touch_fd >= 0) {
        close(redmi_touch_fd);
        redmi_touch_fd = -1;
    }
    redmi_streaming = 0;
    pthread_mutex_unlock(&redmi_mutex);
}

/* ─────────────────────────────────────────────
 * Input Subsystem
 * /dev/input/event4 — touch_engine.c orijinal yolu
 * ───────────────────────────────────────────── */
static hal_status_t redmi_input_init(void)
{
    pthread_mutex_lock(&redmi_mutex);
    if (redmi_touch_fd >= 0) {
        pthread_mutex_unlock(&redmi_mutex);
        return HAL_OK;
    }

    redmi_touch_fd = open(REDMI_TOUCH_DEV, O_RDONLY | O_NONBLOCK);
    if (redmi_touch_fd < 0) {
        HAL_LOG_INFO("HAL:REDMI",
            "Dokunmatik açılamadı: %s (errno=%d)", REDMI_TOUCH_DEV, errno);
        pthread_mutex_unlock(&redmi_mutex);
        return HAL_ERR_IO;
    }

    pthread_mutex_unlock(&redmi_mutex);
    HAL_LOG_INFO("HAL:REDMI",
        "Dokunmatik açıldı: %s fd=%d", REDMI_TOUCH_DEV, redmi_touch_fd);
    return HAL_OK;
}

static void redmi_input_shutdown(void)
{
    pthread_mutex_lock(&redmi_mutex);
    if (redmi_touch_fd >= 0) {
        close(redmi_touch_
