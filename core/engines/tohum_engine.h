#ifndef TOHUM_ENGINE_H
#define TOHUM_ENGINE_H

/* core/engines/tohum_engine.h
 * Anka OS — SPRINT 3 — Güç Tuşu Yaşam Döngüsü
 *
 * TOHUM  → Anka uyku halinde, güç tuşunu bekler
 * FİLİZLEN → Güç tuşuna basıldı: Anka uyanır, pencereler + skill'ler açılır
 * BÜZÜL  → Görev bitti: pencereler kapanır, Anka TOHUM'a döner
 */

#ifdef __cplusplus
extern "C" {
#endif

/* Yaşam döngüsü durumları */
typedef enum {
    TOHUM    = 0,  /* Uyku / bekleme */
    FILIZLEN = 1,  /* Uyanış / aktif pencereler */
    BUZUL    = 2   /* Büzülme / kapanış */
} tohum_durum_t;

/* Skill kaydı (pencere açıldığında gösterilecek) */
#define TOHUM_MAX_SKILL 8

typedef struct {
    char isim[64];
    char durum[32];
} anka_skill_t;

/* Ana bağlam */
typedef struct {
    tohum_durum_t durum;
    anka_skill_t  skill_ler[TOHUM_MAX_SKILL];
    int           skill_sayisi;
    int           pencere_acik;
} tohum_ctx_t;

/* API */
void tohum_init(tohum_ctx_t *ctx);
void tohum_skill_ekle(tohum_ctx_t *ctx, const char *isim);
void tohum_guc_tusu(tohum_ctx_t *ctx);   /* Güç tuşu → FİLİZLEN veya BÜZÜL */
void tohum_gorev_bitti(tohum_ctx_t *ctx); /* Görev tamamlandı → BÜZÜL → TOHUM */
void tohum_durum_yazdir(const tohum_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* TOHUM_ENGINE_H */
