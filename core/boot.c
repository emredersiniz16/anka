// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (QUANTUM FINAL)
// DÜZELTME v5: hal_loader_init() çağrısı eklendi — backend'ler artık yükleniyor.
//               Kapanışta Python çocuğu killpg ile öldürülüyor.
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
#include <signal.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/types.h>

// Motorlar ve Donanım Katmanı
#include "anka_env.h"      // Native Python3 bridge (fork+execvp, sh bypass)
#include "quantum/quantum_dust.h"
extern void collapse_shutdown(void);
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "ui_engine.h"     // fb_context_t, fb_open, fb_close
#include "anim_engine.h"   // anim_boot_run
#include "anka_hal.h"      // AnkaHAL tipi
#include "hal_common.h"    // hal_backend_t, ANKA_HAL_ABI_VERSION
#include "engines/tohum_engine.h"

// --- HAL MOCK (fallback — backend bulunamazsa) ---
AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL };

// hal_loader.c'den geliyor — backend bulursa gerçek HAL döner
extern AnkaHAL *current_hal;
extern void hal_loader_init(void);

extern void ui_render(const char *last_message);

// --- GLOBAL: çalışan ANKA OS durumu ---
static volatile sig_atomic_t g_running = 1;

// --- Python çocuğun PID'si (kapanışta öldürmek için) ---
static pid_t g_python_pid = -1;

// --- SİNYAL HANDLER: SIGINT/SIGTERM → temiz kapanış ---
static void sigint_handler(int sig)
{
    (void)sig;
    g_running = 0;
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGINT alındı — temiz kapanış başlıyor...\n");
}

static void sigterm_handler(int sig)
{
    (void)sig;
    g_running = 0;
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGTERM alındı — kapanıyor...\n");
}

// --- Python çocuğunu güvenli şekilde öldür ---
static void kill_python_child(void)
{
    if (g_python_pid > 0) {
        fprintf(stderr, "🪰 [SİSTEM]: Python ajanı (PID=%d) sonlandırılıyor...\n", g_python_pid);
        // Önce SIGTERM dene (temiz kapanış şansı)
        kill(g_python_pid, SIGTERM);
        // 2 sn bekle, hâlâ ayaktaysa SIGKILL
        sleep(2);
        if (kill(g_python_pid, 0) == 0) {
            fprintf(stderr, "⚠️ [SİSTEM]: Python hâlâ ayakta, SIGKILL gönderiliyor\n");
            kill(g_python_pid, SIGKILL);
            waitpid(g_python_pid, NULL, 0);
        } else {
            waitpid(g_python_pid, NULL, WNOHANG);
        }
        g_python_pid = -1;
    }
    // Ek guarantee: pkill ile tüm sinek python süreçlerini temizle
    system("pkill -f 'python3.*sinek' 2>/dev/null");
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

    signal(SIGPIPE, SIG_IGN);

    // 1. GÖLGE KATMAN BAŞLATMA (Animasyon Motoru)
    fb_context_t fb;
    if (fb_open(&fb) == 0) {
        anim_boot_run(&fb, &g_hal);
        fb_close(&fb);
    } else {
        fprintf(stderr, "⚠️ [GÖLGE]: Framebuffer açılamadı, animasyon atlanıyor.\n");
    }

    printf("\033[1;36m --- ANKA OS: QUANTUM UYANIŞ --- \033[0m\n");

    // 1.5 HAL BACKEND YÜKLEME — cihaza özel sürücüleri dlopen ile bul
    //     (backend_legacy_qualcomm_msm.c → Note 9 titreşim/parlaklık/kamera)
    hal_loader_init();
    AnkaHAL *active_hal = current_hal;
    if (!active_hal) {
        fprintf(stderr, "⚠️ [HAL]: Backend bulunamadı, mock HAL kullanılıyor\n");
        active_hal = &g_hal;
    } else {
        fprintf(stderr, "🪰 [HAL]: Donanım backend'i yüklendi\n");
    }

    // 2. Kuantum motorunu yükle
    const char *lib_path = getenv("ANKA_LIB_PATH");
    if (!lib_path) {
        lib_path = "/data/adb/modules/anka_os/system/lib/libanka_quantum.so";
    }
    void *lib = dlopen(lib_path, RTLD_LAZY);
    
    if (!lib) {
        lib = dlopen("./core/quantum/libanka_quantum.so", RTLD_LAZY);
    }

    if (!lib) {
        fprintf(stderr, "❌ [HATA]: Kuantum motoru yüklenemedi: %s\n", dlerror());
        return -1;
    }

    // 3. Depo ve Motor Başlatma — aktif HAL ile
    static qd_store_t dust;
    qd_init(&dust, "Note9_Merlin_FP", "KovanSecret_v1");
    collapse_init(&dust, active_hal);

    // Tohum Motoru
    static tohum_ctx_t tohum;
    tohum_init(&tohum);
    tohum_skill_ekle(&tohum, "kisilik_motoru");
    tohum_skill_ekle(&tohum, "jammer_surfer");
    tohum_skill_ekle(&tohum, "kuantum_gozlemci");
    tohum_skill_ekle(&tohum, "kovan_zihni");
    tohum_guc_tusu(&tohum);

    // 4. Sinek (FSM) Uyanışı — aktif HAL ile
    static sinek_fsm_t sinek;
    sinek_fsm_init(&sinek, &dust, active_hal);
    sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, NULL, 0);

    // 5. Kovan ve Ağ — NATIVE PYTHON3 (sh bypass!)
    int py_rc = anka_run_python_bg(
        "/data/adb/modules/anka_os/system/anka_core/agents/sinek_nexus.py", NULL);
    if (py_rc < 0) {
        fprintf(stderr, "⚠️ [SİNEK]: Python3 başlatılamadı — yerel modda devam.\n");
        sinek_fsm_handle_event(&sinek, SINEK_EVT_OFFLINE, NULL, 0);
    } else {
        // Python PID'yi sakla (kapanışta öldürmek için)
        g_python_pid = (pid_t)py_rc;
        fprintf(stderr, "🪰 [SİNEK]: sinek_nexus.py arka planda çalışıyor (PID=%d).\n", g_python_pid);
    }

    printf("🎙️ [SİSTEM]: Anka OS Aktif, Kuantum Nabız Başlatıldı.\n");

    // 6. YÜKSEK HIZLI NABIZ DÖNGÜSÜ
    while (g_running) {
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        sinek_fsm_uptime_update(&sinek);
        ui_render("Sistem Senkronize... Kovan Dinleniyor.");
        usleep(500000);
    }

    // 7. TEMİZ KAPANIŞ — Python çocuğunu da öldür
    fprintf(stderr, "🪰 [SİSTEM]: Kapanış — motorlar temizleniyor...\n");
    collapse_shutdown();
    sinek_fsm_destroy(&sinek);
    kill_python_child();

    if (lib) {
        dlclose(lib);
        fprintf(stderr, "🪰 [SİSTEM]: Kuantum motoru (.so) kaldırıldı.\n");
    }

    fprintf(stderr, "🪰 [SİSTEM]: ANKA OS kapatıldı. Hoşça kal sinek.\n");
    return 0;
}
