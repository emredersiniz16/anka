// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (QUANTUM FINAL - MÜHÜRLENMEYE HAZIR)
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
#include <fcntl.h>

// Motorlar ve Donanım Katmanı
#include "quantum/quantum_dust.h"
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "ui_engine.h"
#include "anim_engine.h"
#include "hal/hal_core.h"

// --- HAL MOCK ---
AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL }; 

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    // 1. GÖLGE KATMAN BAŞLATMA (Animasyon Motoru İçin)
    int fb_fd = open("/dev/fb0", O_RDWR);
    if (fb_fd >= 0) {
        // Uyanış sekansını çalıştır
        anim_boot_run(fb_fd, &g_hal);
        close(fb_fd);
    }

    printf("\033[1;36m --- ANKA OS: QUANTUM UYANIŞ --- \033[0m\n");

    // 2. Kuantum motorunu yükle
    void *lib = dlopen("./core/quantum/libanka_quantum.so", RTLD_LAZY);
    if (!lib) { 
        fprintf(stderr, "❌ [HATA]: Kuantum motoru yüklenemedi: %s\n", dlerror()); 
        return -1; 
    }

    // 3. Depo ve Motor Başlatma
    static qd_store_t dust;
    qd_init(&dust, "Note9_Merlin_FP", "KovanSecret_v1");
    collapse_init(&dust, &g_hal);

    // 4. Sinek (FSM) Uyanışı
    static sinek_fsm_t sinek;
    sinek_fsm_init(&sinek, &dust, &g_hal);
    
    // Sinek'i uyanmaya zorla
    sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, NULL, 0);

    // 5. Kovan ve Ağ
    system("su -c 'python3 agents/sinek_nexus.py &' "); 
    
    printf("🎙️ [SİSTEM]: Anka OS Aktif, Kuantum Nabız Başlatıldı.\n");

    // 6. YÜKSEK HIZLI NABIZ DÖNGÜSÜ
    while(1) {
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        sinek_fsm_uptime_update(&sinek);
        
        usleep(500000); 
    }
    
    return 0;
}
