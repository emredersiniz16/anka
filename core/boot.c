// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (QUANTUM FINAL)
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h> // libanka_quantum.so yüklemek için

// --- KUANTUM KATMANI ---
#include "core/quantum/quantum_dust.h"
#include "core/quantum/collapse_engine.h"
#include "core/quantum/sinek_fsm.h"

// --- HAL MOCK (Senin gerçek AnkaHAL header'ın ile değişecek) ---
AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL }; 

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("\033[1;36m --- ANKA OS: QUANTUM UYANIŞ --- \033[0m\n");

    // 1. Kuantum motorunu yükle
    void *lib = dlopen("./core/quantum/libanka_quantum.so", RTLD_LAZY);
    if (!lib) { printf("❌ [HATA]: Kuantum motoru yüklenemedi!\n"); return -1; }

    // 2. Depo ve Motor Başlatma
    static qd_store_t dust;
    qd_init(&dust, "Note9_Merlin_FP", "KovanSecret_v1");
    collapse_init(&dust, &g_hal);

    // 3. Sinek (FSM) Uyanışı
    static sinek_fsm_t sinek;
    sinek_fsm_init(&sinek, &dust, &g_hal);
    
    // Sinek'i uyanmaya zorla
    sinek_fsm_handle_event(&sinek, SINEK_EVT_WAKE, NULL, 0);

    // 4. Kovan ve Ağ (Senin mevcut ajanların)
    system("su -c 'python3 agents/sinek_nexus.py &' "); 
    
    printf("🎙️ [SİSTEM]: Anka OS Aktif, Kuantum Nabız Başlatıldı.\n");

    // 5. YÜKSEK HIZLI NABIZ DÖNGÜSÜ
    while(1) {
        // Sinek nabzı atıyor
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        
        // Kuantum FSM güncelleme
        sinek_fsm_uptime_update(&sinek);
        
        usleep(500000); // 2Hz nabız hızı
    }
    
    return 0;
}
