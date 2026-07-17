#ifndef ANKA_HAL_H
#define ANKA_HAL_H

#include <stdint.h>

// Sinek'in donanım yetenekleri (HAL - Hardware Abstraction Layer)
typedef struct {
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
    int (*capture_camera)(const char* output_path);
    int (*set_brightness)(int level_0_255);
    int (*display_blit)(const uint8_t *buf, int width, int height);
    
    // Hataları engellemek için eksik olan sensör üyelerini de ekledim:
    int (*get_light_level)(float *lux_out);
    int (*get_accel)(float *x, float *y, float *z);
    
    void *priv; // Donanım sürücüsünün özel verisi için
} AnkaHAL;

// Kovan'ın (veya Sinek'in) o an hangi donanımı "beden" olarak kullandığı
extern AnkaHAL *current_hal;

// Donanımı otomatik algıla ve doğru sürücüyü yükle
int init_hardware_bridge(void);

#endif
