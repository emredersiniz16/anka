#ifndef ANKA_HAL_COMMON_H
#define ANKA_HAL_COMMON_H

#include "anka_hal.h"  /* AnkaHAL yapısı ana header'dan çekiliyor */

#ifdef __cplusplus
extern "C" {
#endif

// Chatly'nin belirlediği ABI Versiyon Sözleşmesi
#define ANKA_HAL_ABI_VERSION 0x00010000

// Backend'lerin (Sürücülerin) kendilerini Kovan'a tanıtma şablonu (vtable)
typedef struct {
    unsigned int abi_version;
    const char* backend_name;
    AnkaHAL* (*get_hal_interface)(void);
} hal_backend_t;

// Sistemin o an kullandığı aktif donanım pointer'ı
extern AnkaHAL *current_hal;

#ifdef __cplusplus
}
#endif

#endif /* ANKA_HAL_COMMON_H */
