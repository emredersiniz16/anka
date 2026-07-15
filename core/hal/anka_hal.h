#ifndef ANKA_HAL_H
#define ANKA_HAL_H

// Sinek'in hangi cihazda olursa olsun kullanacağı temel yetenekler
typedef struct {
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
} AnkaHAL;

// Kovanın o an hangi donanımı "beden" olarak kullandığı
extern AnkaHAL *current_hal;

// Donanımı otomatik algıla ve sürücüyü yükle
int init_hardware_bridge(void);

#endif
