#include "anka_env.h"
#include "anka_env.h"
#include "hal_common.h"
#include <stdio.h>
#include <dlfcn.h>
#include <stddef.h>

// HATA BURADAYDI: Değişkeni burada tekrar tanımlama, dışarıdan (extern) referans al.
extern AnkaHAL *current_hal;

// Sinek'in arayacağı donanım sürücüleri (Önce en güçlülerini arar)
static const char *kCandidateBasenames[] = {
    "libhal_backend_flagship_sd.so", // 1. Hedef: Snapdragon Amiral Gemisi
    "libhal_backend_redmi10x.so",    // 2. Hedef: Xiaomi Redmi Serisi
    "libhal_backend_j7prime.so",     // 3. Hedef: Eski Samsung'lar
    "libhal_backend_generic.so",     // 4. Hedef: Hiçbirini bulamazsa Evrensel Mod
    "libhal_backend_sim.so",         // 5. Hedef: Simülatör
    NULL
};

void hal_loader_init() {
    printf("[ANKA BOOT] Donanım taranıyor...\n");
    
    char lib_path[256];
    void *handle = NULL;
    hal_backend_t *backend = NULL;

    // Listeyi baştan aşağı tara ve bulduğun ilk uyumlu kütüphaneyi yükle
    for (int i = 0; kCandidateBasenames[i] != NULL; i++) {
        sprintf(lib_path, "./core/hal/backends/%s", kCandidateBasenames[i]);
        handle = dlopen(lib_path, RTLD_LAZY);
        
        if (handle) {
            backend = (hal_backend_t*)dlsym(handle, "anka_backend_register");
            if (backend && backend->abi_version == ANKA_HAL_ABI_VERSION) {
                // Burada artık yukarıdaki extern sayesinde core içindeki değişkene yazıyoruz
                current_hal = backend->get_hal_interface();
                printf("[ANKA BOOT] Sürücü yüklendi: %s\n", backend->backend_name);
                return;
            }
            dlclose(handle);
        }
    }
    printf("[ANKA PANİK] Hiçbir donanım sürücüsü bulunamadı!\n");
}
