#ifndef ANKA_HAL_COMMON_H
#define ANKA_HAL_COMMON_H

// Chatly'nin belirlediği ABI Versiyon Sözleşmesi
#define ANKA_HAL_ABI_VERSION 0x00010000

// Anka'nın Evrensel Yetenekleri
typedef struct {
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
    int (*capture_camera)(const char* output_path);
} AnkaHAL;

// Backend'lerin (Sürücülerin) kendilerini Kovan'a tanıtma şablonu (vtable)
typedef struct {
    unsigned int abi_version;
    const char* backend_name;
    AnkaHAL* (*get_hal_interface)(void);
} hal_backend_t;

// Sistemin o an kullandığı aktif donanım pointer'ı
extern AnkaHAL *current_hal;

#endif
