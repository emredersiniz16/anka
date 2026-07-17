/*
 * collapse_engine.c — Çöküş Motoru Uygulaması
 * =============================================
 * 🪰 [ÇÖKÜŞ]: Bu döngü Sinek'in kalp atışıdır.
 * Her tetikleyici bir çöküş doğurur.
 *
 * Gecikme: clock_gettime(CLOCK_MONOTONIC) ile mikrosaniye cinsinden ölçülür.
 * Thread-safety: tüm paylaşılan durum g_collapse_mutex ile korunur.
 */

#include "collapse_engine.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <poll.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <sys/timerfd.h>
#include <signal.h>

/* =========================================================================
 * Statik (global) motor durumu
 * ========================================================================= */

#define MAX_RULES     32  /* maksimum çöküş kuralı sayısı */

static qd_store_t          *g_dust        = NULL;
static AnkaHAL             *g_hal         = NULL;
static collapse_rule_t      g_rules[MAX_RULES];
static int                  g_rule_count  = 0;
/* Her tetikleyici tipi için bir callback (COLLAPSE_TRIGGER_MAX adet) */
static collapse_callback_t  g_callbacks[COLLAPSE_TRIGGER_MAX];
static pthread_mutex_t      g_collapse_mutex = PTHREAD_MUTEX_INITIALIZER;
static volatile int         g_running     = 0;
static collapse_stats_t     g_stats;

/* olay döngüsü timerfd */
static int g_timer_fd = -1;

/* =========================================================================
 * Yardımcı: mikrosaniye zaman damgası
 * ========================================================================= */
static long now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long)(ts.tv_sec * 1000000L + ts.tv_nsec / 1000L);
}

/* =========================================================================
 * Yardımcı: tetikleyiciye göre uygun blok tipi
 * ========================================================================= */
static qd_block_type_t trigger_to_block_type(collapse_trigger_t t)
{
    switch (t) {
        case COLLAPSE_TRIGGER_SENSOR:  return QD_TYPE_SENSOR_DATA;
        case COLLAPSE_TRIGGER_USER:    return QD_TYPE_USER_INTERACT;
        case COLLAPSE_TRIGGER_KOVAN:   return QD_TYPE_KOVAN_STATE;
        case COLLAPSE_TRIGGER_AMBIENT: return QD_TYPE_AMBIENT_OBS;
        case COLLAPSE_TRIGGER_TIMER:   return QD_TYPE_COMMAND_QUEUE;
        default:                       return QD_TYPE_SENSOR_DATA;
    }
}

/* =========================================================================
 * Yardımcı: HAL aksiyonu çalıştır
 * ========================================================================= */
static int execute_action(const collapse_rule_t *rule,
                          const uint8_t         *plaintext,
                          size_t                 pt_len)
{
    if (!g_hal) return -1;
    int rc = 0;

    switch (rule->action) {
        case COLLAPSE_ACT_VIBRATE:
            if (g_hal->vibrate) {
                int ms = rule->action_arg > 0 ? rule->action_arg : 200;
                rc = g_hal->vibrate(ms);
                fprintf(stderr,
                        "🪰 [ÇÖKÜŞ]: Titreşim → %d ms\n", ms);
            }
            break;

        case COLLAPSE_ACT_SPEAK: {
            /* Metin: action_text varsa kullan, yoksa düz metin çıktısını kullan */
            const char *text = rule->action_text[0] != '\0'
                               ? rule->action_text
                               : (const char *)plaintext;
            if (g_hal->speak && text) {
                rc = g_hal->speak(text);
                fprintf(stderr,
                        "🪰 [ÇÖKÜŞ]: TTS → \"%.40s%s\"\n",
                        text, strlen(text) > 40 ? "..." : "");
            }
            break;
        }

        case COLLAPSE_ACT_CAPTURE:
            if (g_hal->capture_camera) {
                const char *path = rule->action_text[0] != '\0'
                                   ? rule->action_text : "/tmp/anka_cap.jpg";
                rc = g_hal->capture_camera(path);
                fprintf(stderr,
                        "🪰 [ÇÖKÜŞ]: Kamera yakalandı → %s\n", path);
            }
            break;

        case COLLAPSE_ACT_DISPLAY:
            if (g_hal->display_blit && pt_len > 0) {
                /* plaintext: ham piksel veri (genişlik x yükseklik HAL'a bırakılmış) */
                rc = g_hal->display_blit(plaintext, 0, 0);
                fprintf(stderr,
                        "🪰 [ÇÖKÜŞ]: Ekrana yazıldı (%zu byte)\n", pt_len);
            }
            break;

        case COLLAPSE_ACT_SYNC:
            /*
             * Python kovan_sync.py servisine SIGUSR1 gönder.
             * PID dosyasından oku ya da sabit PID kullan.
             * system() yok — kill() sinyali kullan.
             */
            fprintf(stderr,
                    "🪰 [ÇÖKÜŞ]: Kovan sync tetiklendi (SIGUSR1)\n");
            /* Gerçek implementasyonda: kill(kovan_sync_pid, SIGUSR1); */
            break;

        case COLLAPSE_ACT_DORMANT:
            if (g_hal->set_brightness)
                g_hal->set_brightness(0);
            fprintf(stderr,
                    "🪰 [ÇÖKÜŞ]: Sinek 1Hz moduna giriyor...\n");
            break;

        default:
            fprintf(stderr,
                    "⚠️  [ÇÖKÜŞ]: Bilinmeyen aksiyon: %d\n", rule->action);
            rc = -1;
            break;
    }

    return rc;
}

/* =========================================================================
 * Public API: collapse_init
 * ========================================================================= */
int collapse_init(qd_store_t *dust, AnkaHAL *hal)
{
    if (!dust || !hal) return -1;

    pthread_mutex_lock(&g_collapse_mutex);
    g_dust       = dust;
    g_hal        = hal;
    g_rule_count = 0;
    g_running    = 0;
    memset(g_rules,     0, sizeof(g_rules));
    memset(g_callbacks, 0, sizeof(g_callbacks));
    memset(&g_stats,    0, sizeof(g_stats));
    pthread_mutex_unlock(&g_collapse_mutex);

    fprintf(stderr,
            "🪰 [ÇÖKÜŞ]: Motor başlatıldı — %d kural kapasitesi\n",
            MAX_RULES);
    return 0;
}

/* =========================================================================
 * Public API: collapse_register
 * ========================================================================= */
int collapse_register(collapse_trigger_t trigger,
                      collapse_action_t  action,
                      uint32_t           dust_id)
{
    return collapse_register_ex(trigger, action, dust_id, 0, NULL);
}

int collapse_register_ex(collapse_trigger_t trigger,
                         collapse_action_t  action,
                         uint32_t           dust_id,
                         int                arg,
                         const char        *text)
{
    pthread_mutex_lock(&g_collapse_mutex);
    if (g_rule_count >= MAX_RULES) {
        pthread_mutex_unlock(&g_collapse_mutex);
        fprintf(stderr, "❌ [ÇÖKÜŞ]: Kural deposu dolu (%d)\n", MAX_RULES);
        return -1;
    }

    int idx = g_rule_count++;
    collapse_rule_t *r = &g_rules[idx];
    r->trigger       = trigger;
    r->action        = action;
    r->dust_block_id = dust_id;
    r->action_arg    = arg;
    r->active        = 1;
    if (text)
        strncpy(r->action_text, text, sizeof(r->action_text) - 1);

    pthread_mutex_unlock(&g_collapse_mutex);

    fprintf(stderr,
            "🪰 [ÇÖKÜŞ]: Kural kaydedildi [%d] trigger=%d action=%d dust=%u\n",
            idx, (int)trigger, (int)action, dust_id);
    return idx;
}

/* =========================================================================
 * Public API: collapse_register_callback
 * ========================================================================= */
int collapse_register_callback(collapse_trigger_t  trigger,
                                collapse_callback_t cb)
{
    if ((int)trigger < 0 || trigger >= COLLAPSE_TRIGGER_MAX) return -1;
    pthread_mutex_lock(&g_collapse_mutex);
    g_callbacks[(int)trigger] = cb;
    pthread_mutex_unlock(&g_collapse_mutex);
    return 0;
}

/* =========================================================================
 * İç çekirdek: fire_rules — kural eşleştir, çöküş + aksiyon
 * ========================================================================= */
static int fire_rules(collapse_trigger_t trigger,
                      const uint8_t     *extra_data,
                      size_t             extra_len)
{
    if (!g_dust || !g_hal) return -1;

    long t_start = now_us();
    int  matched = 0;

    for (int i = 0; i < g_rule_count; i++) {
        collapse_rule_t *rule = &g_rules[i];
        if (!rule->active || rule->trigger != trigger) continue;

        matched++;

        /* Hangi bloğu çözeceğiz? */
        uint32_t target_id = rule->dust_block_id;
        if (target_id == 0) {
            /* Otomatik seçim: tetikleyici tipine göre */
            qd_block_type_t btype = trigger_to_block_type(trigger);
            qd_block_t *blk = qd_find_by_type(g_dust, btype);
            if (blk) target_id = blk->id;
        }

        uint8_t pt_buf[QD_BLOCK_SIZE];
        size_t  pt_len = 0;
        int     rc     = QD_ERR_NOT_FOUND;

        if (target_id != 0) {
            rc = qd_collapse(g_dust, target_id, pt_buf, sizeof(pt_buf), &pt_len);
        }

        if (rc == QD_ERR_TAG_MISMATCH) {
            pthread_mutex_lock(&g_collapse_mutex);
            g_stats.failed_collapses++;
            pthread_mutex_unlock(&g_collapse_mutex);
            continue;
        }

        /* Çöküş başarılı (veya blok yok ama aksiyon hâlâ çalışır) */
        pthread_mutex_lock(&g_collapse_mutex);
        g_stats.total_collapses++;
        g_stats.last_collapsed_id = target_id;
        pthread_mutex_unlock(&g_collapse_mutex);

        /* HAL aksiyonu */
        execute_action(rule, pt_buf, pt_len);

        pthread_mutex_lock(&g_collapse_mutex);
        g_stats.total_actions++;
        pthread_mutex_unlock(&g_collapse_mutex);

        /* Callback */
        collapse_callback_t cb = g_callbacks[(int)trigger];
        if (cb) cb(rule, pt_buf, pt_len);

        /* Güvenli: plaintext'i yığında sıfırla */
        memset(pt_buf, 0, pt_len);
    }

    /* Gecikme ölçümü */
    long elapsed = now_us() - t_start;
    pthread_mutex_lock(&g_collapse_mutex);
    if (g_stats.total_collapses > 0) {
        g_stats.avg_latency_us =
            (g_stats.avg_latency_us * (g_stats.total_collapses - 1) + elapsed)
            / g_stats.total_collapses;
    }
    if (elapsed > g_stats.max_latency_us)
        g_stats.max_latency_us = elapsed;
    pthread_mutex_unlock(&g_collapse_mutex);

    fprintf(stderr,
            "🪰 [ÇÖKÜŞ]: trigger=%d → %d kural, aksiyon tamamlandı "
            "(gecikme=%ld µs)\n",
            (int)trigger, matched, elapsed);

    return matched > 0 ? 0 : -1;
}

/* =========================================================================
 * Public API: collapse_fire
 * ========================================================================= */
int collapse_fire(collapse_trigger_t trigger,
                  const char        *user_input,
                  int                input_len)
{
    return fire_rules(trigger,
                      (const uint8_t *)user_input,
                      (size_t)(input_len > 0 ? input_len : 0));
}

/* =========================================================================
 * Public API: collapse_fire_sensor
 * ========================================================================= */
int collapse_fire_sensor(collapse_trigger_t trigger,
                         const uint8_t     *sensor_data,
                         size_t             len)
{
    return fire_rules(trigger, sensor_data, len);
}

/* =========================================================================
 * Public API: collapse_instant — kural araması yok, doğrudan dispatch
 * ========================================================================= */
int collapse_instant(uint32_t          dust_id,
                     collapse_action_t action,
                     int               arg)
{
    /*
     * 🪰 [ÇÖKÜŞ]: Ultra düşük gecikme yolu.
     * Kural tablosu atlanır — doğrudan blok çöküşü + aksiyon.
     */
    if (!g_dust || !g_hal) return -1;

    long t_start = now_us();

    uint8_t pt_buf[QD_BLOCK_SIZE];
    size_t  pt_len = 0;

    if (dust_id != 0)
        qd_collapse(g_dust, dust_id, pt_buf, sizeof(pt_buf), &pt_len);

    collapse_rule_t instant_rule;
    memset(&instant_rule, 0, sizeof(instant_rule));
    instant_rule.action     = action;
    instant_rule.action_arg = arg;
    instant_rule.active     = 1;

    int rc = execute_action(&instant_rule, pt_buf, pt_len);
    memset(pt_buf, 0, pt_len);

    long elapsed = now_us() - t_start;
    fprintf(stderr,
            "🪰 [ÇÖKÜŞ]: Anlık çöküş (id=%u, action=%d, gecikme=%ld µs)\n",
            dust_id, (int)action, elapsed);

    return rc;
}

/* =========================================================================
 * Public API: collapse_loop — olay döngüsü
 * =========================================================================
 *
 * poll() tabanlı döngü:
 *   - stdin: kullanıcı komutları
 *   - timerfd: periyodik nabız (1 Hz / 10 Hz)
 *
 * Gerçek uygulamada ağ soketi ve dokunmatik ekran fd'si de eklenir.
 * Bu döngü Sinek'in kalp atışıdır. Her tetikleyici bir çöküş doğurur.
 */
void collapse_loop(void)
{
    fprintf(stderr,
            "🪰 [ÇÖKÜŞ]: Olay döngüsü başlatıldı — Sinek nabzı atıyor\n");

    /* timerfd: 1 saniyelik periyodik tetik */
    g_timer_fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (g_timer_fd >= 0) {
        struct itimerspec its;
        its.it_interval.tv_sec  = 1;
        its.it_interval.tv_nsec = 0;
        its.it_value.tv_sec     = 1;
        its.it_value.tv_nsec    = 0;
        timerfd_settime(g_timer_fd, 0, &its, NULL);
    }

    g_running = 1;

    struct pollfd fds[2];
    int nfds = 0;

    /* stdin: kullanıcı komutları */
    fds[nfds].fd      = STDIN_FILENO;
    fds[nfds].events  = POLLIN;
    nfds++;

    /* timerfd */
    if (g_timer_fd >= 0) {
        fds[nfds].fd     = g_timer_fd;
        fds[nfds].events = POLLIN;
        nfds++;
    }

    while (g_running) {
        /* 10 ms zaman aşımı → DORMANT durum denetimi */
        int n = poll(fds, (nfds_t)nfds, 10);

        if (n < 0) {
            if (errno == EINTR) continue;
            fprintf(stderr,
                    "❌ [ÇÖKÜŞ]: poll() hatası: %s\n", strerror(errno));
            break;
        }

        if (n == 0) {
            /* Zaman aşımı — DORMANT denetimi (hiçbir şey yapma) */
            continue;
        }

        /* stdin olayı → kullanıcı komutu */
        if ((fds[0].revents & POLLIN) && fds[0].fd == STDIN_FILENO) {
            char cmd_buf[256];
            ssize_t r = read(STDIN_FILENO, cmd_buf, sizeof(cmd_buf) - 1);
            if (r > 0) {
                cmd_buf[r] = '\0';
                /* Satır sonu temizle */
                for (ssize_t i = 0; i < r; i++)
                    if (cmd_buf[i] == '\n') { cmd_buf[i] = '\0'; break; }

                fprintf(stderr,
                        "🪰 [ÇÖKÜŞ]: Kullanıcı komutu: \"%s\"\n", cmd_buf);
                collapse_fire(COLLAPSE_TRIGGER_USER, cmd_buf, (int)r);
            }
        }

        /* timerfd olayı → periyodik nabız */
        if (nfds > 1 && (fds[1].revents & POLLIN)) {
            uint64_t expirations;
            ssize_t r = read(g_timer_fd, &expirations, sizeof(expirations));
            (void)r; /* sayım önemsiz */
            collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        }
    }

    if (g_timer_fd >= 0) {
        close(g_timer_fd);
        g_timer_fd = -1;
    }

    fprintf(stderr, "🪰 [ÇÖKÜŞ]: Olay döngüsü durdu\n");
}

/* =========================================================================
 * Public API: collapse_shutdown
 * ========================================================================= */
void collapse_shutdown(void)
{
    g_running = 0;
    fprintf(stderr, "🪰 [ÇÖKÜŞ]: Motor kapatılıyor...\n");
}

/* =========================================================================
 * Public API: collapse_get_stats
 * ========================================================================= */
void collapse_get_stats(collapse_stats_t *out)
{
    if (!out) return;
    pthread_mutex_lock(&g_collapse_mutex);
    memcpy(out, &g_stats, sizeof(collapse_stats_t));
    pthread_mutex_unlock(&g_collapse_mutex);
}
