#ifndef ANKA_HAL_COMMON_H
#define ANKA_HAL_COMMON_H

#include <stdint.h>

// Chatly'nin belirlediği ABI Versiyon Sözleşmesi (ABI v2 Sinek Otonomisi için güncellendi)
#define ANKA_HAL_ABI_VERSION 0x00020000

// AnkaHAL ana tanımı anka_hal.h içinde yapıldığı için burada ön bildirim (forward declaration) kullanıyoruz.
struct AnkaHAL;
typedef struct AnkaHAL AnkaHAL;

// Backend'lerin (Sürücülerin) kendilerini Kovan'a tanıtma şablonu (vtable)
typedef struct {
    unsigned int abi_version;
    const char* backend_name;
    AnkaHAL* (*get_hal_interface)(void);
} hal_backend_t;

#endif
