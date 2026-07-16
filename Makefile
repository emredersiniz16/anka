#include "../hal_common.h"
#include <stdio.h>

// --- Evrensel (Generic) Donanım Fonksiyonları ---

int generic_vibrate(int ms) {
    printf("[GENERIC HAL] Titreşim simüle edildi (Cihaz tanınmadı): %d ms\n", ms);
    return 0;
}

int generic_read_touch(int *x, int *y) {
    // Standart sahte dokunmatik verisi
    *x = 0; 
    *y = 0;
    return 0;
}

int generic_speak(const char* text) {
    printf("[GENERIC HAL] Ses Çıkışı (Termux TTS bekleniyor): %s\n", text);
    return 0;
}

int generic_capture_camera(const char* output_path) {
    printf("[GENERIC HAL] Kamera simüle edildi. Kayıt yolu -> %s\n", output_path);
    return 0;
}

// --- Fonksiyonları HAL Yapısına Bağlama ---
static AnkaHAL generic_hal = {
    .vibrate = generic_vibrate,
    .read_touch = generic_read_touch,
    .speak = generic_speak,
    .capture_camera = generic_capture_camera
};

AnkaHAL* get_generic_interface(void) {
    return &generic_hal;
}

// --- Loader'ın (Yükleyicinin) Arayacağı İmza ---
hal_backend_t anka_backend_register = {
    .abi_version = ANKA_HAL_ABI_VERSION,
    .backend_name = "Evrensel (Generic) Kurtarma Sürücüsü",
    .get_hal_interface = get_generic_interface
};
