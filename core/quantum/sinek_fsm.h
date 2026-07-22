/*
 * sinek_fsm.h — Sinek Yaşam Döngüsü FSM Arayüzü
 * ================================================
 * 🪰 [SİNEK]: Veri odaklı geçiş tablosu.
 * Yeni davranış eklemek için sadece geçiş tablosuna satır ekle.
 */

#ifndef SINEK_FSM_H
#define SINEK_FSM_H

#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include <pthread.h>
#include <stdio.h>
#include "quantum_dust.h"
#include "collapse_engine.h"

#ifdef __cplusplus
extern "C" {
#endif

/* =========================================================================
 * FSM Durumları
 * ========================================================================= */

typedef enum {
    SINEK_DORMANT   = 0,  /* 1Hz uyku modu */
    SINEK_AWAKE     = 1,  /* uyanık, bekliyor */
    SINEK_OBSERVING = 2,  /* sensörleri izliyor */
    SINEK_COLLAPSED = 3,  /* çöküş gerçekleşti */
    SINEK_ACTING    = 4,  /* aksiyon yürütüyor */
    SINEK_SYNCING   = 5,  /* Kovan ile senkronizasyon */
} sinek_state_t;

/* =========================================================================
 * FSM Olayları
 * ========================================================================= */

typedef enum {
    SINEK_EVT_SENSOR_DATA    = 0,
    SINEK_EVT_USER_COMMAND   = 1,
    SINEK_EVT_KOVAN_MSG      = 2,
    SINEK_EVT_TIMER          = 3,
    SINEK_EVT_AMBIENT_CHANGE = 4,
    SINEK_EVT_ACTION_DONE    = 5,
    SINEK_EVT_SYNC_DONE      = 6,
    SINEK_EVT_OFFLINE        = 7,
    SINEK_EVT_ONLINE         = 8,
    SINEK_EVT_SLEEP          = 9,
    SINEK_EVT_WAKE           = 10,
} sinek_event_t;

/* =========================================================================
 * FSM Durumu
 * ========================================================================= */

typedef struct {
    sinek_state_t    state;
    qd_store_t      *dust;
    AnkaHAL         *hal;
    int              kovan_online;
    int              actions_count;
    int              collapses_count;
    long             uptime_ms;
    struct timespec  start_time;
    pthread_mutex_t  lock;
} sinek_fsm_t;

/* =========================================================================
 * Public API
 * ========================================================================= */

int           sinek_fsm_init         (sinek_fsm_t *fsm,
                                       qd_store_t  *dust,
                                       AnkaHAL     *hal);

int           sinek_fsm_handle_event (sinek_fsm_t  *fsm,
                                       sinek_event_t evt,
                                       const void   *data,
                                       size_t        data_len);

sinek_state_t sinek_fsm_get_state    (sinek_fsm_t *fsm);
void          sinek_fsm_uptime_update(sinek_fsm_t *fsm);
void          sinek_fsm_print_status (sinek_fsm_t *fsm, FILE *out);
void          sinek_fsm_destroy      (sinek_fsm_t *fsm);

const char   *sinek_state_name       (sinek_state_t s);
const char   *sinek_event_name       (sinek_event_t e);

#ifdef __cplusplus
}
#endif

#endif /* SINEK_FSM_H */
