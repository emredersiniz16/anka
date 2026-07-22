/*
 * quantum_dust.c — Kuantum Tozu Şifreli Veri Deposu Uygulaması
 * =============================================================
 * 🪰 [KUANTUM]: Bu modül toz mühürler, çöker ve evriltir.
 *
 * Derleme:
 *   OpenSSL ile:   gcc -DHAVE_OPENSSL -lssl -lcrypto quantum_dust.c
 *   OpenSSL'siz:   gcc quantum_dust.c  (GEÇİCİ — üretimde KULLANMA)
 */

#include "quantum_dust.h"

#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>

#ifdef HAVE_OPENSSL
#  include <openssl/evp.h>
#  include <openssl/rand.h>
#  include <openssl/hmac.h>
#  include <openssl/sha.h>
#  include <openssl/kdf.h>
#else
/* SHA-256 gömülü uygulama — OpenSSL yoksa kullanılır */
#  include <stdint.h>
#endif

/* =========================================================================
 * SHA-256 gömülü uygulama (OpenSSL olmadığında)
 * ========================================================================= */
#ifndef HAVE_OPENSSL

typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t  buf[64];
} sha256_ctx_t;

static const uint32_t K256[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,
    0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,
    0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,
    0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,
    0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,
    0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,
    0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,
    0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,
    0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

#define ROTR32(x,n) (((x)>>(n))|((x)<<(32-(n))))
#define CH(e,f,g)   (((e)&(f))^(~(e)&(g)))
#define MAJ(a,b,c)  (((a)&(b))^((a)&(c))^((b)&(c)))
#define EP0(a)      (ROTR32(a,2)^ROTR32(a,13)^ROTR32(a,22))
#define EP1(e)      (ROTR32(e,6)^ROTR32(e,11)^ROTR32(e,25))
#define SIG0(x)     (ROTR32(x,7)^ROTR32(x,18)^((x)>>3))
#define SIG1(x)     (ROTR32(x,17)^ROTR32(x,19)^((x)>>10))

static void sha256_transform(sha256_ctx_t *ctx, const uint8_t *data)
{
    uint32_t a,b,c,d,e,f,g,h,t1,t2,m[64];
    int i;
    for (i = 0; i < 16; i++) {
        m[i]  = ((uint32_t)data[i*4  ] << 24)
              | ((uint32_t)data[i*4+1] << 16)
              | ((uint32_t)data[i*4+2] <<  8)
              | ((uint32_t)data[i*4+3]);
    }
    for (; i < 64; i++)
        m[i] = SIG1(m[i-2]) + m[i-7] + SIG0(m[i-15]) + m[i-16];

    a=ctx->state[0]; b=ctx->state[1]; c=ctx->state[2]; d=ctx->state[3];
    e=ctx->state[4]; f=ctx->state[5]; g=ctx->state[6]; h=ctx->state[7];

    for (i = 0; i < 64; i++) {
        t1 = h + EP1(e) + CH(e,f,g) + K256[i] + m[i];
        t2 = EP0(a) + MAJ(a,b,c);
        h=g; g=f; f=e; e=d+t1;
        d=c; c=b; b=a; a=t1+t2;
    }
    ctx->state[0]+=a; ctx->state[1]+=b; ctx->state[2]+=c; ctx->state[3]+=d;
    ctx->state[4]+=e; ctx->state[5]+=f; ctx->state[6]+=g; ctx->state[7]+=h;
}

static void sha256_init(sha256_ctx_t *ctx)
{
    ctx->count = 0;
    ctx->state[0]=0x6a09e667; ctx->state[1]=0xbb67ae85;
    ctx->state[2]=0x3c6ef372; ctx->state[3]=0xa54ff53a;
    ctx->state[4]=0x510e527f; ctx->state[5]=0x9b05688c;
    ctx->state[6]=0x1f83d9ab; ctx->state[7]=0x5be0cd19;
}

static void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len)
{
    size_t i;
    for (i = 0; i < len; i++) {
        ctx->buf[ctx->count % 64] = data[i];
        ctx->count++;
        if ((ctx->count % 64) == 0)
            sha256_transform(ctx, ctx->buf);
    }
}

static void sha256_final(sha256_ctx_t *ctx, uint8_t *digest)
{
    uint64_t bits = ctx->count * 8;
    uint8_t  b = 0x80;
    sha256_update(ctx, &b, 1);
    b = 0x00;
    while ((ctx->count % 64) != 56)
        sha256_update(ctx, &b, 1);
    /* bit uzunluğunu big-endian ekle */
    uint8_t len_bytes[8];
    for (int i = 7; i >= 0; i--) { len_bytes[i] = (uint8_t)(bits & 0xFF); bits >>= 8; }
    sha256_update(ctx, len_bytes, 8);
    for (int i = 0; i < 8; i++) {
        digest[i*4  ] = (ctx->state[i] >> 24) & 0xFF;
        digest[i*4+1] = (ctx->state[i] >> 16) & 0xFF;
        digest[i*4+2] = (ctx->state[i] >>  8) & 0xFF;
        digest[i*4+3] =  ctx->state[i]         & 0xFF;
    }
}

/* HMAC-SHA256 gömülü */
static void hmac_sha256(const uint8_t *key, size_t key_len,
                        const uint8_t *data, size_t data_len,
                        uint8_t *out)
{
    uint8_t k[64], ipad[64], opad[64], inner[32];
    sha256_ctx_t ctx;

    memset(k, 0, 64);
    if (key_len > 64) {
        sha256_init(&ctx);
        sha256_update(&ctx, key, key_len);
        sha256_final(&ctx, k);
    } else {
        memcpy(k, key, key_len);
    }
    for (int i = 0; i < 64; i++) { ipad[i] = k[i] ^ 0x36; opad[i] = k[i] ^ 0x5c; }

    sha256_init(&ctx);
    sha256_update(&ctx, ipad, 64);
    sha256_update(&ctx, data, data_len);
    sha256_final(&ctx, inner);

    sha256_init(&ctx);
    sha256_update(&ctx, opad, 64);
    sha256_update(&ctx, inner, 32);
    sha256_final(&ctx, out);
}

#endif /* !HAVE_OPENSSL */

/* =========================================================================
 * Yardımcı: /dev/urandom'dan rastgele byte oku
 * ========================================================================= */
static int read_urandom(uint8_t *buf, size_t len)
{
    int fd = open("/dev/urandom", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t r = read(fd, buf, len);
    close(fd);
    return (r == (ssize_t)len) ? 0 : -1;
}

/* =========================================================================
 * Anahtar Türetme — HKDF-SHA256(device_fingerprint || kovan_secret)
 * ========================================================================= */
static int derive_master_key(const char *device_fp, const char *kovan_secret,
                              const uint8_t *salt,  uint8_t *out_key)
{
    /*
     * 🪰 [KUANTUM]: Ana anahtar türetimi.
     * IKM = device_fingerprint || kovan_secret
     * HKDF-SHA256(salt, IKM, info="AnkaOS-QuantumDust-v1") → 32 byte
     */

#ifdef HAVE_OPENSSL
    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_HKDF, NULL);
    if (!pctx) return QD_ERR_CRYPTO;

    size_t fp_len     = strlen(device_fp);
    size_t secret_len = strlen(kovan_secret);
    size_t ikm_len    = fp_len + secret_len;
    uint8_t *ikm      = malloc(ikm_len);
    if (!ikm) { EVP_PKEY_CTX_free(pctx); return QD_ERR_CRYPTO; }
    memcpy(ikm,         device_fp,    fp_len);
    memcpy(ikm+fp_len,  kovan_secret, secret_len);

    static const uint8_t info[] = "AnkaOS-QuantumDust-v1";
    size_t out_len = QD_KEY_LEN;
    int ok = (EVP_PKEY_derive_init(pctx)                                  == 1 &&
              EVP_PKEY_CTX_set_hkdf_md(pctx, EVP_sha256())                == 1 &&
              EVP_PKEY_CTX_set1_hkdf_salt(pctx, salt, QD_SALT_LEN)        == 1 &&
              EVP_PKEY_CTX_set1_hkdf_key(pctx, ikm, (int)ikm_len)         == 1 &&
              EVP_PKEY_CTX_add1_hkdf_info(pctx, info, sizeof(info)-1)     == 1 &&
              EVP_PKEY_derive(pctx, out_key, &out_len)                     == 1);

    EVP_PKEY_CTX_free(pctx);
    memset(ikm, 0, ikm_len);
    free(ikm);
    return ok ? QD_OK : QD_ERR_CRYPTO;

#else
    /*
     * GEÇİCİ: Manuel HKDF-SHA256 (RFC 5869, tek adım)
     * NOT: Bu implementasyon güvenlidir (HMAC-SHA256 tabanlı),
     * ancak OpenSSL EVP doğrulamasından geçmemiştir.
     * Üretimde: -DHAVE_OPENSSL ile derle.
     */
    size_t fp_len     = strlen(device_fp);
    size_t secret_len = strlen(kovan_secret);
    size_t ikm_len    = fp_len + secret_len;
    uint8_t *ikm      = malloc(ikm_len);
    if (!ikm) return QD_ERR_CRYPTO;
    memcpy(ikm,        device_fp,    fp_len);
    memcpy(ikm+fp_len, kovan_secret, secret_len);

    /* HKDF-Extract: PRK = HMAC-SHA256(salt, IKM) */
    uint8_t prk[32];
    hmac_sha256(salt, QD_SALT_LEN, ikm, ikm_len, prk);
    memset(ikm, 0, ikm_len);
    free(ikm);

    /* HKDF-Expand: T(1) = HMAC-SHA256(PRK, "" || 0x01) → 32 byte */
    static const uint8_t info_block[] = "AnkaOS-QuantumDust-v1\x01";
    hmac_sha256(prk, 32, info_block, sizeof(info_block)-1, out_key);
    memset(prk, 0, 32);
    return QD_OK;
#endif
}

/* =========================================================================
 * GEÇİCİ Fallback Şifreleme — XOR-stream + HMAC-SHA256 etiketi
 * =========================================================================
 *
 * ⚠️  GEÇİCİ implementasyon — XOR stream cipher with SHA-256 KDF
 * NOT: Bu güvenli DEĞİL (ChaCha20 değil, Poly1305 değil).
 *      OpenSSL ile derle: -DHAVE_OPENSSL
 *      Sadece geliştirme/test için. Üretimde ChaCha20-Poly1305 kullan.
 */
#ifndef HAVE_OPENSSL

static int fallback_encrypt(const uint8_t *key,   /* QD_KEY_LEN byte */
                            const uint8_t *nonce,  /* QD_NONCE_LEN byte */
                            const uint8_t *pt,     size_t pt_len,
                            uint8_t       *ct,
                            uint8_t       *tag)    /* QD_TAG_LEN byte çıktı */
{
    /*
     * Anahtar akışı üretimi:
     *   Her 32-byte blok için: block_key = SHA256(key || nonce || counter)
     *   Düz metin XOR anahtar akışı = şifreli metin
     *
     * Etiket: HMAC-SHA256(key, nonce || ciphertext) → ilk 16 byte
     */
    uint8_t  block_input[QD_KEY_LEN + QD_NONCE_LEN + 4];
    uint8_t  keystream_block[32];
    sha256_ctx_t ctx;
    size_t   processed = 0;
    uint32_t counter   = 0;

    memcpy(block_input,                key,   QD_KEY_LEN);
    memcpy(block_input + QD_KEY_LEN,   nonce, QD_NONCE_LEN);

    while (processed < pt_len) {
        /* counter big-endian */
        block_input[QD_KEY_LEN + QD_NONCE_LEN + 0] = (counter >> 24) & 0xFF;
        block_input[QD_KEY_LEN + QD_NONCE_LEN + 1] = (counter >> 16) & 0xFF;
        block_input[QD_KEY_LEN + QD_NONCE_LEN + 2] = (counter >>  8) & 0xFF;
        block_input[QD_KEY_LEN + QD_NONCE_LEN + 3] =  counter        & 0xFF;

        sha256_init(&ctx);
        sha256_update(&ctx, block_input, sizeof(block_input));
        sha256_final(&ctx, keystream_block);

        size_t chunk = pt_len - processed;
        if (chunk > 32) chunk = 32;
        for (size_t i = 0; i < chunk; i++)
            ct[processed + i] = pt[processed + i] ^ keystream_block[i];

        processed += chunk;
        counter++;
    }

    /* Etiket: HMAC-SHA256(key, nonce || ct) → ilk 16 byte */
    size_t  mac_input_len = QD_NONCE_LEN + pt_len;
    uint8_t *mac_input    = malloc(mac_input_len);
    if (!mac_input) return QD_ERR_CRYPTO;
    memcpy(mac_input,                nonce, QD_NONCE_LEN);
    memcpy(mac_input + QD_NONCE_LEN, ct,    pt_len);

    uint8_t full_mac[32];
    hmac_sha256(key, QD_KEY_LEN, mac_input, mac_input_len, full_mac);
    memcpy(tag, full_mac, QD_TAG_LEN);

    memset(mac_input, 0, mac_input_len);
    free(mac_input);
    memset(keystream_block, 0, 32);
    return QD_OK;
}

static int fallback_decrypt(const uint8_t *key,
                            const uint8_t *nonce,
                            const uint8_t *ct,  size_t ct_len,
                            const uint8_t *tag,
                            uint8_t       *pt)
{
    /* Etiket doğrulama: HMAC-SHA256(key, nonce || ct) */
    size_t  mac_input_len = QD_NONCE_LEN + ct_len;
    uint8_t *mac_input    = malloc(mac_input_len);
    if (!mac_input) return QD_ERR_CRYPTO;
    memcpy(mac_input,                nonce, QD_NONCE_LEN);
    memcpy(mac_input + QD_NONCE_LEN, ct,    ct_len);

    uint8_t full_mac[32], expected_tag[QD_TAG_LEN];
    hmac_sha256(key, QD_KEY_LEN, mac_input, mac_input_len, full_mac);
    memcpy(expected_tag, full_mac, QD_TAG_LEN);
    free(mac_input);

    /* Sabit zamanlı karşılaştırma — timing saldırılarına karşı */
    uint8_t diff = 0;
    for (int i = 0; i < QD_TAG_LEN; i++)
        diff |= (tag[i] ^ expected_tag[i]);
    if (diff != 0) return QD_ERR_TAG_MISMATCH;

    /* XOR şifre çözme (encrypt ile özdeş — simetrik) */
    return fallback_encrypt(key, nonce, ct, ct_len, pt, (uint8_t[QD_TAG_LEN]){0});
}

#endif /* !HAVE_OPENSSL */

/* =========================================================================
 * OpenSSL ChaCha20-Poly1305
 * ========================================================================= */
#ifdef HAVE_OPENSSL

static int openssl_chacha20_poly1305_encrypt(const uint8_t *key,
                                              const uint8_t *nonce,
                                              const uint8_t *pt,   size_t pt_len,
                                              uint8_t       *ct,
                                              uint8_t       *tag)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return QD_ERR_CRYPTO;

    int ok = 1, outlen = 0;
    ok &= (EVP_EncryptInit_ex(ctx, EVP_chacha20_poly1305(), NULL, NULL, NULL) == 1);
    ok &= (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, QD_NONCE_LEN, NULL) == 1);
    ok &= (EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce) == 1);
    ok &= (EVP_EncryptUpdate(ctx, ct, &outlen, pt, (int)pt_len) == 1);
    int total = outlen;
    ok &= (EVP_EncryptFinal_ex(ctx, ct + total, &outlen) == 1);
    ok &= (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_GET_TAG, QD_TAG_LEN, tag) == 1);

    EVP_CIPHER_CTX_free(ctx);
    return ok ? QD_OK : QD_ERR_CRYPTO;
}

static int openssl_chacha20_poly1305_decrypt(const uint8_t *key,
                                              const uint8_t *nonce,
                                              const uint8_t *ct,   size_t ct_len,
                                              const uint8_t *tag,
                                              uint8_t       *pt)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return QD_ERR_CRYPTO;

    int ok = 1, outlen = 0;
    ok &= (EVP_DecryptInit_ex(ctx, EVP_chacha20_poly1305(), NULL, NULL, NULL) == 1);
    ok &= (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, QD_NONCE_LEN, NULL) == 1);
    ok &= (EVP_DecryptInit_ex(ctx, NULL, NULL, key, nonce) == 1);
    ok &= (EVP_DecryptUpdate(ctx, pt, &outlen, ct, (int)ct_len) == 1);
    ok &= (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_TAG,
                                QD_TAG_LEN, (void *)tag) == 1);
    int final_ok = EVP_DecryptFinal_ex(ctx, pt + outlen, &outlen);
    EVP_CIPHER_CTX_free(ctx);

    if (!ok || final_ok <= 0) return QD_ERR_TAG_MISMATCH;
    return QD_OK;
}

#endif /* HAVE_OPENSSL */

/* =========================================================================
 * Birleşik şifreleme / çözme — OpenSSL varsa kullan, yoksa fallback
 * ========================================================================= */
static int do_encrypt(const uint8_t *key, const uint8_t *nonce,
                      const uint8_t *pt, size_t pt_len,
                      uint8_t *ct, uint8_t *tag)
{
#ifdef HAVE_OPENSSL
    return openssl_chacha20_poly1305_encrypt(key, nonce, pt, pt_len, ct, tag);
#else
    /* ⚠️  GEÇİCİ fallback — üretimde KULLANMA */
    return fallback_encrypt(key, nonce, pt, pt_len, ct, tag);
#endif
}

static int do_decrypt(const uint8_t *key, const uint8_t *nonce,
                      const uint8_t *ct, size_t ct_len,
                      const uint8_t *tag, uint8_t *pt)
{
#ifdef HAVE_OPENSSL
    return openssl_chacha20_poly1305_decrypt(key, nonce, ct, ct_len, tag, pt);
#else
    /* ⚠️  GEÇİCİ fallback — üretimde KULLANMA */
    return fallback_decrypt(key, nonce, ct, ct_len, tag, pt);
#endif
}

/* =========================================================================
 * Blok ID üretimi: HMAC-SHA256(master_key, nonce || type)[0:4]
 * ========================================================================= */
static uint32_t compute_block_id(const uint8_t *master_key,
                                  const uint8_t *nonce,
                                  qd_block_type_t type)
{
    uint8_t input[QD_NONCE_LEN + 4];
    memcpy(input, nonce, QD_NONCE_LEN);
    input[QD_NONCE_LEN + 0] = (uint32_t)type >> 24;
    input[QD_NONCE_LEN + 1] = (uint32_t)type >> 16;
    input[QD_NONCE_LEN + 2] = (uint32_t)type >>  8;
    input[QD_NONCE_LEN + 3] = (uint32_t)type;

    uint8_t mac[32];
#ifdef HAVE_OPENSSL
    unsigned int mac_len = 32;
    HMAC(EVP_sha256(), master_key, QD_KEY_LEN, input, sizeof(input), mac, &mac_len);
#else
    hmac_sha256(master_key, QD_KEY_LEN, input, sizeof(input), mac);
#endif
    uint32_t id = ((uint32_t)mac[0] << 24) | ((uint32_t)mac[1] << 16)
                | ((uint32_t)mac[2] <<  8) |  (uint32_t)mac[3];
    return id ? id : 1; /* sıfırdan kaçın */
}

/* =========================================================================
 * Yardımcı: boş slot bul
 * ========================================================================= */
static int find_free_slot(qd_store_t *store)
{
    if (store->block_count >= QD_MAX_BLOCKS) return -1;
    for (int i = 0; i < QD_MAX_BLOCKS; i++) {
        if (store->blocks[i].id == 0) return i;
    }
    return -1;
}

/* =========================================================================
 * Public API
 * ========================================================================= */

int qd_init(qd_store_t *store,
            const char *device_fingerprint,
            const char *kovan_secret)
{
    if (!store || !device_fingerprint || !kovan_secret) return QD_ERR_NOT_INIT;

    memset(store, 0, sizeof(*store));
    pthread_mutex_init(&store->lock, NULL);

    /* Tuz: /dev/urandom ya da sabit (disk'ten yüklenirse üzerine yazılır) */
    if (read_urandom(store->salt, QD_SALT_LEN) != 0) {
        /* urandom başarısız — zaman + PID tabanlı fallback (ZAYIF) */
        uint64_t seed = (uint64_t)time(NULL) ^ ((uint64_t)getpid() << 32);
        for (int i = 0; i < QD_SALT_LEN; i++)
            store->salt[i] = (uint8_t)(seed >> (i % 8));
    }

    int rc = derive_master_key(device_fingerprint, kovan_secret,
                               store->salt, store->master_key);
    if (rc != QD_OK) return rc;

    store->key_initialized = 1;
    store->block_count     = 0;

    /* 🪰 [KUANTUM]: Toz deposu başlatıldı */
    fprintf(stderr, "🪰 [KUANTUM]: Depo başlatıldı — anahtar türetildi, "
                    "%d blok kapasitesi hazır\n", QD_MAX_BLOCKS);
    return QD_OK;
}

int qd_seal(qd_store_t      *store,
            qd_block_type_t  type,
            const uint8_t   *plaintext,
            size_t           len,
            uint32_t        *out_id)
{
    if (!store || !store->key_initialized || !plaintext || !out_id)
        return QD_ERR_NOT_INIT;
    if (len > QD_BLOCK_SIZE) return QD_ERR_TOO_LARGE;

    pthread_mutex_lock(&store->lock);

    int slot = find_free_slot(store);
    if (slot < 0) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_STORE_FULL;
    }

    qd_block_t *blk = &store->blocks[slot];
    memset(blk, 0, sizeof(*blk));

    /* Nonce: /dev/urandom */
#ifdef HAVE_OPENSSL
    if (RAND_bytes(blk->nonce, QD_NONCE_LEN) != 1) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_CRYPTO;
    }
#else
    if (read_urandom(blk->nonce, QD_NONCE_LEN) != 0) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_CRYPTO;
    }
#endif

    int rc = do_encrypt(store->master_key, blk->nonce,
                        plaintext, len,
                        blk->ciphertext, blk->tag);
    if (rc != QD_OK) {
        pthread_mutex_unlock(&store->lock);
        return rc;
    }

    blk->id             = compute_block_id(store->master_key, blk->nonce, type);
    blk->type           = type;
    blk->ciphertext_len = len;
    *out_id             = blk->id;
    store->block_count++;

    /* 🪰 [KUANTUM]: Toz mühürlendi */
    fprintf(stderr,
            "🪰 [KUANTUM]: Toz mühürlendi (id=%u, tip=%d, gürültü=%zu byte)\n",
            blk->id, (int)type, len);

    pthread_mutex_unlock(&store->lock);
    return QD_OK;
}

/* Dahili: kilitsiz blok arama */
static qd_block_t *_find_block_nolock(qd_store_t *store, uint32_t block_id)
{
    for (int i = 0; i < QD_MAX_BLOCKS; i++) {
        if (store->blocks[i].id == block_id) return &store->blocks[i];
    }
    return NULL;
}

qd_block_t *qd_find_block(qd_store_t *store, uint32_t block_id)
{
    pthread_mutex_lock(&store->lock);
    qd_block_t *b = _find_block_nolock(store, block_id);
    pthread_mutex_unlock(&store->lock);
    return b;
}

qd_block_t *qd_find_by_type(qd_store_t *store, qd_block_type_t type)
{
    pthread_mutex_lock(&store->lock);
    qd_block_t *result = NULL;
    for (int i = 0; i < QD_MAX_BLOCKS; i++) {
        if (store->blocks[i].id != 0 && store->blocks[i].type == type) {
            result = &store->blocks[i];
            break;
        }
    }
    pthread_mutex_unlock(&store->lock);
    return result;
}

int qd_collapse(qd_store_t *store,
                uint32_t    block_id,
                uint8_t    *out_buf,
                size_t      buf_len,
                size_t     *out_len)
{
    if (!store || !store->key_initialized || !out_buf || !out_len)
        return QD_ERR_NOT_INIT;

    pthread_mutex_lock(&store->lock);

    qd_block_t *blk = _find_block_nolock(store, block_id);
    if (!blk) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_NOT_FOUND;
    }
    if (buf_len < blk->ciphertext_len) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_BUF_TOO_SMALL;
    }

    int rc = do_decrypt(store->master_key, blk->nonce,
                        blk->ciphertext, blk->ciphertext_len,
                        blk->tag, out_buf);
    if (rc == QD_ERR_TAG_MISMATCH) {
        /* ❌ Gözlemci reddedildi */
        fprintf(stderr,
                "❌ [KUANTUM]: Gözlemci reddedildi (tag mismatch, id=%u)\n",
                block_id);
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_TAG_MISMATCH;
    }
    if (rc != QD_OK) {
        pthread_mutex_unlock(&store->lock);
        return rc;
    }

    *out_len = blk->ciphertext_len;

    /* 🪰 [KUANTUM]: Toz çöktü */
    fprintf(stderr,
            "🪰 [KUANTUM]: Toz çöktü (id=%u, plaintext=%zu byte)\n",
            block_id, *out_len);

    pthread_mutex_unlock(&store->lock);
    return QD_OK;
}

int qd_evolve(qd_store_t    *store,
              uint32_t       block_id,
              const uint8_t *new_data,
              size_t         len)
{
    /*
     * 🪰 [KUANTUM]: Süperpozisyon evrimi.
     * Gürültü tamamen değişir (yeni nonce → yeni ciphertext),
     * blok kimliği sabit kalır.
     */
    if (!store || !store->key_initialized || !new_data) return QD_ERR_NOT_INIT;
    if (len > QD_BLOCK_SIZE) return QD_ERR_TOO_LARGE;

    pthread_mutex_lock(&store->lock);

    qd_block_t *blk = _find_block_nolock(store, block_id);
    if (!blk) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_NOT_FOUND;
    }

    uint8_t new_nonce[QD_NONCE_LEN];
#ifdef HAVE_OPENSSL
    if (RAND_bytes(new_nonce, QD_NONCE_LEN) != 1) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_CRYPTO;
    }
#else
    if (read_urandom(new_nonce, QD_NONCE_LEN) != 0) {
        pthread_mutex_unlock(&store->lock);
        return QD_ERR_CRYPTO;
    }
#endif

    uint8_t  new_ct[QD_BLOCK_SIZE];
    uint8_t  new_tag[QD_TAG_LEN];
    int rc = do_encrypt(store->master_key, new_nonce, new_data, len,
                        new_ct, new_tag);
    if (rc != QD_OK) {
        pthread_mutex_unlock(&store->lock);
        return rc;
    }

    memcpy(blk->nonce,      new_nonce, QD_NONCE_LEN);
    memcpy(blk->tag,        new_tag,   QD_TAG_LEN);
    memcpy(blk->ciphertext, new_ct,    len);
    blk->ciphertext_len = len;
    /* ID değişmez — süperpozisyon korunur */

    fprintf(stderr,
            "🪰 [KUANTUM]: Toz evrildi (id=%u, yeni gürültü=%zu byte)\n",
            block_id, len);

    pthread_mutex_unlock(&store->lock);
    return QD_OK;
}

void qd_purge(qd_store_t *store, uint32_t block_id)
{
    pthread_mutex_lock(&store->lock);
    for (int i = 0; i < QD_MAX_BLOCKS; i++) {
        if (store->blocks[i].id == block_id) {
            /* Güvenli sıfırlama — derleme optimizasyonu engellenmiş */
            volatile uint8_t *p = (volatile uint8_t *)&store->blocks[i];
            for (size_t j = 0; j < sizeof(qd_block_t); j++) p[j] = 0;
            store->block_count--;
            fprintf(stderr,
                    "🪰 [KUANTUM]: Toz silindi (id=%u)\n", block_id);
            break;
        }
    }
    pthread_mutex_unlock(&store->lock);
}

void qd_destroy(qd_store_t *store)
{
    pthread_mutex_lock(&store->lock);
    volatile uint8_t *p = (volatile uint8_t *)store;
    for (size_t i = 0; i < sizeof(qd_store_t); i++) p[i] = 0;
    pthread_mutex_unlock(&store->lock);
    pthread_mutex_destroy(&store->lock);
    fprintf(stderr, "🪰 [KUANTUM]: Toz deposu yok edildi — tüm gürültü silindi\n");
}

int qd_save_disk(qd_store_t *store, const char *path)
{
    /*
     * Dosya içeriği zaten ciphertext — ekstra şifrelemeye gerek yok,
     * ama dosya izinleri 0600 olmalı (sadece sahip okuyabilir).
     */
    if (!store || !path) return QD_ERR_IO;

    pthread_mutex_lock(&store->lock);

    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0600);
    if (fd < 0) {
        pthread_mutex_unlock(&store->lock);
        fprintf(stderr, "❌ [KUANTUM]: Disk yazma başarısız: %s\n", strerror(errno));
        return QD_ERR_IO;
    }

    /* Önce tuzu kaydet (anahtar türetimi için gerekli) */
    ssize_t n = write(fd, store->salt, QD_SALT_LEN);
    if (n != QD_SALT_LEN) { close(fd); pthread_mutex_unlock(&store->lock); return QD_ERR_IO; }

    /* block_count */
    int32_t bc = store->block_count;
    n = write(fd, &bc, sizeof(bc));
    if (n != sizeof(bc)) { close(fd); pthread_mutex_unlock(&store->lock); return QD_ERR_IO; }

    /* Tüm blok dizisi */
    ssize_t expected = (ssize_t)(sizeof(qd_block_t) * QD_MAX_BLOCKS);
    n = write(fd, store->blocks, (size_t)expected);
    if (n != expected) { close(fd); pthread_mutex_unlock(&store->lock); return QD_ERR_IO; }

    close(fd);
    pthread_mutex_unlock(&store->lock);

    fprintf(stderr,
            "🪰 [KUANTUM]: Toz diske yazıldı: %s (%d blok)\n",
            path, bc);
    return QD_OK;
}

int qd_load_disk(qd_store_t *store, const char *path)
{
    if (!store || !path) return QD_ERR_IO;

    pthread_mutex_lock(&store->lock);

    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        pthread_mutex_unlock(&store->lock);
        fprintf(stderr, "❌ [KUANTUM]: Disk okuma başarısız: %s\n", strerror(errno));
        return QD_ERR_IO;
    }

    ssize_t n = read(fd, store->salt, QD_SALT_LEN);
    if (n != QD_SALT_LEN) { close(fd); pthread_mutex_unlock(&store->lock); return QD_ERR_IO; }

    int32_t bc;
    n = read(fd, &bc, sizeof(bc));
    if (n != sizeof(bc)) { close(fd); pthread_mutex_unlock(&store->lock); return QD_ERR_IO; }
    store->block_count = bc;

    ssize_t expected = (ssize_t)(sizeof(qd_block_t) * QD_MAX_BLOCKS);
    n = read(fd, store->blocks, (size_t)expected);
    if (n != expected) { close(fd); pthread_mutex_unlock(&store->lock); return QD_ERR_IO; }

    close(fd);
    pthread_mutex_unlock(&store->lock);

    fprintf(stderr,
            "🪰 [KUANTUM]: Toz diskten yüklendi: %s (%d blok)\n",
            path, bc);
    return QD_OK;
}

int qd_count_by_type(qd_store_t *store, qd_block_type_t type)
{
    if (!store) return 0;
    pthread_mutex_lock(&store->lock);
    int count = 0;
    for (int i = 0; i < QD_MAX_BLOCKS; i++) {
        if (store->blocks[i].id != 0 && store->blocks[i].type == type)
            count++;
    }
    pthread_mutex_unlock(&store->lock);
    return count;
}

size_t qd_total_noise_bytes(qd_store_t *store)
{
    /* "Sinek şu an X byte kuantum tozu taşıyor." */
    if (!store) return 0;
    pthread_mutex_lock(&store->lock);
    size_t total = 0;
    for (int i = 0; i < QD_MAX_BLOCKS; i++) {
        if (store->blocks[i].id != 0)
            total += store->blocks[i].ciphertext_len;
    }
    pthread_mutex_unlock(&store->lock);
    return total;
}
