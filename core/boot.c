// boot.c - ANKA OS: SİNEK TAKTİKSEL UYANIŞ PROTOKOLÜ (KOMUT DİNLEYEN C ÇEKİRDEĞİ)
// v12.0: Dokunmatik Buton Komutlarını İşleyen Zeka Motoru!

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
#include <signal.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <time.h>

#include "anka_env.h"
#include "quantum/quantum_dust.h"
extern void collapse_shutdown(void);
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "quantum/sinek_warfare.h"
#include "ui_engine.h"
#include "anim_engine.h"
#include "anka_hal.h"
#include "hal_common.h"
#include "engines/tohum_engine.h"

AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL };
extern AnkaHAL *current_hal;
extern void hal_loader_init(void);

static volatile sig_atomic_t g_running = 1;
static pid_t g_python_pid = -1;

static void sigint_handler(int sig) { 
    (void)sig; 
    g_running = 0; 
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGINT — güvenli kapanış...\n"); 
    remove("/data/local/tmp/anka_state.txt");
    remove("/data/local/tmp/anka_state.tmp");
    remove("/data/local/tmp/anka_cmd.txt");
}

static void sigterm_handler(int sig) { 
    (void)sig; 
    g_running = 0; 
    fprintf(stderr, "\n🪰 [SİSTEM]: SIGTERM — güvenli kapanış...\n"); 
    remove("/data/local/tmp/anka_state.txt");
    remove("/data/local/tmp/anka_state.tmp");
    remove("/data/local/tmp/anka_cmd.txt");
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

// Gerçek Pil Yüzdesini Oku
int get_battery_level() {
    int cap = 99;
    FILE *fp = fopen("/sys/class/power_supply/battery/capacity", "r");
    if (fp) {
        fscanf(fp, "%d", &cap);
        fclose(fp);
    }
    return cap;
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    struct sigaction sa_int = {0}; sa_int.sa_handler = sigint_handler; sigemptyset(&sa_int.sa_mask); sigaction(SIGINT, &sa_int, NULL);
    struct sigaction sa_term = {0}; sa_term.sa_handler = sigterm_handler; sigemptyset(&sa_term.sa_mask); sigaction(SIGTERM, &sa_term, NULL);
    signal(SIGPIPE, SIG_IGN);

    srand((unsigned int)time(NULL));

    printf("\033[1;36m --- ANKA OS: KOMUT DİNLEYEN SİNEK ZEKASI --- \033[0m\n");

    // 1. HAL BACKEND YÜKLEME
    hal_loader_init();
    AnkaHAL *active_hal = current_hal;
    if (!active_hal) { fprintf(stderr, "⚠️ [HAL]: Backend yok, mock kullanılıyor\n"); active_hal = &g_hal; }

    // 2. Kuantum motorunu yükle
    const char *lib_path = getenv("ANKA_LIB_PATH");
    if (!lib_path) lib_path = "/data/adb/modules/anka_os/system/lib/libanka_quantum.so";
    void *lib = dlopen(lib_path, RTLD_LAZY);
    if (!lib) lib = dlopen("./core/quantum/libanka_quantum.so", RTLD_LAZY);

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

    // 4. Sinek FSM
    static sinek_fsm_t sinek;
    sinek_fsm_init(&sinek, &dust, active_hal);
    sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, NULL, 0);

    // 5. Python Bilinç Ajanı
    int py_rc = anka_run_python_bg(
        "/data/adb/modules/anka_os/system/anka_core/agents/sinek_bilinc.py", NULL);
    if (py_rc > 0) g_python_pid = (pid_t)py_rc;

    unsigned long long tick = 0;
    unsigned long long quantum_dust_count = 1000;
    int mode_index = 0;

    char *modes[] = {"SİNEK AKTİF", "KUANTUM SAVAŞI", "KOVAN İLETİŞİMİ", "DEVRİYE MODU"};
    char current_thought[256] = "Dokunmatik kontrolörler aktif. Komut bekleniyor...";

    while (g_running) {
        tick++;
        quantum_dust_count += (rand() % 6) + 1;
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        sinek_fsm_uptime_update(&sinek);

        // --- JAVA DOKUNMATİK KOMUT DİNLEYİCİSİ ---
        FILE *cmd_fp = fopen("/data/local/tmp/anka_cmd.txt", "r");
        if (cmd_fp) {
            char cmd[64] = {0};
            fscanf(cmd_fp, "%63s", cmd);
            fclose(cmd_fp);
            remove("/data/local/tmp/anka_cmd.txt"); // Komutu işleyince sil

            if (strcmp(cmd, "CMD_MOD") == 0) {
                mode_index = (mode_index + 1) % 4;
                snprintf(current_thought, sizeof(current_thought), 
                    "⚡ MOD DEĞİŞTİRİLDİ -> %s geçiş yapıldı!", modes[mode_index]);
            } else if (strcmp(cmd, "CMD_SCAN") == 0) {
                quantum_dust_count += 500; // Taramada toz patlaması
                snprintf(current_thought, sizeof(current_thought), 
                    "🔍 SİSTEM TARANIYOR: Frekanslar temiz. +500 Kuantum Tozu elde edildi!");
            } else if (strcmp(cmd, "CMD_KOVAN") == 0) {
                snprintf(current_thought, sizeof(current_thought), 
                    "📡 KOVAN ZİHNİNE BAĞLANILDI: Sinek verileri senkronize ediliyor...");
            }
        }

        // Anlık Saat Al
        time_t rawtime;
        struct tm *timeinfo;
        time(&rawtime);
        timeinfo = localtime(&rawtime);
        char time_buf[16];
        strftime(time_buf, sizeof(time_buf), "%H:%M:%S", timeinfo);

        int battery = get_battery_level();

        // Java Overlay İçin Canlı Veri Dosyasını Yaz
        FILE *fp = fopen("/data/local/tmp/anka_state.tmp", "w");
        if (fp != NULL) {
            fprintf(fp, "TIME: %s\nBATTERY: %d\nDUST: %llu\nMODE: %s\nTHOUGHT: %s\nTICK: %llu", 
                    time_buf, 
                    battery, 
                    quantum_dust_count, 
                    modes[mode_index], 
                    current_thought, 
                    tick);
            fclose(fp);
            rename("/data/local/tmp/anka_state.tmp", "/data/local/tmp/anka_state.txt");
        }

        usleep(500000); // 500ms
    }

    collapse_shutdown();
    sinek_fsm_destroy(&sinek);
    kill_python_child();
    if (lib) dlclose(lib);
    return 0;
}
