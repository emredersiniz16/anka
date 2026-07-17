// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (QUANTUM FINAL - DÜZELTİLMİŞ)
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>

// Motorlar ve Donanım Katmanı
// Makefile'da -I./core tanımlı olduğu için doğrudan dosya isimlerini yazıyoruz.
#include "quantum/quantum_dust.h"
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "ui_engine.h"    // "engines/" prefix'i kaldırıldı
#include "anim_engine.h"  // "engines/" prefix'i kaldırıldı

// --- HAL MOCK ---
AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL }; 

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    // 1. GÖLGE KATMAN BAŞLATMA (Animasyon Motoru İçin)
    fb_context_t fb;
    if (fb_open(&fb) == 0) {
        // Uyanış sekansını çalıştır
        anim_boot_run(&fb, &g_hal);
    }

    printf("\033[1;36m --- ANKA OS: QUANTUM UYANIŞ --- \033[0m\n");

    // 2. Kuantum motorunu yükle
    // Not: Çalıştırma dizinine göre yolun doğruluğundan emin ol
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
