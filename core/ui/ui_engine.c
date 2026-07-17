/*
 * core/engines/ui_engine.c
 *
 * 🪰 ANKA OS - GÖLGE KATMAN VE ARAYÜZ MOTORU
 * Chatly Framebuffer Altyapısı + Anka OS Otonom Zihin Entegrasyonu
 */

#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#include "ui_engine.h"
#include "fly_engine.h" // Sinek otonom durumları (FLY_GHOST, FLY_MIRROR vb.)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/fb.h>
#include <time.h>

/* ═══════════════════════════════════════════════════════════════════════════
 * 8x8 BİTMAP FONT (Chatly tarafından oluşturulan donanımsal font)
 * (Kısa tutulmuştur, orijinal Chatly kodundaki 96 karakterlik font dizisi buraya gelecek)
 * ═══════════════════════════════════════════════════════════════════════════ */
static const uint8_t font8x8_basic[96][8] = {
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, /* 32: Space */
    { 0x18, 0x3C, 0x3C, 0x18, 0x18, 0x00, 0x18, 0x00 }, /* 33: ! */
    /* ... (Chatly'nin verdiği font dizisinin tamamı burada olacak) ... */
    { 0x00, 0x00, 0x3F, 0x19, 0x0C, 0x26, 0x3F, 0x00 }, /* 122: z */
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, /* 127: DEL */
};

/* --- Chatly'nin yazdığı temel Framebuffer fonksiyonları (Buraya dokunmuyoruz) --- */
// (Burada fb_open, fb_close, fb_put_pixel, fb_fill_rect, fb_clear, 
// fb_draw_text_scaled, fb_load_bmp_centered fonksiyonlarının Chatly kodları yer alıyor)

/* ═══════════════════════════════════════════════════════════════════════════
 * ANKA OS - ÖZEL GÖREV FONKSİYONLARI (ESKİ KODUN YENİ HALİ)
 * ═══════════════════════════════════════════════════════════════════════════ */

/* ─── UYANIŞ SEKANSI (AÇILIŞ ANİMASYONU) ─── */
void anka_boot_sequence(fb_context_t *fb) {
    if (!fb || !fb->map) return;

    // 1. Ekranı tamamen siyah yap
    fb_clear(fb, 0, 0, 0);
    
    // 2. Terminal estetiğinde yeşil kod akışı (x=50, y=100'den başlar)
    // usleep ile ekranda akıyormuş hissiyatı veriyoruz.
    fb_draw_text_scaled(fb, 50, 150, "[OK] Anka_Core Init...", 3, 0, 255, 0);
    usleep(600000); // 0.6 saniye bekle
    
    fb_draw_text_scaled(fb, 50, 250, "[OK] Kuantum Tozlari Aktif...", 3, 0, 255, 0);
    usleep(600000);
    
    fb_draw_text_scaled(fb, 50, 350, "[OK] Omni Sensorler Cevrimici...", 3, 0, 255, 0);
    usleep(800000);

    // 3. Ekranı temizle ve Sinek Görselini merkeze bas
    fb_clear(fb, 0, 0, 0);
    fb_load_bmp_centered(fb, "assets/sinek_icon.bmp");

    // 4. Donanım Tetikleyicileri (Titreşim ve Ses)
    // Note 9'un sysfs vibrator portuna doğrudan komut gönderir.
    system("su -c 'echo 150 > /sys/class/timed_output/vibrator/enable' 2>/dev/null");
    // ALSA veya tinyplay üzerinden uyanış sesi çalar (audio_engine arka planı)
    system("su -c 'tinyplay assets/awake.wav' 2>/dev/null &");
    
    usleep(1000000); // Sinek 1 saniye ekranda ihtişamla kalsın
}

/* ─── GÜNLÜK ARAYÜZ (ESKİ ui_render) ─── */
// Artık system("fbi...") yerine doğrudan belleğe çizim yapıyoruz.
void ui_render(fb_context_t *fb, const char *last_message) {
    if (!fb || !fb->map) return;

    // Sinek durumunu güncelle (fly_engine.h'den gelir)
    update_fly_behavior(); 

    // GHOST modu: Sistem tamamen karanlığa gömülür, sadece arka planda dinler
    if (current_state == FLY_GHOST) {
        fb_clear(fb, 0, 0, 0);
        return; 
    }
    
    // Zaman bazlı tema motoru (eski is_day mantığı)
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    int is_day = (tm->tm_hour >= 7 && tm->tm_hour <= 18) ? 1 : 0;

    // Renkleri temaya göre ayarla
    uint8_t bg_r = is_day ? 220 : 10;
    uint8_t bg_g = is_day ? 220 : 15;
    uint8_t bg_b = is_day ? 220 : 20;

    uint8_t text_r = is_day ? 0 : 0;
    uint8_t text_g = is_day ? 0 : 255; // Gece modunda siberpunk yeşili
    uint8_t text_b = is_day ? 0 : 0;

    // Arka planı boya
    fb_clear(fb, bg_r, bg_g, bg_b);

    // Üst Bilgi Barı
    if (is_day) {
        fb_draw_text_scaled(fb, 50, 50, "[--- GUNDUZ ARAYUZU ---]", 3, 50, 50, 50);
    } else {
        fb_draw_text_scaled(fb, 50, 50, "[--- SIBERPUNK NEON GECE ---]", 3, 0, 255, 0);
    }

    // Duruma göre BMP görselini merkeze yükle (GIF yerine BMP kullanıyoruz)
    if (current_state == FLY_MIRROR) {
        fb_load_bmp_centered(fb, "assets/sinek_ayna.bmp");
    } else if (current_state == FLY_THINK) {
        fb_load_bmp_centered(fb, "assets/sinek_dusunen.bmp");
    } else {
        fb_load_bmp_centered(fb, "assets/sinek_ucuyor.bmp");
    }

    // Alt kısma sohbeti / mesajı yazdır
    if (last_message != NULL) {
        // "SINEK:" başlığı
        fb_draw_text_scaled(fb, 50, fb->height - 200, "SINEK:", 4, text_r, text_g, text_b);
        // Gelen mesaj (Ölçek 3 ile okunabilir boyutta)
        fb_draw_text_scaled(fb, 50, fb->height - 130, last_message, 3, text_r, text_g, text_b);
        
        // İmza durumu kontrolü
        if (strstr(last_message, "[FLY_SIGNATURE_ICON]")) {
            // Sağ alt köşeye minik imza ikonunu bas
            fb_load_bmp(fb, "assets/sinek_icon.bmp", fb->width - 150, fb->height - 150);
        }
    }
}
