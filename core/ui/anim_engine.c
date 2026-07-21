/*
 * core/ui/anim_engine.c
 * BİRLEŞTİRİLMİŞ: Uyanış Sekansı + Koordinat Motoru
 */

#define _DEFAULT_SOURCE
#define _BSD_SOURCE
#include "anim_engine.h"
#include "ui_engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

extern int audio_play_awakening(void);

// Terminal akışı ve ASCII yedekler burada (değişmedi)
static const char *BOOT_LINES[] = {
    "[OK] Anka_Core Init...", "[OK] HAL Backend Yuklendi",
    "[OK] Kuantum Tozlari Aktif", "[OK] Sinek Bilinc Uyaniyor",
    "[OK] Kovan Baglantisi Hazir", "[OK] Donanim Koprusu Kuruldu",
    "[OK] Golge Katman Aktif", "[OK] Sinek Gozlerini Aciyor...", NULL
};
static const int BOOT_LINE_COUNT = 8;

/* ═══════════════════════════════════════════════════════════════════════════
 * SİNEK GÖRSEL VE KOORDİNAT MOTORU (Entegrasyon)
 * Artık pkill veya fbi yok, doğrudan Framebuffer'a (VRAM) yazıyor.
 * ═══════════════════════════════════════════════════════════════════════════ */
void anim_update_fly_state(fb_context_t *fb, int current_state, float scale) {
    if (!fb || !fb->map) return;

    // Sinek boyutları
    int fly_w = (int)(250 * scale); 
    int fly_h = (int)(250 * scale); 

    // Koordinatlar: Ekranın sağ üst köşesindeki neon panelin içi
    int pos_x = (int)fb->width - fly_w - (int)(50 * scale); 
    int pos_y = (int)(80 * scale);

    if (current_state == 0) { // FLY_IDLE
        fprintf(stderr, "🪰 [GÖRSEL]: Sinek koordinata oturtuluyor (%d, %d)\n", pos_x, pos_y);
        fb_load_bmp(fb, "assets/sinek_ucuyor.bmp", pos_x, pos_y);
    } 
    else if (current_state == 1) { // FLY_THINK
        fprintf(stderr, "⚡ [BEYİN]: Düşünen Sinek (%d, %d)\n", pos_x, pos_y);
        fb_load_bmp(fb, "assets/sinek_dusunen.bmp", pos_x, pos_y);
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
 * UYANIŞ VE BOOT SEKANSLARI (Önceki fonksiyonların aynısı)
 * ═══════════════════════════════════════════════════════════════════════════ */

static void delay_ms(int ms) { if (ms <= 0) return; usleep((useconds_t)(ms * 1000)); }

static void draw_boot_line_with_blink(fb_context_t *fb, int x, int y, const char *line, int scale) {
    fb_draw_text_scaled(fb, x, y, line, scale, 0x00, 0xFF, 0x41);
    delay_ms(30);
    fb_draw_text_scaled(fb, x, y, line, scale, 0x00, 0x80, 0x20);
    delay_ms(40);
    fb_draw_text_scaled(fb, x, y, line, scale, 0x00, 0xFF, 0x41);
}

int anim_fly_appear(fb_context_t *fb, AnkaHAL *hal, const char *image_path, int vibrate_ms) {
    int bmp_rc = fb_load_bmp_centered(fb, image_path);
    
    if (hal && hal->vibrate) hal->vibrate(vibrate_ms);
    audio_play_awakening();
    if (hal && hal->speak) hal->speak("click");
    
    return bmp_rc;
}
/* ═══════════════════════════════════════════════════════════════════════════
 * anim_boot_run — Varsayılan konfigürasyon ile tam boot sekansı.
 * boot.c'nin çağırdığı giriş noktası. anim_boot_run_custom'a delege eder.
 * ═══════════════════════════════════════════════════════════════════════════ */
int anim_boot_run(fb_context_t *fb, AnkaHAL *hal) {
    anim_boot_config_t cfg = {
        .fb             = fb,
        .hal             = hal,
        .text_scale      = 3,        /* 24×24 px karakter (1080p için) */
        .line_delay_ms   = 250,      /* satırlar arası 250ms */
        .post_delay_ms   = 1000,     /* terminal sonrası 1s bekle */
        .vibrate_ms      = 400,      /* güçlü uyanış titreşimi */
        .fly_image_path  = "assets/fly_icon.bmp",
    };
    return anim_boot_run_custom(&cfg);
}

int anim_boot_run_custom(const anim_boot_config_t *cfg) {
    fb_context_t *fb = cfg->fb;
    int scale = (cfg->text_scale > 0) ? cfg->text_scale : 3;
    
    fb_clear(fb, 0, 0, 0);
    delay_ms(500);

    int cur_y = 100;
    for (int i = 0; i < BOOT_LINE_COUNT && BOOT_LINES[i] != NULL; i++) {
        draw_boot_line_with_blink(fb, 80, cur_y, BOOT_LINES[i], scale);
        cur_y += (8 * scale + 4);
        delay_ms(cfg->line_delay_ms);
    }

    delay_ms(300);
    anim_fly_appear(fb, cfg->hal, cfg->fly_image_path, cfg->vibrate_ms);
    return 0;
}
