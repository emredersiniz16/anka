#ifndef ANKA_HAL_H
#define ANKA_HAL_H

#include <stdint.h>

// Sinek'in donanım yetenekleri (HAL - Hardware Abstraction Layer)
// ABI v1 ve ABI v2 (Otonom Fiziksel Beden Kontrolü) birleştirildi.
typedef struct {
    // --- ABI v1 (Klasik Yetenekler) ---
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
    int (*capture_camera)(const char* output_path);

    // --- ABI v2 (Sinek Otonomisi - Backend ile tam uyumlu) ---
    int (*get_battery)(int *pct);
    int (*set_brightness)(int level);
    int (*get_brightness)(int *level);
    int (*is_network_up)(int *up);
    int (*display_clear)(void);
    int (*display_blit)(const char *path, int x, int y, int w, int h);
    int (*get_device_info)(char *buf, int len);
    
    // --- Sensörler (Hataları engellemek için eklendi) ---
    int (*get_light_level)(float *lux_out);
    int (*get_accel)(float *x, float *y, float *z);
    
    void *priv; // Donanım sürücüsünün özel verisi için
} AnkaHAL;

// Kovan'ın (veya Sinek'in) o an hangi donanımı "beden" olarak kullandığı
extern AnkaHAL *current_hal;

// Donanımı otomatik algıla ve doğru sürücüyü yükle
int init_hardware_bridge(void);

#endif
