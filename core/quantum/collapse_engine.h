#ifndef ANKA_COLLAPSE_ENGINE_H
#define ANKA_COLLAPSE_ENGINE_H

/*
 * collapse_engine.h — Çöküş Motoru API
 * =====================================
 * 🪰 [ÇÖKÜŞ]: Tetikleyici geldiğinde Kuantum Tozu'nu anlık olarak
 * çözer ve HAL katmanına donanım komutu gönderir.
 * Zero-latency hedeflenir — gecikme mikrosaniye cinsinden ölçülür.
 *
 * "Gözlemci etkisi": Doğru tetikleyici + anahtar → toz gerçeğe çöker.
 */

#include <stddef.h>
#include <stdint.h>
#include "quantum_dust.h"

/* ---- AnkaHAL İleri Bildirimi ------------------------------------------ */
/*
 * Gerçek HAL başlığı projeye göre dahil edilir.
 * Burada minimum arayüzü tanımlıyoruz — tam HAL entegrasyonu için
 * core/hal/anka_hal.h dosyasını dahil et.
 */
#ifndef ANKA_HAL_DEFINED
#define ANKA_HAL_DEFINED

typedef struct AnkaHAL {
    /* Donanım aksiyonları — her biri 0 başarı, -1 hata döndürür */
    int (*vibrate)(int duration_ms);                /* titreşim motoru      */
    int (*speak)(const char *text);                 /* TTS / hoparlör       */
    int (*capture_camera)(const char *out_path);    /* kamera yakalaması    */
    int (*set_brightness)(int level_0_255);         /* ekran parlaklığı     */
    int (*display_blit)(const uint8_t *buf,
                        int width, int height);     /* ham piksel yazma     */
    int (*get_light_level)(float *lux_out);         /* ortam ışığı          */
    int (*get_accel)(float *x, float *y, float *z); /* ivme ölçer          */
    void *priv;                                     /* HAL özel verisi      */
} AnkaHAL;

#endif /* ANKA_HAL_DEFINED */

/* ---- Tetikleyici Tipleri ----------------------------------------------- */
typedef enum {
    COLLAPSE_TRIGGER_SENSOR  = 1, /* sensör verisi geldi                   */
    COLLAPSE_TRIGGER_USER    = 2, /* kullanıcı komutu ("bilet bak" vb.)    */
    COLLAPSE_TRIGGER_KOVAN   = 3, /* Kovan ağından mesaj geldi             */
    COLLAPSE_TRIGGER_TIMER   = 4, /* periyodik tetik (nabız)               */
    COLLAPSE_TRIGGER_AMBIENT = 5, /* ortam değişimi (ışık, ses, titreşim)  */
    COLLAPSE_TRIGGER_MAX     = 6, /* sınır — geri callback dizisi için     */
} collapse_trigger_t;

/* ---- Aksiyon Tipleri --------------------------------------------------- */
typedef enum {
    COLLAPSE_ACT_VIBRATE  = 1,  /* titreşim (action_arg = ms)             */
    COLLAPSE_ACT_SPEAK    = 2,  /* TTS konuşma (action_text = metin)      */
    COLLAPSE_ACT_CAPTURE  = 3,  /* kamera yakala (action_text = yol)      */
    COLLAPSE_ACT_DISPLAY  = 4,  /* ekrana yaz (action_text = yol/veri)    */
    COLLAPSE_ACT_SYNC     = 5,  /* Kovan delta senkronizasyonu            */
    COLLAPSE_ACT_DORMANT  = 6,  /* 1Hz sinek moduna dön                   */
} collapse_action_t;

/* ---- Çöküş Kuralı ------------------------------------------------------ */
/*
 * Her kural: "bu tetikleyici gelirse, bu toz bloğunu çöz, bu aksiyonu yap"
 * dust_block_id = 0 → en uygun bloğu otomatik seç (tetikleyici tipine göre)
 */
typedef struct {
    collapse_trigger_t trigger;
    uint32_t           dust_block_id;   /* 0 = otomatik seç               */
    collapse_action_t  action;
    int                action_arg;      /* VIBRATE: ms, DISPLAY: level, vb.*/
    char               action_text[256];/* SPEAK metni, CAPTURE yolu, vb.  */
    int                active;          /* bu kural etkin mi?              */
} collapse_rule_t;

/* ---- Çöküş Geri Çağrısı ----------------------------------------------- */
/*
 * Tetikleyici sonrası isteğe bağlı callback.
 * plaintext: çözülen toz içeriği
 * len:       plaintext uzunluğu
 */
typedef void (*collapse_callback_t)(const collapse_rule_t *rule,
                                    const uint8_t         *plaintext,
                                    size_t                 len);

/* ---- İstatistik yapısı ------------------------------------------------- */
typedef struct {
    long     total_collapses;          /* toplam çöküş sayısı             */
    long     failed_collapses;         /* başarısız çöküş (tag mismatch)  */
    long     total_actions;            /* gönderilen HAL aksiyonu          */
    long     avg_latency_us;           /* ortalama gecikme (mikrosaniye)   */
    long     max_latency_us;           /* maksimum gecikme                 */
    uint32_t last_collapsed_id;        /* son çöken blok ID               */
} collapse_stats_t;

/* ---- Public API -------------------------------------------------------- */

/*
 * collapse_init — Çöküş motorunu başlat.
 * dust: başlatılmış toz deposu
 * hal:  başlatılmış HAL katmanı
 */
int  collapse_init(qd_store_t *dust, AnkaHAL *hal);

/*
 * collapse_register — Yeni çöküş kuralı kaydet.
 * Döndürür: kural indeksi (≥0) veya -1 (hata)
 */
int  collapse_register(collapse_trigger_t trigger,
                       collapse_action_t  action,
                       uint32_t           dust_id);

/*
 * collapse_register_ex — Genişletilmiş kural kaydı (arg ve metin ile).
 */
int  collapse_register_ex(collapse_trigger_t trigger,
                          collapse_action_t  action,
                          uint32_t           dust_id,
                          int                arg,
                          const char        *text);

/*
 * collapse_register_callback — Tetikleyici için callback kaydet.
 * Her tetikleyici için tek callback (üzerine yazılır).
 */
int  collapse_register_callback(collapse_trigger_t   trigger,
                                collapse_callback_t  cb);

/*
 * collapse_fire — Tetikleyiciyi ateşle (kullanıcı girişi ile).
 * user_input: isteğe bağlı kullanıcı metni (NULL olabilir)
 */
int  collapse_fire(collapse_trigger_t trigger,
                   const char        *user_input,
                   int                input_len);

/*
 * collapse_fire_sensor — Sensör verisiyle tetikle.
 */
int  collapse_fire_sensor(collapse_trigger_t trigger,
                          const uint8_t     *sensor_data,
                          size_t             len);

/*
 * collapse_instant — Kural aramasını atla, doğrudan çöküş + dispatch.
 * Ultra düşük gecikme yolu.
 */
int  collapse_instant(uint32_t          dust_id,
                      collapse_action_t action,
                      int               arg);

/*
 * collapse_loop — Olay döngüsü (epoll/poll tabanlı, engelleyen).
 * Bu döngü Sinek'in kalp atışıdır. Her tetikleyici bir çöküş doğurur.
 */
void collapse_loop(void);

/*
 * collapse_shutdown — Motoru durdur, olay döngüsünden çık.
 */
void collapse_shutdown(void);

/*
 * collapse_get_stats — İstatistikleri al (thread-safe, kopya döndürür).
 */
void collapse_get_stats(collapse_stats_t *out);

#endif /* ANKA_COLLAPSE_ENGINE_H */
