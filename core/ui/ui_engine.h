#ifndef ANKA_UI_ENGINE_H
#define ANKA_UI_ENGINE_H

/*
 * core/engines/ui_engine.h
 *
 * 🪰 [GÖLGE] Gölge Katman — Framebuffer UI Motoru
 *
 * Android'in surfaceflinger'ını öldürmeden, doğrudan /dev/graphics/fb0'a
 * mmap ile yazar. Çökersek surfaceflinger ekranı geri alır → bootloop YOK.
 *
 * "Gölge" çünkü: surfaceflinger hâlâ çalışır, ama biz onun üstüne yazarız.
 * O yeniden çizerse biz tekrar yazarız. Sonunda biz kazanırız (daha hızlıyız).
 *
 * ÖNEMLİ GÜVENLİK NOTU:
 *   Bu bir userspace sürecidir. Çökersek kernel paniklemez.
 *   surfaceflinger ekranı geri alır → cihaz kullanılabilir kalır → BOOTLOOP YOK.
 *   Magisk root gerekir: `su -c ./anka_os` ile çalıştırılmalı.
 *
 * Hedef donanım: Redmi Note 9 (1080×2340, SDM660, 32bpp RGBA8888)
 * Çalışma ortamı: Termux + Magisk root
 */

#include <stdint.h>
#include <linux/fb.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ─── Framebuffer bağlamı ─── */
typedef struct {
    int      fd;           /* /dev/graphics/fb0 veya /dev/fb0 dosya tanımlayıcısı */
    uint8_t *map;          /* mmap'd framebuffer belleği — doğrudan ekran VRAM */
    uint32_t width;        /* ekran genişliği (piksel) */
    uint32_t height;       /* ekran yüksekliği (piksel) */
    uint32_t bpp;          /* bit/piksel: 16 (RGB565) veya 32 (RGBA8888) */
    uint32_t stride;       /* satır başına bayt (fb_fix_screeninfo.line_length) */
    uint32_t smem_len;     /* toplam framebuffer boyutu (bayt) */
    int      shadow_mode;  /* 1 = gölge (surfaceflinger canlı), 0 = tam devralma */

    /* Piksel sırası algılama (farklı cihazlarda BGR/RGB karışıklığı için) */
    uint32_t red_offset;   /* kırmızı kanalın bit ofseti */
    uint32_t green_offset; /* yeşil kanalın bit ofseti */
    uint32_t blue_offset;  /* mavi kanalın bit ofseti */

    /* Ham IOCTL sonuçları — hata ayıklama için saklanır */
    struct fb_var_screeninfo vinfo;
    struct fb_fix_screeninfo finfo;
} fb_context_t;

/* ─── Framebuffer yaşam döngüsü ─── */
int  fb_open(fb_context_t *fb);
void fb_close(fb_context_t *fb);

/* ─── Piksel ilkel işlemleri ─── */
void fb_put_pixel(fb_context_t *fb, int x, int y, uint8_t r, uint8_t g, uint8_t b);
void fb_fill_rect(fb_context_t *fb, int x, int y, int w, int h, uint8_t r, uint8_t g, uint8_t b);
void fb_clear(fb_context_t *fb, uint8_t r, uint8_t g, uint8_t b);

/* ─── Metin çizimi — 8×8 bitmap font ─── */
void fb_draw_text(fb_context_t *fb, int x, int y, const char *text, uint8_t r, uint8_t g, uint8_t b);
void fb_draw_text_scaled(fb_context_t *fb, int x, int y, const char *text, int scale, uint8_t r, uint8_t g, uint8_t b);

/* ─── BMP görüntü yükleyici ─── */
int  fb_load_bmp(fb_context_t *fb, const char *path, int x, int y);
int  fb_load_bmp_centered(fb_context_t *fb, const char *path);

/* ─── Terminal efekti ─── */
void fb_scroll_up(fb_context_t *fb, int pixels);

/* ─── Ekran devralma (isteğe bağlı, su gerektirir) ─── */
int  fb_takeover_stop_surfaceflinger(void);
int  fb_takeover_start_surfaceflinger(void);

/* ─── Anka OS Özel Arayüz Fonksiyonları ─── */
void anka_boot_sequence(fb_context_t *fb);
void ui_render(fb_context_t *fb, const char *last_message);
void ui_render_dashboard(fb_context_t *fb, 
                         int battery_level, 
                         const char *time_str, 
                         int quantum_dust, 
                         const char *current_mood, 
                         const char *last_log);

/* Unresolved External Stub / Evrim Onayı */
int user_confirmed_evolution(void);

#ifdef __cplusplus
}
#endif

#endif /* ANKA_UI_ENGINE_H */
