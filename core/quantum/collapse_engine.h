#ifndef ANKA_COLLAPSE_ENGINE_H
#define ANKA_COLLAPSE_ENGINE_H

#include <stddef.h>
#include <stdint.h>
#include "quantum_dust.h"
#include "../hal/anka_hal.h" // HAL tanımı burada

/* ---- Tipler ve Enumlar (Hataların sebebi burasıydı) ---- */
typedef enum {
    COLLAPSE_TRIGGER_SENSOR  = 1,
    COLLAPSE_TRIGGER_USER    = 2,
    COLLAPSE_TRIGGER_KOVAN   = 3,
    COLLAPSE_TRIGGER_TIMER   = 4,
    COLLAPSE_TRIGGER_AMBIENT = 5,
    COLLAPSE_TRIGGER_MAX     = 6,
} collapse_trigger_t;

typedef enum {
    COLLAPSE_ACT_VIBRATE  = 1,
    COLLAPSE_ACT_SPEAK    = 2,
    COLLAPSE_ACT_CAPTURE  = 3,
    COLLAPSE_ACT_DISPLAY  = 4,
    COLLAPSE_ACT_SYNC     = 5,
    COLLAPSE_ACT_DORMANT  = 6,
} collapse_action_t;

typedef struct {
    collapse_trigger_t trigger;
    uint32_t           dust_block_id;
    collapse_action_t  action;
    int                action_arg;
    char               action_text[256];
    int                active;
} collapse_rule_t;

typedef void (*collapse_callback_t)(const collapse_rule_t *rule, const uint8_t *plaintext, size_t len);

/* ---- Public API ---- */
int  collapse_init(qd_store_t *dust, AnkaHAL *hal);
int  collapse_register(collapse_trigger_t trigger, collapse_action_t action, uint32_t dust_id);
int  collapse_fire(collapse_trigger_t trigger, const char *user_input, int input_len);
// ... (Diğer fonksiyon imzaların burada kalsın) ...

#endif
