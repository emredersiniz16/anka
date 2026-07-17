#include "anka_env.h"
#include "anka_env.h"
// core/hal/hal_core.c
#include "anka_hal.h"
#include <stdio.h>

// --- GENEL (DEFAULT) DONANIM SÜRÜCÜLERİ ---
// İleride buraya Note 9 veya diğer cihazlar için cihaz bazlı özel sürücüleri ekleyeceğiz

int default_vibrate(int ms) { 
    printf("[ANKA DONANIM] Titreşim tetiklendi: %d ms\n", ms); 
    return 0; 
}

int default_read_touch(int *x, int *y) {
    // Şimdilik sahte koordinat dönüyoruz, ileride ekrandan okunacak
    *x = 0; 
    *y = 0;
    printf("[ANKA DONANIM] Dokunmatik okundu: X=%d, Y=%d\n", *x, *y);
    return 0;
}

int default_speak(const char* text) {
    printf("[ANKA DONANIM] Ses çıkışı: %s\n", text);
    return 0;
}

int default_capture_camera(const char* output_path) {
    printf("[ANKA DONANIM] Kamera çekimi yapılıyor. Dosya: %s\n", output_path);
    return 0;
}

// --- DONANIM KİMLİĞİ (HAL) ATAMASI ---
AnkaHAL hal_generic = { 
    .vibrate = default_vibrate,
    .read_touch = default_read_touch,
    .speak = default_speak,
    .capture_camera = default_capture_camera
};

AnkaHAL *current_hal = &hal_generic;

// --- KÖPRÜYÜ AYAĞA KALDIRMA ---
int init_hardware_bridge(void) {
    printf("[ANKA BİLGİ] Kovan donanım köprüsü kuruluyor...\n");
    // İleride burada cihazın ID'sini kontrol edip uygun HAL'i seçeceğiz.
    // Şimdilik generic (varsayılan) donanımı kullanıyoruz.
    return 0;
}
