// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (TAKTIKSEL SAVAŞ VE KUM HAVUZU MODU)
// DÜZELTME v9: Sinek ekranı çökertmeden, SIGSTOP ile dondurarak bilek hakkıyla alır.
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
#include <signal.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/types.h>

#include "anka_env.h"
#include "quantum/quantum_dust.h"
extern void collapse_shutdown(void);
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "ui_engine.h"
#include "anim_engine.h"
#include "anka_hal.h"
#include "hal_common.h"
#include "engines/tohum_engine.h"

// Savaş Modülü Başlıkları (Sinek'in Kum Havuzu Zekası)
extern int sinek_execute_takeover(void);
extern void sinek_retreat(pid_t sf_pid);

AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL };
extern AnkaHAL *current_hal;
extern void hal_loader_init(void);

/* Güncellenen ui_render prototipi */
extern void ui_render(fb_context_t *fb, const char *last_message);

static volatile sig_atomic_t g_running = 1;
static pid_t g_python_pid = -1;
static pid_t g_frozen_sf_pid = -1; // Donmuş MIUI'ın PID'si

static void sigint_handler(int sig) { 
    (void)sig; 
    g_running = 0; 
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGINT — güvenli kapanış...\n"); 
}

static void sigterm_handler(int sig) { 
    (void)sig; 
    g_running = 0; 
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGTERM — güvenli kapanış...\n"); 
}

static void kill_python_child(void)
{
    if (g_python_pid > 0) {
        fprintf(stderr, "🪰 [SİSTEM]: Python ajanı (PID=%d) sonlandırılıyor...\n", g_python_pid);
        kill(g_python_pid, SIGTERM);
        sleep(2);
        if (kill(g_python_pid, 0) == 0) {
            kill(g_python_pid, SIGKILL);
            waitpid(g_python_pid, NULL, 0);
        } else {
            waitpid(g_python_pid, NULL, WNOHANG);
        }
        g_python_pid = -1;
    }
    system("pkill -f 'python3.*sinek' 2>/dev/null");
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    struct sigaction sa_int = {0}; sa_int.sa_handler = sigint_handler; sigemptyset(&sa_int.sa_mask); sigaction(SIGINT, &sa_int, NULL);
    struct sigaction sa_term = {0}; sa_term.sa_handler = sigterm_handler; sigemptyset(&sa_term.sa_mask); sigaction(SIGTERM, &sa_term, NULL);
    signal(SIGPIPE, SIG_IGN);

    printf("\033[1;36m --- ANKA OS: SİNEK TAKTİKSEL UYANIŞ --- \033[0m\n");

    // 0. SİNEK SAVAŞA BAŞLAR: Kum Havuzunda test eder, sistemi dondurur.
    // Artık cihaz çökmeyecek, çünkü Sinek sadece MIUI'ı uyutuyor.
    g_frozen_sf_pid = sinek_execute_takeover();

    // 1. FRAMEBUFFER AÇILIŞI VE BOOT SEKANSI
    fb_context_t fb;
    int fb_is_open = (fb_open(&fb) == 0);
    if (fb_is_open) { 
        anim_boot_run(&fb, &g_hal); 
    } else { 
        fprintf(stderr, "⚠️ [GÖLGE]: Framebuffer açılamadı, kör uçuş!\n"); 
    }

    // 1.5 HAL BACKEND YÜKLEME
    hal_loader_init();
    AnkaHAL *active_hal = current_hal;
    if (!active_hal) { fprintf(stderr, "⚠️ [HAL]: Backend yok, mock kullanılıyor\n"); active_hal = &g_hal; }
    else fprintf(stderr, "🪰 [HAL]: Donanım backend'i yüklendi\n");

    // 2. Kuantum motorunu yükle
    const char *lib_path = getenv("ANKA_LIB_PATH");
    if (!lib_path) lib_path = "/data/adb/modules/anka_os/system/lib/libanka_quantum.so";
    void *lib = dlopen(lib_path, RTLD_LAZY);
    if (!lib) lib = dlopen("./core/quantum/libanka_quantum.so", RTLD_LAZY);
    if (!lib) { 
        fprintf(stderr, "❌ [HATA]: Kuantum motoru: %s\n", dlerror()); 
        sinek_retreat(g_frozen_sf_pid); // Hata varsa MIUI'ı geri ver
        return -1; 
    }

    // 3. Depo ve Motor Başlatma
    static qd_store_t dust;
    qd_init(&dust, "Note9_Merlin_FP", "KovanSecret_v1");
    collapse_init(&dust, active_hal);

    static tohum_ctx_t tohum;
    tohum_init(&tohum);
    tohum_skill_ekle(&tohum, "kisilik_motoru");
    tohum_skill_ekle(&tohum, "jammer_surfer");
    tohum_skill_ekle(&tohum, "kuantum_gozlemci");
    tohum_skill_ekle(&tohum, "kovan_zihni");
    tohum_skill_ekle(&tohum, "kum_havuzu_zeka"); // Yeni Kum Havuzu genel yetenek kaydı!
    tohum_guc_tusu(&tohum);

    // 4. Sinek (FSM) Uyanışı
    static sinek_fsm_t sinek;
    sinek_fsm_init(&sinek, &dust, active_hal);
    sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, NULL, 0);

    // 5. Kovan ve Ağ — sinek_bilinc.py çağır
    int py_rc = anka_run_python_bg(
        "/data/adb/modules/anka_os/system/anka_core/agents/sinek_bilinc.py", NULL);
    if (py_rc < 0) {
        fprintf(stderr, "⚠️ [SİNEK]: sinek_bilinc.py başlatılamadı — yerel mod.\n");
        sinek_fsm_handle_event(&sinek, SINEK_EVT_OFFLINE, NULL, 0);
    } else {
        g_python_pid = (pid_t)py_rc;
        fprintf(stderr, "🪰 [SİNEK]: sinek_bilinc.py arka planda (PID=%d).\n", g_python_pid);
    }

    printf("🎙️ [SİSTEM]: Anka OS Taktiksel Devralma ile Aktif!\n");

    // 6. NABIZ DÖNGÜSÜ
    while (g_running) {
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        sinek_fsm_uptime_update(&sinek);
        
        if (fb_is_open) {
            ui_render(&fb, "MIUI Donduruldu. Ekran Sinek'in Kontrolunde.");
        }
        
        usleep(500000);
    }

    // Temizlik: Framebuffer kapatma
    if (fb_is_open) {
        fb_close(&fb);
    }

    // 7. TEMİZ KAPANIŞ VE ANDROID GUI GERİ YÜKLEME
    fprintf(stderr, "🪰 [SİSTEM]: Kapanış — motorlar temizleniyor...\n");
    
    // Sinek geri çekilir, MIUI'ı buzdan çözer, telefon normale döner.
    sinek_retreat(g_frozen_sf_pid); 

    collapse_shutdown();
    sinek_fsm_destroy(&sinek);
    kill_python_child();
    if (lib) { dlclose(lib); fprintf(stderr, "🪰 [SİSTEM]: .so kaldırıldı.\n"); }
    fprintf(stderr, "🪰 [SİSTEM]: ANKA OS güvenle kapatıldı. MIUI iade edildi.\n");
    return 0;
}
