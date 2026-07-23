/*
 * collapse_engine.h — Çöküş Motoru Arayüzü
 * ==========================================
 * 🪰 [ÇÖKÜŞ]: Bu döngü Sinek'in kalp atışıdır.
 * Her tetikleyici bir çöküş doğurur.
 */

#ifndef COLLAPSE_ENGINE_H
#define COLLAPSE_ENGINE_H

#include <stdint.h>
#include <stddef.h>
#include "quantum_dust.h"
#include "anka_hal.h"  /* AnkaHAL tanımı artık tek bir ana merkezden çekiliyor */

#ifdef __cplusplus
extern "C" {
#endif

/* =========================================================================
 * Tetikleyici Tipleri
 * ========================================================================= */

typedef enum {
    COLLAPSE_TRIGGER_SENSOR  = 0,
    COLLAPSE_TRIGGER_USER    = 1,
    COLLAPSE_TRIGGER_KOVAN   = 2,
    COLLAPSE_TRIGGER_AMBIENT = 3,
    COLLAPSE_TRIGGER_TIMER   = 4,
    COLLAPSE_TRIGGER_MAX     /* sentinel — her zaman sonda */
} collapse_trigger_t;

/* =========================================================================
 * Aksiyon Tipleri
 * ========================================================================= */

typedef enum {
    COLLAPSE_ACT_VIBRATE = 0,
    COLLAPSE_ACT_SPEAK   = 1,
    COLLAPSE_ACT_CAPTURE = 2,
    COLLAPSE_ACT_DISPLAY = 3,
    COLLAPSE_ACT_SYNC    = 4,
    COLLAPSE_ACT_DORMANT = 5,
} collapse_action_t;

/* =========================================================================
 * Çöküş Kuralı
 * ========================================================================= */

#define COLLAPSE_ACTION_TEXT_MAX 256

typedef struct {
    collapse_trigger_t trigger;
    collapse_action_t  action;
    uint32_t           dust_block_id;
    int                action_arg;
    int                active;
    char               action_text[COLLAPSE_ACTION_TEXT_MAX];
} collapse_rule_t;

/* =========================================================================
 * Olay Geri Çağırması
 * ========================================================================= */

typedef void (*collapse_callback_t)(const collapse_rule_t *rule,
                                    const uint8_t         *data,
                                    size_t                 len);

/* =========================================================================
 * İstatistikler
 * ========================================================================= */

typedef struct {
    long     total_collapses;
    long     failed_collapses;
    long     total_actions;
    uint32_t last_collapsed_id;
    long     avg_latency_us;
    long     max_latency_us;
} collapse_stats_t;

/* =========================================================================
 * Public API
 * ========================================================================= */

int  collapse_init             (qd_store_t *dust, AnkaHAL *hal);

int  collapse_register         (collapse_trigger_t trigger,
                                collapse_action_t  action,
                                uint32_t           dust_id);

int  collapse_register_ex      (collapse_trigger_t trigger,
                                collapse_action_t  action,
                                uint32_t           dust_id,
                                int                arg,
                                const char        *text);

int  collapse_register_callback(collapse_trigger_t  trigger,
                                collapse_callback_t cb);

int  collapse_fire             (collapse_trigger_t trigger,
                                const char        *user_input,
                                int                input_len);

int  collapse_fire_sensor      (collapse_trigger_t trigger,
                                const uint8_t     *sensor_data,
                                size_t             len);

int  collapse_instant          (uint32_t          dust_id,
                                collapse_action_t action,
                                int               arg);

void collapse_loop             (void);
void collapse_shutdown         (void);
void collapse_get_stats        (collapse_stats_t *out);

#ifdef __cplusplus
}
#endif

#endif /* COLLAPSE_ENGINE_H */
