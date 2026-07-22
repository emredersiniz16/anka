/*
 * quantum_dust.h — Kuantum Tozu Şifreli Veri Deposu Arayüzü
 * ===========================================================
 * 🪰 [KUANTUM]: Toz mühürler, çöker ve evriltir.
 */

#ifndef QUANTUM_DUST_H
#define QUANTUM_DUST_H

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <pthread.h>

#ifdef __cplusplus
extern "C" {
#endif

/* =========================================================================
 * Sabitler
 * ========================================================================= */

#define QD_MAX_BLOCKS   64
#define QD_BLOCK_SIZE   1024
#define QD_KEY_LEN      32   /* ChaCha20-256 anahtarı */
#define QD_NONCE_LEN    12   /* ChaCha20-Poly1305 nonce */
#define QD_TAG_LEN      16   /* Poly1305 kimlik doğrulama etiketi */
#define QD_SALT_LEN     32   /* HKDF tuzu */

/* =========================================================================
 * Hata Kodları
 * ========================================================================= */

#define QD_OK              0
#define QD_ERR_NOT_INIT   -1
#define QD_ERR_TOO_LARGE  -2
#define QD_ERR_STORE_FULL -3
#define QD_ERR_CRYPTO     -4
#define QD_ERR_TAG_MISMATCH -5
#define QD_ERR_NOT_FOUND      -6
#define QD_ERR_IO             -7
#define QD_ERR_BUF_TOO_SMALL  -8

/* =========================================================================
 * Blok Tipleri
 * ========================================================================= */

typedef enum {
    QD_TYPE_SENSOR_DATA   = 0,
    QD_TYPE_USER_INTERACT = 1,
    QD_TYPE_KOVAN_STATE   = 2,
    QD_TYPE_AMBIENT_OBS   = 3,
    QD_TYPE_COMMAND_QUEUE = 4,
} qd_block_type_t;

/* =========================================================================
 * Şifreli Blok
 * ========================================================================= */

typedef struct {
    uint32_t        id;
    qd_block_type_t type;
    uint8_t         nonce[QD_NONCE_LEN];
    uint8_t         ciphertext[QD_BLOCK_SIZE];
    uint8_t         tag[QD_TAG_LEN];
    size_t          ciphertext_len;
} qd_block_t;

/* =========================================================================
 * Şifreli Veri Deposu
 * ========================================================================= */

typedef struct {
    qd_block_t      blocks[QD_MAX_BLOCKS];
    int             block_count;
    uint8_t         master_key[QD_KEY_LEN];
    uint8_t         salt[QD_SALT_LEN];
    int             key_initialized;
    pthread_mutex_t lock;
} qd_store_t;

/* =========================================================================
 * Public API
 * ========================================================================= */

int         qd_init          (qd_store_t *store,
                               const char *device_fingerprint,
                               const char *kovan_secret);

int         qd_seal          (qd_store_t *store,
                               qd_block_type_t type,
                               const uint8_t  *plaintext,
                               size_t          len,
                               uint32_t       *out_id);

qd_block_t *qd_find_block    (qd_store_t *store, uint32_t block_id);
qd_block_t *qd_find_by_type  (qd_store_t *store, qd_block_type_t type);

int         qd_collapse      (qd_store_t *store,
                               uint32_t    block_id,
                               uint8_t    *out_plaintext,
                               size_t      out_size,
                               size_t     *out_len);

int         qd_evolve        (qd_store_t    *store,
                               uint32_t       block_id,
                               const uint8_t *new_data,
                               size_t         len);

void        qd_purge         (qd_store_t *store, uint32_t block_id);
void        qd_destroy       (qd_store_t *store);

int         qd_save_disk     (qd_store_t *store, const char *path);
int         qd_load_disk     (qd_store_t *store, const char *path);

int         qd_count_by_type (qd_store_t *store, qd_block_type_t type);
size_t      qd_total_noise_bytes(qd_store_t *store);

#ifdef __cplusplus
}
#endif

#endif /* QUANTUM_DUST_H */
