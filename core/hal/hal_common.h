#ifndef ANKA_HAL_COMMON_H
#define ANKA_HAL_COMMON_H

// Chatly'nin belirlediği ABI Versiyon Sözleşmesi (ABI v2 Sinek Otonomisi için güncellendi)
#define ANKA_HAL_ABI_VERSION 0x00020000

// Anka'nın Evrensel Yetenekleri (ABI v1 + ABI v2 Sinek Otonomisi)
typedef struct {
    // --- ABI v1 (Klasik Yetenekler) ---
    int (*vibrate)(int ms);
    int (*read_touch)(int *x, int *y);
    int (*speak)(const char* text);
    int (*capture_camera)(const char* output_path);

    // --- ABI v2 (Sinek'in Fiziksel Beden Kontrolü) ---
    int (*get_battery)(int *pct);
    int (*set_brightness)(int level);
    int (*get_brightness)(int *level);
    int (*is_network_up)(int *up);
    int (*display_clear)(void);
    int (*display_blit)(const char *path, int x, int y, int w, int h);
    int (*get_device_info)(char *buf, int len);
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
