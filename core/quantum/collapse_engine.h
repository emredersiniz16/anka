#ifndef ANKA_COLLAPSE_ENGINE_H
#define ANKA_COLLAPSE_ENGINE_H

/*
 * collapse_engine.h — Çöküş Motoru API
 * 🪰 [ÇÖKÜŞ]: Tetikleyici geldiğinde Kuantum Tozu'nu anlık olarak çözer.
 */

#include <stddef.h>
#include <stdint.h>
#include "quantum_dust.h"

/* 
 * DÜZELTME: AnkaHAL tanımını kendimiz yapmak yerine 
 * gerçek HAL başlığını dahil ediyoruz.
 */
#include "../hal/anka_hal.h"

/* ---- Tetikleyici Tipleri ----------------------------------------------- */
typedef enum {
    COLLAPSE_TRIGGER_SENSOR  = 1,
    COLLAPSE_TRIGGER_USER    = 2,
    COLLAPSE_TRIGGER_KOVAN   = 3,
    COLLAPSE_TRIGGER_TIMER   = 4,
    COLLAPSE_TRIGGER_AMBIENT = 5,
    COLLAPSE_TRIGGER_MAX     = 6,
} collapse_trigger_t;

/* ---- Aksiyon Tipleri --------------------------------------------------- */
typedef enum {
    COLLAPSE_ACT_VIBRATE  = 1,
    COLLAPSE_ACT_SPEAK    = 2,
    COLLAPSE_ACT_CAPTURE  = 3,
    COLLAPSE_ACT_DISPLAY  = 4,
    COLLAPSE_ACT_SYNC     = 5,
    COLLAPSE_ACT_DORMANT  = 6,
} collapse_action_t;

/* ---- Çöküş Kuralı ------------------------------------------------------ */
typedef struct {
    collapse_trigger_t trigger;
    uint32_t           dust_block_id;
    collapse_action_t  action;
    int                action_arg;
    char               action_text[256];
    int                active;
} collapse_rule_t;

/* ---- Çöküş Geri Çağrısı ----------------------------------------------- */
typedef void (*collapse_callback_t)(const collapse_rule_t *rule,
                                    const uint8_t         *plaintext,
                                    size_t                 len);

/* ---- İstatistik yapısı ------------------------------------------------- */
typedef struct {
    long     total_collapses;
    long     failed_collapses;
    long     total_actions;
    long     avg_latency_us;
    long     max_latency_us;
    uint32_t last_collapsed_id;
} collapse_stats_t;

/* ---- Public API -------------------------------------------------------- */

int  collapse_init(qd_store_t *dust, AnkaHAL *hal);
int  collapse_register(collapse_trigger_t trigger, collapse_action_t action, uint32_t dust_id);
int  collapse_register_ex(collapse_trigger_t trigger, collapse_action_t action, uint32_t dust_id, int arg, const char *text);
int  collapse_register_callback(collapse_trigger_t trigger, collapse_callback_t cb);
int  collapse_fire(collapse_trigger_t trigger, const char *user_input, int input_len);
int  collapse_fire_sensor(collapse_trigger_t trigger, const uint8_t *sensor_data, size_t len);
int  collapse_instant(uint32_t dust_id, collapse_action_t action, int arg);
void collapse_loop(void);
void collapse_shutdown(void);
void collapse_get_stats(collapse_stats_t *out);

#endif /* ANKA_COLLAPSE_ENGINE_H */
