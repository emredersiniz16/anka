#ifndef ANKA_ANIM_ENGINE_H
#define ANKA_ANIM_ENGINE_H

/*
 * core/ui/anim_engine.h
 *
 * 🪰 [GÖLGE] Uyanış Animasyon Motoru & Canlı Dashboard Köprüsü
 *
 * Boot sekansı (görsel akış):
 *
 *   ┌─────────────────────────────────────────────────┐
 *   │  AŞAMA 1: SİYAH EKRAN                           │
 *   │    → Ekran saf siyaha boyandı (500ms bekle)      │
 *   ├─────────────────────────────────────────────────┤
 *   │  AŞAMA 2: TERMİNAL AKIŞI                        │
 *   │    → Yeşil (#00FF41) monospace metin             │
 *   │    → Her satır 250ms arayla kaydırıla gelir      │
 *   │    → "[OK] Anka_Core Init..."                    │
 *   │    → "[OK] Golge Katman Aktif"                   │
 *   │    → "[OK] Sinek Gozlerini Aciyor..."            │
 *   ├─────────────────────────────────────────────────┤
 *   │  AŞAMA 3: TEMİZLE                               │
 *   │    → Ekran siyaha döner (dramatik duraklama)     │
 *   ├─────────────────────────────────────────────────┤
 *   │  AŞAMA 4: SİNEK GÖRÜNDÜ                         │
 *   │    → BMP görüntü ekranın tam ortasına basılır    │
 *   ├─────────────────────────────────────────────────┤
 *   │  AŞAMA 5: DONANIM TETİĞİ                        │
 *   │    → current_hal->vibrate(400)  — güçlü titreşim│
 *   │    → audio_play_awakening()     — vızıltı + CLICK│
 *   │    → current_hal->speak("click")— mekanik ses    │
 *   └─────────────────────────────────────────────────┘
 *
 * Bootloop güvencesi:
 *   Bu bir userspace sürecidir. Çökersek Android kurtarır.
 *   surfaceflinger → ekranı geri alır → cihaz kullanılabilir.
 *   Kernel paniklemez. ADB erişilebilir kalır.
 */

#include <stdint.h>
#include "ui_engine.h"

/* HAL başlığını opsiyonel dahil et — test modunda HAL olmayabilir */
#ifndef ANKA_UI_TEST
#  include "../hal/anka_hal.h"
#else
/* Test modu: HAL tip taklidi */
typedef struct {
    void (*vibrate)(int ms);
    void (*speak)(const char *text);
} AnkaHAL;
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* ─── Boot animasyon konfigürasyonu ─── */
typedef struct {
    fb_context_t *fb;             /* Açık framebuffer bağlamı (zorunlu) */
    AnkaHAL      *hal;            /* HAL arayüzü (NULL ise yok sayılır) */
    int           text_scale;     /* Font ölçeği: 3 = 24×24px (1080p için önerilen) */
    int           line_delay_ms;  /* Satırlar arası gecikme (ms, varsayılan: 250) */
    int           post_delay_ms;  /* Terminal sonrası bekleme (ms, varsayılan: 1000) */
    int           vibrate_ms;     /* Uyanış titreşim süresi (ms, varsayılan: 400) */
    const char   *fly_image_path; /* Sinek BMP dosya yolu (varsayılan: "assets/fly_icon.bmp") */
} anim_boot_config_t;

/*
 * anim_boot_run: Varsayılan konfigürasyon ile tam boot sekansını çalıştır.
 *   - text_scale=3, line_delay_ms=250, post_delay_ms=1000, vibrate_ms=400
 *   - fly_image_path="assets/fly_icon.bmp"
 *
 * Dönüş: 0 başarı, -1 kritik hata.
 */
int anim_boot_run(fb_context_t *fb, AnkaHAL *hal);

/*
 * anim_boot_run_custom: Özelleştirilmiş konfigürasyon ile boot sekansını çalıştır.
 *   cfg->fb ve cfg->hal dışındaki alanlar sıfırsa varsayılanlar kullanılır.
 *
 * Dönüş: 0 başarı, -1 kritik hata (fb NULL veya geçersiz).
 */
int anim_boot_run_custom(const anim_boot_config_t *cfg);

/*
 * anim_terminal_scroll: Sadece terminal akışı — test ve debug için.
 *   Ekranı temizlemez, sinek basmaz, donanım tetiklemez.
 *   lines: NULL sonlu dize dizisi.
 *   count: satır sayısı (-1 = NULL'a kadar say).
 *   scale: font ölçeği.
 *   delay_ms: satırlar arası gecikme (ms).
 *
 * Dönüş: yazılan satır sayısı.
 */
int anim_terminal_scroll(fb_context_t *fb, const char *lines[], int count,
                         int scale, int delay_ms);

/*
 * anim_fly_appear: Sineği ekrana bas + donanım tetikle.
 *   BMP yoksa ASCII sinek çizilir (yedek).
 *   image_path: BMP dosya yolu.
 *   vibrate_ms: titreşim süresi.
 *
 * Dönüş: 0 başarı, -1 BMP yükleme hatası (yedek çizildi).
 */
int anim_fly_appear(fb_context_t *fb, AnkaHAL *hal, const char *image_path,
                    int vibrate_ms);

/*
 * anim_draw_ascii_fly: ASCII sinek çizimi (BMP yoksa yedek).
 *   cx, cy: sineğin çizileceği merkez koordinatı.
 *   scale: font ölçeği.
 */
void anim_draw_ascii_fly(fb_context_t *fb, int cx, int cy, int scale);

/* ─── Sinek Durum ve Canlı Dashboard Köprüsü ─── */
void anim_update_fly_state(fb_context_t *fb, int current_state, float scale);
void anim_render_live_dashboard(fb_context_t *fb, int current_state, int battery_level, const char *time_str, int quantum_dust, const char *last_log);

#ifdef __cplusplus
}
#endif

#endif /* ANKA_ANIM_ENGINE_H */
