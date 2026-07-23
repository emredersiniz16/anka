#ifndef ANKA_HAL_H
#define ANKA_HAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 
 * Sinek'in donanım yetenekleri (HAL - Hardware Abstraction Layer)
 * Struct tag'i (struct AnkaHAL) açıkça belirtildi.
 */
typedef struct AnkaHAL {
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
    int (*capture_camera)(const char* output_path);
    int (*set_brightness)(int level_0_255);
    int (*display_blit)(const uint8_t *buf, int width, int height);
    
    /* Sensör üyeleri */
    int (*get_light_level)(float *lux_out);
    int (*get_accel)(float *x, float *y, float *z);
    
    void *priv; /* Donanım sürücüsünün özel verisi */
} AnkaHAL;

/* Kovan'ın (veya Sinek'in) o an hangi donanımı "beden" olarak kullandığı */
extern AnkaHAL *current_hal;

/* Donanımı otomatik algıla ve doğru sürücüyü yükle */
int init_hardware_bridge(void);

#ifdef __cplusplus
}
#endif

#endif /* ANKA_HAL_H */
