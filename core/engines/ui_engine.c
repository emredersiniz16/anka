#include <stdio.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include "fly_engine.c" // FlyState ve durum yönetimi eklendi

// --- İMZA MOTORU ---
void render_fly_signature(int x, int y) {
    char sign_cmd[512];
    sprintf(sign_cmd, "fbi -d /dev/fb0 -g 32x32+%d+%d -a -noverbose -T 1 assets/sinek_icon.bmp &", x, y);
    system(sign_cmd);
}

// --- TEMA VE ARAYÜZ ---
void draw_ui_window(const char *message, int is_day) {
    if (is_day) {
        printf("\n[--- YÜKSEK KONTRAST GÜNDÜZ ARAYÜZÜ ---]\n");
    } else {
        printf("\n[--- SİBERPUNK NEON GECE ARAYÜZÜ ---]\n");
    }
    printf("🪰 SİNEK: %s\n", message);
}

// --- ANA UI RENDER ---
void ui_render(const char *last_message) {
    update_fly_behavior(); // Her karede durumu güncelle (Nexus/Jammer kontrolü)

    // GHOST modu: Sistem tamamen saydamlaşır
    if (current_state == FLY_GHOST) {
        system("clear");
        return; 
    }

    int fb_fd = open("/dev/fb0", O_RDONLY);
    if (fb_fd < 0) return;
    struct fb_var_screeninfo vinfo;
    ioctl(fb_fd, FBIOGET_VSCREENINFO, &vinfo);
    close(fb_fd);

    int w = vinfo.xres;
    int h = vinfo.yres;
    
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    int is_day = (tm->tm_hour >= 7 && tm->tm_hour <= 18) ? 1 : 0;

    // SİNEK DURUMUNA GÖRE GÖRSELLEŞTİRME (YEDEKLEMELİ / FALLBACK)
    char fly_cmd[512];
    if (current_state == FLY_MIRROR) {
        // Yansıtma: Ayna GIF'i yoksa uçan sineğe dön
        sprintf(fly_cmd, "fbi -d /dev/fb0 -g 250x250+%d+%d -a -noverbose -T 1 assets/sinek_ayna.GIF || fbi -d /dev/fb0 -g 150x150+%d+%d -a -noverbose -T 1 assets/sinek_ucuyor.GIF &", w/2 - 125, h/2 - 125, w - 250, 50);
    } else if (current_state == FLY_THINK) {
        // Düşünme: Düşünen GIF yoksa uçan sineğe dön
        sprintf(fly_cmd, "fbi -d /dev/fb0 -g 200x200+%d+%d -a -noverbose -T 1 assets/sinek_dusunen.GIF || fbi -d /dev/fb0 -g 150x150+%d+%d -a -noverbose -T 1 assets/sinek_ucuyor.GIF &", w/2 - 100, h/2 - 100, w - 250, 50);
    } else {
        // İdle/Normal: Standart uçuş
        sprintf(fly_cmd, "fbi -d /dev/fb0 -g 150x150+%d+%d -a -noverbose -T 1 assets/sinek_ucuyor.GIF &", w - 250, 50);
    }
    system(fly_cmd);

    // MESAJ VE İMZA
    if (last_message != NULL) {
        draw_ui_window(last_message, is_day);
        if (strstr(last_message, "[FLY_SIGNATURE_ICON]")) {
            render_fly_signature(w - 60, h - 60); 
        }
    }
}
