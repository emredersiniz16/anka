#ifndef ANKA_QUANTUM_DUST_H
#define ANKA_QUANTUM_DUST_H

/*
 * quantum_dust.h — Kuantum Tozu Şifreli Veri Deposu API
 * ======================================================
 * 🪰 [KUANTUM]: Bir "Toz" parçası, dışarıdan bakan için rastgele
 * gürültüdür. Sinek çekirdeği tarafından "gözlemlendiğinde"
 * (çözüldüğünde) anlamlı veriye çöker.
 *
 * Gözlemci etkisi: Anahtara sahip olan çözer, diğerleri gürültü görür.
 */

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <pthread.h>

/* ---- Sabitler ---------------------------------------------------------- */
#define QD_MAX_BLOCKS    256    /* maksimum eş zamanlı toz bloğu          */
#define QD_BLOCK_SIZE    4096   /* her blok en fazla 4 KB gürültü taşır   */
#define QD_KEY_LEN       32     /* ChaCha20-Poly1305 anahtar uzunluğu      */
#define QD_NONCE_LEN     12     /* 96-bit nonce (RFC 8439)                 */
#define QD_TAG_LEN       16     /* Poly1305 / HMAC-SHA256[:16] tag          */
#define QD_SALT_LEN      32     /* HKDF tuz uzunluğu                       */

/* ---- Toz Blok Tipi ----------------------------------------------------- */
typedef enum {
    QD_TYPE_SENSOR_DATA    = 1, /* ham sensör okumaları                    */
    QD_TYPE_KOVAN_STATE    = 2, /* Kovan FSM anlık görüntüsü               */
    QD_TYPE_USER_INTERACT  = 3, /* kullanıcı girdisi / komutu              */
    QD_TYPE_AMBIENT_OBS    = 4, /* ortam gözlemi (ışık, ses, titreşim)     */
    QD_TYPE_COMMAND_QUEUE  = 5, /* bekleyen HAL komutları                  */
} qd_block_type_t;

/* ---- Kuantum Tozu Bloğu ------------------------------------------------ */
/*
 * Bu yapı dışarıdan bakan için tamamen anlamsızdır:
 * ciphertext alanı matematiksel olarak rastgele gürültüden ayırt edilemez.
 * id ve type alanları meta-veri, anahtar olmadan anlamsızdır.
 */
typedef struct {
    uint32_t        id;                        /* blok kimliği (nonce+type hash) */
    qd_block_type_t type;                      /* toz tipi                       */
    size_t          ciphertext_len;            /* kullanılan gerçek byte sayısı  */
    uint8_t         nonce[QD_NONCE_LEN];       /* tek kullanımlık rastgele değer */
    uint8_t         tag[QD_TAG_LEN];           /* bütünlük etiketi (AEAD/HMAC)   */
    uint8_t         ciphertext[QD_BLOCK_SIZE]; /* şifreli veri — saf gürültü     */
} qd_block_t;

/* ---- Toz Deposu -------------------------------------------------------- */
/*
 * Tüm toz bloklarını bellekte tutan ana yapı.
 * master_key: cihaz parmak izi + kovan sırrından türetilir (HKDF-SHA256).
 * lock: tüm okuma/yazma işlemleri bu mutex altında gerçekleşir.
 */
typedef struct {
    qd_block_t      blocks[QD_MAX_BLOCKS]; /* toz bloğu dizisi               */
    int             block_count;           /* aktif blok sayısı               */
    uint8_t         master_key[QD_KEY_LEN];/* türetilmiş ana anahtar          */
    int             key_initialized;       /* anahtar türetildi mi?           */
    uint8_t         salt[QD_SALT_LEN];     /* HKDF tuzu (sabit per-device)    */
    pthread_mutex_t lock;                  /* iş parçacığı güvenliği          */
} qd_store_t;

/* ---- Hata Kodları ------------------------------------------------------ */
#define QD_OK                  0
#define QD_ERR_NOT_INIT       -1  /* depo başlatılmadı                     */
#define QD_ERR_STORE_FULL     -2  /* QD_MAX_BLOCKS doldu                   */
#define QD_ERR_NOT_FOUND      -3  /* blok ID bulunamadı                    */
#define QD_ERR_TAG_MISMATCH   -4  /* AEAD doğrulama başarısız (ret. -4)    */
#define QD_ERR_BUF_TOO_SMALL  -5  /* çıktı tamponu yetersiz                */
#define QD_ERR_CRYPTO         -6  /* şifreleme/çözme hatası                */
#define QD_ERR_IO             -7  /* dosya okuma/yazma hatası              */
#define QD_ERR_TOO_LARGE      -8  /* plaintext QD_BLOCK_SIZE'ı aşıyor      */

/* ---- Public API -------------------------------------------------------- */

/*
 * qd_init — Depoyu başlat, ana anahtarı türet.
 * device_fingerprint: cihaz kimliği (örn. /proc/cpuinfo hash)
 * kovan_secret:       paylaşılan Kovan sırrı
 * Döndürür: QD_OK veya hata kodu
 */
int qd_init(qd_store_t *store,
            const char *device_fingerprint,
            const char *kovan_secret);

/*
 * qd_seal — Düz metni şifrele, yeni toz bloğu oluştur.
 * out_id: yeni bloğun kimliği buraya yazılır
 * Döndürür: QD_OK veya hata kodu
 */
int qd_seal(qd_store_t       *store,
            qd_block_type_t   type,
            const uint8_t    *plaintext,
            size_t            len,
            uint32_t         *out_id);

/*
 * qd_collapse — Toz bloğunu çöz (şifre çöz), düz metni döndür.
 * Gözlemci etkisi: anahtar olmadan çöküş gerçekleşmez.
 * Döndürür: QD_OK veya QD_ERR_TAG_MISMATCH (gözlemci reddedildi)
 */
int qd_collapse(qd_store_t *store,
                uint32_t    block_id,
                uint8_t    *out_buf,
                size_t      buf_len,
                size_t     *out_len);

/*
 * qd_evolve — Mevcut bloğu yeni veriyle güncelle (yeni nonce, aynı ID).
 * Süperpozisyon evrimi: gürültü değişir, kimlik sabit kalır.
 * Döndürür: QD_OK veya hata kodu
 */
int qd_evolve(qd_store_t    *store,
              uint32_t       block_id,
              const uint8_t *new_data,
              size_t         len);

/*
 * qd_purge — Bloğu bellekten sil (güvenli sıfırlama).
 */
void qd_purge(qd_store_t *store, uint32_t block_id);

/*
 * qd_destroy — Tüm depoyu temizle, anahtarı sıfırla.
 */
void qd_destroy(qd_store_t *store);

/*
 * qd_save_disk — Tüm depoyu diske yaz (0600 izni).
 * Not: Dosya içeriği zaten ciphertext — ekstra şifrelemeye gerek yok,
 * ama dosya izinleri 0600 olmalı.
 */
int qd_save_disk(qd_store_t *store, const char *path);

/*
 * qd_load_disk — Diskten depoyu yükle.
 */
int qd_load_disk(qd_store_t *store, const char *path);

/*
 * qd_count_by_type — Belirli tipteki blok sayısını döndür.
 */
int qd_count_by_type(qd_store_t *store, qd_block_type_t type);

/*
 * qd_total_noise_bytes — Toplam gürültü byte'ı (metrik).
 * "Sinek şu an X byte kuantum tozu taşıyor."
 */
size_t qd_total_noise_bytes(qd_store_t *store);

/* ---- İç yardımcı: blok arama (harici kullanım için değil) ------------- */
qd_block_t *qd_find_block(qd_store_t *store, uint32_t block_id);
qd_block_t *qd_find_by_type(qd_store_t *store, qd_block_type_t type);

#endif /* ANKA_QUANTUM_DUST_H */
