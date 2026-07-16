/*
 * sinek_fsm.c — Sinek Yaşam Döngüsü FSM Uygulaması
 * ===================================================
 * 🪰 [SİNEK]: Veri odaklı geçiş tablosu. Yeni geçiş eklemek için
 * sadece g_transitions[] dizisine bir satır ekle — kod değişmez.
 *
 * Her handler:
 *   - Gerekli aksiyonu gerçekleştirir
 *   - Loglar
 *   - 0 (başarı) veya -1 (hata) döndürür
 */

#include "sinek_fsm.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <pthread.h>

/* =========================================================================
 * İleri bildirimler — handler fonksiyonları
 * ========================================================================= */
static int h_wake_up          (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_go_dormant       (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_start_observing  (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_collect_dust     (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_collapse         (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_execute_action   (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_start_sync       (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_resume_observing (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_offline_fallback (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_heartbeat        (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_reconsider       (sinek_fsm_t *fsm, const void *data, size_t len);
static int h_go_online        (sinek_fsm_t *fsm, const void *data, size_t len);

/* =========================================================================
 * Geçiş Tablosu — FSM'nin kalbi
 * =========================================================================
 * 🪰 [SİNEK]: Bu tablo Sinek'in tüm davranışını tanımlar.
 * Her satır: (kaynak_durum, olay) → (hedef_durum, handler)
 *
 * Yeni davranış eklemek: sadece buraya satır ekle.
 */
static const struct {
    sinek_state_t  from;
    sinek_event_t  event;
    sinek_state_t  to;
    int (*handler)(sinek_fsm_t *fsm, const void *data, size_t len);
} g_transitions[] = {

    /* ---- DORMANT -------------------------------------------------------- */
    { SINEK_DORMANT,   SINEK_EVT_SENSOR_DATA,    SINEK_AWAKE,      h_wake_up         },
    { SINEK_DORMANT,   SINEK_EVT_USER_COMMAND,   SINEK_AWAKE,      h_wake_up         },
    { SINEK_DORMANT,   SINEK_EVT_KOVAN_MSG,      SINEK_AWAKE,      h_wake_up         },
    { SINEK_DORMANT,   SINEK_EVT_WAKE,           SINEK_AWAKE,      h_wake_up         },
    { SINEK_DORMANT,   SINEK_EVT_ONLINE,         SINEK_AWAKE,      h_go_online       },
    { SINEK_DORMANT,   SINEK_EVT_TIMER,          SINEK_DORMANT,    h_heartbeat       }, /* 1Hz nabız */
    { SINEK_DORMANT,   SINEK_EVT_OFFLINE,        SINEK_DORMANT,    h_offline_fallback},

    /* ---- AWAKE ---------------------------------------------------------- */
    { SINEK_AWAKE,     SINEK_EVT_USER_COMMAND,   SINEK_OBSERVING,  h_start_observing },
    { SINEK_AWAKE,     SINEK_EVT_SENSOR_DATA,    SINEK_OBSERVING,  h_start_observing },
    { SINEK_AWAKE,     SINEK_EVT_KOVAN_MSG,      SINEK_OBSERVING,  h_start_observing },
    { SINEK_AWAKE,     SINEK_EVT_AMBIENT_CHANGE, SINEK_OBSERVING,  h_start_observing },
    { SINEK_AWAKE,     SINEK_EVT_SLEEP,          SINEK_DORMANT,    h_go_dormant      },
    { SINEK_AWAKE,     SINEK_EVT_OFFLINE,        SINEK_AWAKE,      h_offline_fallback},
    { SINEK_AWAKE,     SINEK_EVT_ONLINE,         SINEK_AWAKE,      h_go_online       },
    { SINEK_AWAKE,     SINEK_EVT_TIMER,          SINEK_AWAKE,      h_heartbeat       },

    /* ---- OBSERVING ------------------------------------------------------ */
    { SINEK_OBSERVING, SINEK_EVT_USER_COMMAND,   SINEK_COLLAPSED,  h_collapse        },
    { SINEK_OBSERVING, SINEK_EVT_SENSOR_DATA,    SINEK_OBSERVING,  h_collect_dust    }, /* toz biriktir */
    { SINEK_OBSERVING, SINEK_EVT_AMBIENT_CHANGE, SINEK_COLLAPSED,  h_collapse        },
    { SINEK_OBSERVING, SINEK_EVT_KOVAN_MSG,      SINEK_COLLAPSED,  h_collapse        },
    { SINEK_OBSERVING, SINEK_EVT_SLEEP,          SINEK_DORMANT,    h_go_dormant      },
    { SINEK_OBSERVING, SINEK_EVT_OFFLINE,        SINEK_OBSERVING,  h_offline_fallback},
    { SINEK_OBSERVING, SINEK_EVT_ONLINE,         SINEK_OBSERVING,  h_go_online       },
    { SINEK_OBSERVING, SINEK_EVT_TIMER,          SINEK_OBSERVING,  h_heartbeat       },

    /* ---- COLLAPSED ------------------------------------------------------ */
    { SINEK_COLLAPSED, SINEK_EVT_ACTION_DONE,    SINEK_ACTING,     h_execute_action  },
    { SINEK_COLLAPSED, SINEK_EVT_KOVAN_MSG,      SINEK_COLLAPSED,  h_reconsider      }, /* yeni bilgi */
    { SINEK_COLLAPSED, SINEK_EVT_SLEEP,          SINEK_DORMANT,    h_go_dormant      },
    { SINEK_COLLAPSED, SINEK_EVT_OFFLINE,        SINEK_ACTING,     h_execute_action  }, /* offline da aksiyon al */

    /* ---- ACTING --------------------------------------------------------- */
    { SINEK_ACTING,    SINEK_EVT_ACTION_DONE,    SINEK_SYNCING,    h_start_sync      },
    { SINEK_ACTING,    SINEK_EVT_OFFLINE,        SINEK_OBSERVING,  h_offline_fallback}, /* Kovan yok, yerel devam */
    { SINEK_ACTING,    SINEK_EVT_SLEEP,          SINEK_DORMANT,    h_go_dormant      },
    { SINEK_ACTING,    SINEK_EVT_TIMER,          SINEK_ACTING,     h_heartbeat       },

    /* ---- SYNCING -------------------------------------------------------- */
    { SINEK_SYNCING,   SINEK_EVT_SYNC_DONE,      SINEK_OBSERVING,  h_resume_observing},
    { SINEK_SYNCING,   SINEK_EVT_OFFLINE,        SINEK_DORMANT,    h_go_dormant      }, /* sync başarısız, uyu */
    { SINEK_SYNCING,   SINEK_EVT_TIMER,          SINEK_SYNCING,    h_heartbeat       },
    { SINEK_SYNCING,   SINEK_EVT_SLEEP,          SINEK_DORMANT,    h_go_dormant      },
};

static const int G_TRANSITION_COUNT =
    (int)(sizeof(g_transitions) / sizeof(g_transitions[0]));

/* =========================================================================
 * Durum ve olay adları
 * ========================================================================= */
const char *sinek_state_name(sinek_state_t s)
{
    switch (s) {
        case SINEK_DORMANT:   return "DORMANT (1Hz Uyku)";
        case SINEK_AWAKE:     return "AWAKE (Uyanık)";
        case SINEK_OBSERVING: return "OBSERVING (Gözlem)";
        case SINEK_COLLAPSED: return "COLLAPSED (Çöküş)";
        case SINEK_ACTING:    return "ACTING (Aksiyon)";
        case SINEK_SYNCING:   return "SYNCING (Senkron)";
        default:              return "BILINMIYOR";
    }
}

const char *sinek_event_name(sinek_event_t e)
{
    switch (e) {
        case SINEK_EVT_SENSOR_DATA:    return "SENSOR_DATA";
        case SINEK_EVT_USER_COMMAND:   return "USER_COMMAND";
        case SINEK_EVT_KOVAN_MSG:      return "KOVAN_MSG";
        case SINEK_EVT_TIMER:          return "TIMER";
        case SINEK_EVT_AMBIENT_CHANGE: return "AMBIENT_CHANGE";
        case SINEK_EVT_ACTION_DONE:    return "ACTION_DONE";
        case SINEK_EVT_SYNC_DONE:      return "SYNC_DONE";
        case SINEK_EVT_OFFLINE:        return "OFFLINE";
        case SINEK_EVT_ONLINE:         return "ONLINE";
        case SINEK_EVT_SLEEP:          return "SLEEP";
        case SINEK_EVT_WAKE:           return "WAKE";
        default:                       return "BILINMIYOR";
    }
}

/* =========================================================================
 * Handler Fonksiyonları
 * ========================================================================= */

static int h_wake_up(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: Uyanış... */
    fprintf(stderr,
            "🪰 [SİNEK]: Uyanış... HAL aktif hale getiriliyor\n");
    if (fsm->hal && fsm->hal->set_brightness)
        fsm->hal->set_brightness(128); /* orta parlaklık */
    return 0;
}

static int h_go_dormant(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: 1Hz moduna geçiş... */
    fprintf(stderr,
            "🪰 [SİNEK]: 1Hz moduna geçiş... ekran karartılıyor\n");
    if (fsm->hal && fsm->hal->set_brightness)
        fsm->hal->set_brightness(0);
    return 0;
}

static int h_start_observing(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)fsm;
    /* 🪰 [SİNEK]: Gözlem başladı */
    fprintf(stderr,
            "🪰 [SİNEK]: Gözlem başladı — sensörler dinleniyor "
            "(veri=%zu byte)\n", len);
    if (data && len > 0 && fsm->dust) {
        /* Gelen veriyi hemen toz olarak mühürle */
        uint32_t dust_id = 0;
        qd_seal(fsm->dust, QD_TYPE_SENSOR_DATA,
                (const uint8_t *)data, len, &dust_id);
        fprintf(stderr,
                "🪰 [SİNEK]: İlk toz mühürlendi (id=%u)\n", dust_id);
    }
    return 0;
}

static int h_collect_dust(sinek_fsm_t *fsm, const void *data, size_t len)
{
    /* 🪰 [SİNEK]: Toz biriktirme — sensör verisi toz'a dönüşüyor */
    if (!data || len == 0 || !fsm->dust) return 0;

    uint32_t dust_id = 0;
    int rc = qd_seal(fsm->dust, QD_TYPE_SENSOR_DATA,
                     (const uint8_t *)data, len, &dust_id);
    if (rc == QD_OK) {
        int total = qd_count_by_type(fsm->dust, QD_TYPE_SENSOR_DATA);
        fprintf(stderr,
                "🪰 [SİNEK]: Toz +1 (id=%u, sensör tozu=%d blok)\n",
                dust_id, total);
    }
    return rc;
}

static int h_collapse(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: Çöküş tetiklendi — toz anlam kazanıyor */
    fprintf(stderr,
            "🪰 [SİNEK]: Çöküş tetiklendi (çöküş #%d)\n",
            fsm->collapses_count + 1);

    int rc = collapse_fire(COLLAPSE_TRIGGER_USER, (const char *)data,
                           (int)len);
    fsm->collapses_count++;

    /* Çöküş tamamlandıktan sonra ACTION_DONE olayını otomatik üret */
    /* (gerçek sistemde HAL callback'i tetikler) */
    return rc;
}

static int h_execute_action(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: Aksiyon yürütülüyor */
    fprintf(stderr,
            "🪰 [SİNEK]: HAL aksiyonu yürütülüyor (aksiyon #%d)\n",
            fsm->actions_count + 1);
    fsm->actions_count++;
    return 0;
}

static int h_start_sync(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: Kovan senkronizasyonu başlatılıyor */
    if (!fsm->kovan_online) {
        fprintf(stderr,
                "⚠️  [SİNEK]: Kovan çevrimdışı — sync atlandı\n");
        return -1;
    }
    fprintf(stderr,
            "🪰 [SİNEK]: Kovan delta sync başlatıldı "
            "(toz=%zu byte)\n",
            qd_total_noise_bytes(fsm->dust));

    /* Python kovan_sync.py'ye SIGUSR1 → delta sync başlat */
    /* kill(kovan_sync_pid, SIGUSR1);  -- PID dosyasından oku */
    return 0;
}

static int h_resume_observing(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)fsm; (void)data; (void)len;
    /* 🪰 [SİNEK]: Sync tamamlandı, gözleme dönülüyor */
    fprintf(stderr,
            "🪰 [SİNEK]: Kovan sync tamam — gözleme dönülüyor\n");
    return 0;
}

static int h_offline_fallback(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* ⚠️  [SİNEK]: Kovan yok, yerel mod devam */
    fsm->kovan_online = 0;
    fprintf(stderr,
            "⚠️  [SİNEK]: Kovan yok, yerel mod devam — "
            "toz yerel'de birikmeye devam ediyor\n");
    return 0;
}

static int h_heartbeat(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: 1Hz nabız — DORMANT durumunda minimal işlem */
    sinek_fsm_uptime_update(fsm);
    size_t noise = fsm->dust ? qd_total_noise_bytes(fsm->dust) : 0;
    fprintf(stderr,
            "🪰 [SİNEK]: ♥ Nabız | durum=%-20s | "
            "toz=%zu byte | uptime=%ld s\n",
            sinek_state_name(fsm->state),
            noise,
            fsm->uptime_ms / 1000);
    return 0;
}

static int h_reconsider(sinek_fsm_t *fsm, const void *data, size_t len)
{
    /* 🪰 [SİNEK]: Çöküş sırasında yeni bilgi geldi — yeniden çökert */
    fprintf(stderr,
            "🪰 [SİNEK]: Yeniden değerlendirme — "
            "Kovan'dan yeni toz geldi (%zu byte)\n", len);

    if (data && len > 0 && fsm->dust) {
        uint32_t dust_id = 0;
        qd_seal(fsm->dust, QD_TYPE_KOVAN_STATE,
                (const uint8_t *)data, len, &dust_id);
    }
    /* Yeni toz ile çöküşü tekrarla */
    return h_collapse(fsm, data, len);
}

static int h_go_online(sinek_fsm_t *fsm, const void *data, size_t len)
{
    (void)data; (void)len;
    /* 🪰 [SİNEK]: Kovan bağlantısı kuruldu */
    fsm->kovan_online = 1;
    fprintf(stderr,
            "🪰 [SİNEK]: Kovan bağlantısı kuruldu — "
            "senkronizasyon mümkün\n");
    return 0;
}

/* =========================================================================
 * Public API: sinek_fsm_init
 * ========================================================================= */
int sinek_fsm_init(sinek_fsm_t *fsm, qd_store_t *dust, AnkaHAL *hal)
{
    if (!fsm || !dust || !hal) return -1;

    memset(fsm, 0, sizeof(sinek_fsm_t));
    fsm->state         = SINEK_DORMANT;
    fsm->dust          = dust;
    fsm->hal           = hal;
    fsm->kovan_online  = 0;
    fsm->actions_count = 0;
    fsm->collapses_count = 0;
    fsm->uptime_ms     = 0;

    clock_gettime(CLOCK_MONOTONIC, &fsm->start_time);
    pthread_mutex_init(&fsm->lock, NULL);

    fprintf(stderr,
            "🪰 [SİNEK]: FSM başlatıldı — başlangıç durumu: %s\n"
            "   Geçiş tablosu: %d kural yüklendi\n",
            sinek_state_name(fsm->state), G_TRANSITION_COUNT);
    return 0;
}

/* =========================================================================
 * Public API: sinek_fsm_handle_event
 * ========================================================================= */
int sinek_fsm_handle_event(sinek_fsm_t   *fsm,
                           sinek_event_t  evt,
                           const void    *data,
                           size_t         data_len)
{
    if (!fsm) return -1;

    pthread_mutex_lock(&fsm->lock);

    sinek_state_t current = fsm->state;
    int found = 0;
    int handler_rc = 0;

    /* Geçiş tablosunu tara */
    for (int i = 0; i < G_TRANSITION_COUNT; i++) {
        if (g_transitions[i].from  == current &&
            g_transitions[i].event == evt) {

            sinek_state_t next = g_transitions[i].to;

            fprintf(stderr,
                    "🪰 [SİNEK]: Geçiş: %s + %s → %s\n",
                    sinek_state_name(current),
                    sinek_event_name(evt),
                    sinek_state_name(next));

            /* Handler çağrısı — mutex tutulurken, dikkatli ol */
            if (g_transitions[i].handler) {
                pthread_mutex_unlock(&fsm->lock);
                handler_rc = g_transitions[i].handler(fsm, data, data_len);
                pthread_mutex_lock(&fsm->lock);
            }

            fsm->state = next;
            found = 1;
            break;
        }
    }

    if (!found) {
        /* Geçersiz geçiş — uyarı ver ama çökme */
        fprintf(stderr,
                "⚠️  [SİNEK]: Geçersiz geçiş (durum=%s, olay=%s) — "
                "yoksayıldı\n",
                sinek_state_name(current), sinek_event_name(evt));
        pthread_mutex_unlock(&fsm->lock);
        return -1;
    }

    pthread_mutex_unlock(&fsm->lock);
    return handler_rc;
}

/* =========================================================================
 * Public API: sinek_fsm_get_state
 * ========================================================================= */
sinek_state_t sinek_fsm_get_state(sinek_fsm_t *fsm)
{
    if (!fsm) return SINEK_DORMANT;
    pthread_mutex_lock(&fsm->lock);
    sinek_state_t s = fsm->state;
    pthread_mutex_unlock(&fsm->lock);
    return s;
}

/* =========================================================================
 * Public API: sinek_fsm_uptime_update
 * ========================================================================= */
void sinek_fsm_uptime_update(sinek_fsm_t *fsm)
{
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    long sec_diff  = now.tv_sec  - fsm->start_time.tv_sec;
    long nsec_diff = now.tv_nsec - fsm->start_time.tv_nsec;
    fsm->uptime_ms = sec_diff * 1000L + nsec_diff / 1000000L;
}

/* =========================================================================
 * Public API: sinek_fsm_print_status
 * ========================================================================= */
void sinek_fsm_print_status(sinek_fsm_t *fsm, FILE *out)
{
    if (!fsm || !out) return;

    pthread_mutex_lock(&fsm->lock);
    sinek_fsm_uptime_update(fsm);

    size_t noise_bytes  = fsm->dust ? qd_total_noise_bytes(fsm->dust) : 0;
    int    block_count  = fsm->dust ? fsm->dust->block_count : 0;
    long   uptime_sec   = fsm->uptime_ms / 1000;

    fprintf(out,
            "\n🪰 [SİNEK DURUM] ═══════════════════════════════\n"
            "   Durum    : %s\n"
            "   Toz      : %d blok (%zu byte gürültü)\n"
            "   Çöküş    : %d kez\n"
            "   Aksiyon  : %d kez\n"
            "   Kovan    : %s\n"
            "   Uptime   : %ld saniye\n"
            "🪰 ═════════════════════════════════════════════\n\n",
            sinek_state_name(fsm->state),
            block_count, noise_bytes,
            fsm->collapses_count,
            fsm->actions_count,
            fsm->kovan_online ? "ÇEVRİMİÇİ 🟢" : "ÇEVRİMDIŞI 🔴",
            uptime_sec);

    pthread_mutex_unlock(&fsm->lock);
}

/* =========================================================================
 * Public API: sinek_fsm_destroy
 * ========================================================================= */
void sinek_fsm_destroy(sinek_fsm_t *fsm)
{
    if (!fsm) return;
    pthread_mutex_destroy(&fsm->lock);
    fprintf(stderr, "🪰 [SİNEK]: FSM yok edildi\n");
}
