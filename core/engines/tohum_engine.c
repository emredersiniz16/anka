/* core/engines/tohum_engine.c
 * Anka OS — SPRINT 3 — Güç Tuşu Yaşam Döngüsü
 *
 * Döngü:
 *   TOHUM  ──(güç tuşu)──► FİLİZLEN  ──(görev bitti)──► BÜZÜL ──► TOHUM
 *
 * FİLİZLEN aşamasında:
 *   • Aktif pencereler (work window) terminale overlay olarak basılır.
 *   • Kayıtlı skill'ler listelenir (HAL v2 UI engine uyumlu).
 *
 * BÜZÜL aşamasında:
 *   • Tüm pencereler tek tek "küçülüp" kaybolur.
 *   • Anka TOHUM moduna döner ve güç tuşunu bekler.
 */

#include "tohum_engine.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* =========================================================================
 * Yardımcı: Renkli çerçeve çiz
 * ========================================================================= */
static void pencere_ciz(const char *baslik, const char *icerik)
{
    printf("\033[1;35m┌─────────────────────────────────┐\033[0m\n");
    printf("\033[1;35m│\033[1;37m %-31s \033[1;35m│\033[0m\n", baslik);
    printf("\033[1;35m├─────────────────────────────────┤\033[0m\n");
    printf("\033[1;35m│\033[0m %-33s\033[1;35m│\033[0m\n", icerik);
    printf("\033[1;35m└─────────────────────────────────┘\033[0m\n");
}

/* =========================================================================
 * tohum_init — Bağlamı sıfırla, TOHUM moduna al
 * ========================================================================= */
void tohum_init(tohum_ctx_t *ctx)
{
    if (!ctx) return;
    memset(ctx, 0, sizeof(*ctx));
    ctx->durum       = TOHUM;
    ctx->pencere_acik = 0;
    printf("🌱 [TOHUM]: Anka uyku modunda. Güç tuşunu bekliyorum...\n");
}

/* =========================================================================
 * tohum_skill_ekle — Yeni bir skill kaydet (filizlenince gösterilir)
 * ========================================================================= */
void tohum_skill_ekle(tohum_ctx_t *ctx, const char *isim)
{
    if (!ctx || !isim) return;
    if (ctx->skill_sayisi >= TOHUM_MAX_SKILL) {
        printf("⚠️  [TOHUM]: Skill slotu dolu (%d/%d).\n",
               ctx->skill_sayisi, TOHUM_MAX_SKILL);
        return;
    }
    anka_skill_t *s = &ctx->skill_ler[ctx->skill_sayisi++];
    snprintf(s->isim,  sizeof(s->isim),  "%s", isim);
    snprintf(s->durum, sizeof(s->durum), "HAZIR");
    printf("🌱 [TOHUM]: Skill eklendi → %s\n", isim);
}

/* =========================================================================
 * filizlen_aksiyon — FİLİZLEN safhasında çalışır
 * ========================================================================= */
static void filizlen_aksiyon(tohum_ctx_t *ctx)
{
    printf("\n\033[1;32m🌿 [FİLİZLEN]: Anka uyanıyor...\033[0m\n\n");
    usleep(300000);

    /* Work pencereleri aç */
    pencere_ciz("WORK: Kovan Ağı",         "● Kovan bağlantısı: AKTIF     ");
    usleep(150000);
    pencere_ciz("WORK: HAL v2 Sensörler",  "● Donanım köprüsü: HAZIR      ");
    usleep(150000);
    pencere_ciz("WORK: Kuantum Motoru",    "● Collapse engine: ÇALIŞIYOR  ");
    usleep(150000);

    /* Skill overlay */
    if (ctx->skill_sayisi > 0) {
        printf("\n\033[1;36m══ SKİLL OVERLAY ══\033[0m\n");
        for (int i = 0; i < ctx->skill_sayisi; i++) {
            printf("  \033[1;33m[%d]\033[0m %-24s → \033[1;32m%s\033[0m\n",
                   i + 1,
                   ctx->skill_ler[i].isim,
                   ctx->skill_ler[i].durum);
            ctx->skill_ler[i].durum[0] = '\0'; /* "AKTIF" yap */
            snprintf(ctx->skill_ler[i].durum, sizeof(ctx->skill_ler[i].durum), "AKTİF");
            usleep(80000);
        }
        printf("\033[1;36m═══════════════════\033[0m\n\n");
    }

    ctx->pencere_acik = 1;
    printf("🌿 [FİLİZLEN]: Tüm pencereler açık. Anka hazır.\n\n");
}

/* =========================================================================
 * buzul_aksiyon — BÜZÜL safhasında çalışır
 * ========================================================================= */
static void buzul_aksiyon(tohum_ctx_t *ctx)
{
    printf("\n\033[1;34m🍂 [BÜZÜL]: Görev tamamlandı — pencereler kapanıyor...\033[0m\n");
    usleep(200000);

    /* Skill'leri kapat */
    for (int i = ctx->skill_sayisi - 1; i >= 0; i--) {
        printf("  \033[1;31m[KAPAT]\033[0m %s\n", ctx->skill_ler[i].isim);
        snprintf(ctx->skill_ler[i].durum, sizeof(ctx->skill_ler[i].durum), "HAZIR");
        usleep(100000);
    }

    /* Work pencereleri büzüştür */
    const char *pencereler[] = {
        "WORK: Kuantum Motoru",
        "WORK: HAL v2 Sensörler",
        "WORK: Kovan Ağı"
    };
    for (int i = 0; i < 3; i++) {
        printf("  \033[1;31m[BÜZÜL ▼]\033[0m %s\n", pencereler[i]);
        usleep(120000);
    }

    ctx->pencere_acik = 0;
    printf("🍂 [BÜZÜL]: Tüm pencereler kapandı.\n\n");
}

/* =========================================================================
 * tohum_guc_tusu — Güç tuşu olayı
 *   • TOHUM    → FİLİZLEN  (uyanış)
 *   • FİLİZLEN → BÜZÜL → TOHUM  (tekrar basınca kapat)
 * ========================================================================= */
void tohum_guc_tusu(tohum_ctx_t *ctx)
{
    if (!ctx) return;

    switch (ctx->durum) {
        case TOHUM:
            ctx->durum = FILIZLEN;
            filizlen_aksiyon(ctx);
            break;

        case FILIZLEN:
            ctx->durum = BUZUL;
            buzul_aksiyon(ctx);
            ctx->durum = TOHUM;
            printf("🌱 [TOHUM]: Anka tekrar uyku modunda.\n\n");
            break;

        case BUZUL:
            /* Büzülme sürerken ikinci tuş: yoksay */
            printf("⚠️  [TOHUM]: Büzülme devam ediyor, lütfen bekleyin...\n");
            break;
    }
}

/* =========================================================================
 * tohum_gorev_bitti — Görev tamamlandı sinyali (programatik)
 * ========================================================================= */
void tohum_gorev_bitti(tohum_ctx_t *ctx)
{
    if (!ctx) return;

    if (ctx->durum != FILIZLEN) {
        printf("⚠️  [TOHUM]: Aktif görev yok.\n");
        return;
    }

    ctx->durum = BUZUL;
    buzul_aksiyon(ctx);
    ctx->durum = TOHUM;
    printf("🌱 [TOHUM]: Anka uyku moduna döndü.\n\n");
}

/* =========================================================================
 * tohum_durum_yazdir — Debug / loglama
 * ========================================================================= */
void tohum_durum_yazdir(const tohum_ctx_t *ctx)
{
    if (!ctx) return;

    static const char *durum_adi[] = { "TOHUM", "FİLİZLEN", "BÜZÜL" };
    printf("🌱 [TOHUM DURUM]: %s | Pencere: %s | Skill: %d/%d\n",
           durum_adi[ctx->durum],
           ctx->pencere_acik ? "AÇIK" : "KAPALI",
           ctx->skill_sayisi,
           TOHUM_MAX_SKILL);
}
