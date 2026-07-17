// boot.c - ANKA OS: SİNEK UYANIŞ PROTOKOLÜ (QUANTUM FINAL)
// DÜZELTME: hal/hal_core.h → anka_hal.h, fb_open() kullanımı düzeltildi
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>

// Motorlar ve Donanım Katmanı
#include "quantum/quantum_dust.h"
#include "quantum/collapse_engine.h"
#include "quantum/sinek_fsm.h"
#include "ui_engine.h"     // fb_context_t, fb_open, fb_close
#include "anim_engine.h"   // anim_boot_run
#include "anka_hal.h"      // AnkaHAL tipi (eski adı: hal/hal_core.h — YOK)

// --- HAL MOCK ---
AnkaHAL g_hal = { .vibrate = NULL, .speak = NULL };
// Bunu main'in hemen üstüne ekle kanka:
extern void ui_render(const char *last_message);

int main() {
    // ...


int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    // 1. GÖLGE KATMAN BAŞLATMA (Animasyon Motoru İçin)
    // DÜZELTME: raw fd yerine fb_context_t kullan (anim_boot_run bunu bekler)
    fb_context_t fb;
    if (fb_open(&fb) == 0) {
        // Uyanış sekansını çalıştır
        anim_boot_run(&fb, &g_hal);
        fb_close(&fb);
    } else {
        fprintf(stderr, "⚠️ [GÖLGE]: Framebuffer açılamadı, animasyon atlanıyor.\n");
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
        // 1. Kuantum Nabzı (Arka plan zekası)
        collapse_fire(COLLAPSE_TRIGGER_TIMER, NULL, 0);
        sinek_fsm_uptime_update(&sinek);
        
        // 2. ARAYÜZÜ EKRANA BAS (İşte OS'i telefonda gösterecek olan bu!)
        ui_render("Sistem Senkronize... Kovan Dinleniyor.");
        
        usleep(500000); // Yarım saniye bekle
    }


    return 0;
}

