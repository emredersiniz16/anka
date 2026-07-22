#ifndef ANKA_SINEK_FSM_H
#define ANKA_SINEK_FSM_H

/*
 * sinek_fsm.h — Sinek Yaşam Döngüsü Sonlu Durum Makinesi
 * ========================================================
 * 🪰 [SİNEK]: Sinek'in tüm durumları ve geçişleri burada tanımlanır.
 *
 * DORMANT   → 1Hz sinek modu: minimum CPU, ekran karartılmış
 * AWAKE     → HAL hazır, sensörler açık, toz store yüklü
 * OBSERVING → Sensör/kullanıcı dinleme, toz biriktirme
 * COLLAPSED → Toz çöküşü gerçekleşti, karar alındı
 * ACTING    → HAL aksiyonu gönderiliyor
 * SYNCING   → Kovan'a delta senkronizasyonu yapılıyor
 *
 * Geçiş tablosu veri odaklıdır — yeni geçiş eklemek için
 * sadece g_transitions[] dizisine satır ekle.
 */

#include <stddef.h>
#include <stdio.h>
#include "quantum_dust.h"
#include "collapse_engine.h"

/* ---- Durum Tanımları --------------------------------------------------- */
typedef enum {
    SINEK_DORMANT   = 0, /* uyku — 1Hz kalp atışı                         */
    SINEK_AWAKE     = 1, /* uyanık — HAL aktif                             */
    SINEK_OBSERVING = 2, /* gözlem — toz biriktirme                        */
    SINEK_COLLAPSED = 3, /* çöküş — karar alındı                          */
    SINEK_ACTING    = 4, /* aksiyon — HAL komutu gönderiliyor              */
    SINEK_SYNCING   = 5, /* senkronizasyon — Kovan'a delta gönderiliyor   */
    SINEK_STATE_MAX = 6, /* sınır değer                                    */
} sinek_state_t;

/* ---- Olay Tanımları ---------------------------------------------------- */
typedef enum {
    SINEK_EVT_SENSOR_DATA    =  1, /* sensör okuması geldi                */
    SINEK_EVT_USER_COMMAND   =  2, /* kullanıcı komutu ("bilet bak" vb.) */
    SINEK_EVT_KOVAN_MSG      =  3, /* Kovan ağından mesaj                 */
    SINEK_EVT_TIMER          =  4, /* periyodik nabız tetikleyicisi       */
    SINEK_EVT_AMBIENT_CHANGE =  5, /* ortam değişimi (ışık, ses, titreşim)*/
    SINEK_EVT_ACTION_DONE    =  6, /* HAL aksiyonu tamamlandı             */
    SINEK_EVT_SYNC_DONE      =  7, /* Kovan sync tamamlandı               */
    SINEK_EVT_OFFLINE        =  8, /* Kovan bağlantısı koptu              */
    SINEK_EVT_ONLINE         =  9, /* Kovan bağlantısı geldi              */
    SINEK_EVT_SLEEP          = 10, /* 1Hz moduna geç                      */
    SINEK_EVT_WAKE           = 11, /* 1Hz'den uyan                        */
    SINEK_EVT_MAX            = 12, /* sınır değer                         */
} sinek_event_t;

/* ---- FSM Ana Yapısı ---------------------------------------------------- */
typedef struct {
    sinek_state_t    state;           /* geçerli durum                    */
    qd_store_t      *dust;            /* toz deposu referansı             */
    AnkaHAL         *hal;             /* HAL katmanı referansı            */
    int              kovan_online;    /* 1 = Kovan bağlı, 0 = çevrimdışı */
    int              actions_count;   /* toplam HAL aksiyonu sayısı       */
    int              collapses_count; /* toplam çöküş sayısı              */
    long             uptime_ms;       /* başlangıçtan bu yana milisaniye  */
    struct timespec  start_time;      /* başlangıç zamanı                 */
    pthread_mutex_t  lock;            /* FSM iş parçacığı güvenliği       */
} sinek_fsm_t;

/* ---- Public API -------------------------------------------------------- */

/*
 * sinek_fsm_init — FSM'yi başlat, başlangıç durumu DORMANT.
 */
int sinek_fsm_init(sinek_fsm_t *fsm, qd_store_t *dust, AnkaHAL *hal);

/*
 * sinek_fsm_handle_event — Olayı işle, geçiş tablosuna bak, geç.
 * Geçerli geçiş bulunamazsa: uyarı log → ama ÇÖKMEZ.
 * Döndürür: 0 başarı, -1 geçersiz geçiş
 */
int sinek_fsm_handle_event(sinek_fsm_t   *fsm,
                           sinek_event_t  evt,
                           const void    *data,
                           size_t         data_len);

/*
 * sinek_fsm_get_state — Geçerli durumu döndür (thread-safe).
 */
sinek_state_t sinek_fsm_get_state(sinek_fsm_t *fsm);

/*
 * sinek_state_name — Durum adını insan-okunur Türkçe string olarak döndür.
 */
const char *sinek_state_name(sinek_state_t s);

/*
 * sinek_event_name — Olay adını insan-okunur Türkçe string olarak döndür.
 */
const char *sinek_event_name(sinek_event_t e);

/*
 * sinek_fsm_print_status — Mevcut FSM durumunu formatlanmış çıktı.
 */
void sinek_fsm_print_status(sinek_fsm_t *fsm, FILE *out);

/*
 * sinek_fsm_uptime_update — Uptime'ı güncelle (periyodik çağrı).
 */
void sinek_fsm_uptime_update(sinek_fsm_t *fsm);

/*
 * sinek_fsm_destroy — FSM'yi temizle.
 */
void sinek_fsm_destroy(sinek_fsm_t *fsm);

#endif /* ANKA_SINEK_FSM_H */
