// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (QUANTUM FINAL + TOUCH INTEGRATED)
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
#include <signal.h>
#include <string.h>

// Motorlar ve Donanım Katmanı
#include "anka_env.h"      // Termux python3 bridge (sh bypass)
#include "quantum/quantum_dust.h"
extern void collapse_shutdown(void);
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "ui_engine.h"     // fb_context_t, fb_open, fb_close
#include "anim_engine.h"   // anim_boot_run
#include "anka_hal.h"      // AnkaHAL tipi
#include "engines/tohum_engine.h" // SPRINT 3: tohum→filizlen→büzül döngüsü
#include "touch_engine.h"  // GERÇEK DOKUNMATİK SENSÖR MOTORU

// --- HAL MOCK ---
AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL };

extern void ui_render(const char *last_message);

// --- GLOBAL: çalışan ANKA OS durumu (sinyal handler için) ---
static volatile sig_atomic_t g_running = 1;

// --- SİNYAL HANDLER: SIGINT (Ctrl-C) → temiz kapanış ---
static void sigint_handler(int sig)
{
    (void)sig;
    g_running = 0;
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGINT alındı — temiz kapanış başlıyor...\n");
}

// --- SİNYAL HANDLER: SIGTERM (kill) → temiz kapanış ---
static void sigterm_handler(int sig)
{
    (void)sig;
    g_running = 0;
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGTERM alındı — kapanıyor...\n");
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    // 0. SİNYAL HANDLER KURULUMU
    struct sigaction sa_int;
    memset(&sa_int, 0, sizeof(sa_int));
    sa_int.sa_handler = sigint_handler;
    sigemptyset(&sa_int.sa_mask);
    sa_int.sa_flags = 0;
    sigaction(SIGINT, &sa_int, NULL);

    struct sigaction sa_term;
    memset(&sa_term, 0, sizeof(sa_term));
    sa_term.sa_handler = sigterm_handler;
    sigemptyset(&sa_term.sa_mask);
    sa_term.sa_flags = 0;
    sigaction(SIGTERM, &sa_term, NULL);

    // SIGPIPE'i yoksay (python3 alt processte pipe kırılırsa crash olmasın)
    signal(SIGPIPE, SIG_IGN);

    // 1. GÖLGE KATMAN BAŞLATMA (Animasyon Motoru İçin)
    fb_context_t fb;
    if (fb_open(&fb) == 0) {
        // Uyanış sekansını çalıştır
        anim_boot_run(&fb, &g_hal);
        fb_close(&fb);
    } else {
        fprintf(stderr, "⚠️ [GÖLGE]: Framebuffer açılamadı, animasyon atlanıyor.\n");
    }

    printf("\033[1;36m --- ANKA OS: QUANTUM UYANIŞ --- \033[0m\n");

    // 1.5. GERÇEK DOKUNMATİK SENSÖRÜ BAŞLAT (/dev/input/event4)
    if (init_touch() < 0) {
        fprintf(stderr, "⚠️ [DOKUNMATİK]: Sensör başlatılamadı, dokunmatik girdiler pasif.\n");
    }

    // 2. Kuantum motorunu yükle
    void *lib = dlopen("./core/quantum/libanka_quantum.so", RTLD_LAZY);
    if (!lib) {
        fprintf(stderr, "❌ [HATA]: Kuantum motoru yüklenemedi: %s\n", dlerror());
        close_touch();
        return -1;
    }

    // 3. Depo ve Motor Başlatma
    static qd_store_t dust;
    qd_init(&dust, "Note9_Merlin_FP", "KovanSecret_v1");
    collapse_init(&dust, &g_hal);

    // SPRINT 3: Tohum Motoru — Güç tuşu yaşam döngüsü
    static tohum_ctx_t tohum;
    tohum_init(&tohum);
    tohum_skill_ekle(&tohum, "kisilik_motoru");
    tohum_skill_ekle(&tohum, "jammer_surfer");
    tohum_skill_ekle(&tohum, "kuantum_gozlemci");
    tohum_skill_ekle(&tohum, "kovan_zihni");

    // Güç tuşu → Anka uyanır → pencereler + skill'ler açılır
    tohum_guc_tusu(&tohum);

    // 4. Sinek (FSM) Uyanışı
    static sinek_fsm_t sinek;
    sinek_fsm_init(&sinek, &dust, &g_hal);

    // Sinek'i uyanmaya zorla
    sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, NULL, 0);

    // 5. Kovan ve Ağ — TERMUX PYTHON3 (sh bypass!)
    int py_rc = anka_run_python_bg("agents/sinek_nexus.py", NULL);
    if (py_rc < 0) {
        fprintf(stderr,
                "⚠️ [SİNEK]: Python3 (sinek_nexus.py) başlatılamadı — "
                "yerel modda devam ediliyor.\n");
        sinek_fsm_handle_event(&sinek, SINEK_EVT_OFFLINE, NULL, 0);
    } else {
        fprintf(stderr, "🪰 [SİNEK]: sinek_nexus.py arka planda çalışıyor.\n");
    }

    printf("🎙️ [SİSTEM]: Anka OS Aktif, Kuantum Nabız ve Dokunmatik Dinleme Başlatıldı.\n");

    // 6. YÜKSEK HIZLI NABIZ VE DOKUNMATİK DÖNGÜSÜ
    int touch_x = 0, touch_y = 0;
    while (g_running) {
        // 1. Gerçek Dokunmatik Girdilerini Kontrol Et
        if (get_touch_event(&touch_x, &touch_y)) {
            fprintf(stderr, "👆 [DOKUNMA TESPİT EDİLDİ]: X=%d, Y=%d\n", touch_x, touch_y);
            // Sinek dokunmaya karşı uyandırıcı/tepkisel FSM olayını tetikler
            sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, &touch_x, sizeof(touch_x));
        }

        // 2. Kuantum Nabzı (Arka plan zekası)
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        sinek_fsm_uptime_update(&sinek);

        // 3. ARAYÜZÜ EKRANA BAS
        ui_render("Sistem Senkronize... Dokunmatik Dinleniyor.");

        usleep(50000); // 50ms döngü hızı (dokunmatik tepki süresi optimize edildi)
    }

    // 7. TEMİZ KAPANIŞ
    fprintf(stderr, "🪰 [SİSTEM]: Kapanış — FSM ve motorlar temizleniyor...\n");
    close_touch(); // Dokunmatik kaynaklarını serbest bırak
    collapse_shutdown();
    sinek_fsm_destroy(&sinek);

    if (lib) {
        dlclose(lib);
        fprintf(stderr, "🪰 [SİSTEM]: Kuantum motoru (.so) kaldırıldı.\n");
    }

    fprintf(stderr, "🪰 [SİSTEM]: ANKA OS kapatıldı. Hoşça kal sinek.\n");
    return 0;
}
