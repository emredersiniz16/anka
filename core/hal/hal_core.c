#include "anka_hal.h"
#include <stdio.h>

// İleride buraya cihaz bazlı özel sürücüleri ekleyeceğiz
int default_vibrate(int ms) { printf("Titreşim tetiklendi: %d ms\n", ms); return 0; }

AnkaHAL hal_generic = { .vibrate = default_vibrate };
AnkaHAL *current_hal = &hal_generic;

int init_hardware_bridge(void) {
    printf("[ANKA] Kovan köprüsü kuruluyor...\n");
    // Burada cihazın ID'sini kontrol edip uygun HAL'i seçeceğiz
    return 0;
}
