#ifndef ANKA_HAL_H
#define ANKA_HAL_H

#include <stdint.h> // uint8_t veri tipi için şart

// Sinek'in hangi cihazda (Note 9, J7 vb.) olursa olsun kullanacağı temel yetenekler
// Fonksiyon işaretçileri ile donanım bağımsız mimari (True HAL)
typedef struct {
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
    int (*capture_camera)(const char* output_path); // Sinek'in en önemli donanımı (Kamera)
    int (*set_brightness)(int level_0_255);         // Kuantum Çöküşü için parlaklık kontrolü (Eklendi)
    int (*display_blit)(const uint8_t *buf, int width, int height); // Ham piksel yazma katmanı (Eklendi)
} AnkaHAL;

// Kovan'ın (veya Sinek'in) o an hangi donanımı "beden" olarak kullandığı
extern AnkaHAL *current_hal;

// Donanımı otomatik algıla ve doğru sürücüyü yükle
int init_hardware_bridge(void);

#endif
