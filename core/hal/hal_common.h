#ifndef ANKA_HAL_COMMON_H
#define ANKA_HAL_COMMON_H

#include <stdint.h>
// AnkaHAL tam tanımını buraya dahil ediyoruz; bu sayede
// yalnızca hal_common.h dahil eden dosyalar da tam tipe erişebilir.
#include "anka_hal.h"

// Chatly'nin belirlediği ABI Versiyon Sözleşmesi (ABI v2 Sinek Otonomisi için güncellendi)
#define ANKA_HAL_ABI_VERSION 0x00020000

// Backend'lerin (Sürücülerin) kendilerini Kovan'a tanıtma şablonu (vtable)
typedef struct {
    unsigned int abi_version;
    const char* backend_name;
    AnkaHAL* (*get_hal_interface)(void);
} hal_backend_t;

#endif
