/* core/hal/hal_power.c
 * Anka OS — Kovan Mimarisi — Güç/Ağ İzleme Uygulaması
 */

#include "anka_hal.h"
#include "hal_common.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define POWER_TAG  "GÜÇ"

/* Olası pil yolları */
static const char *BATT_CAP_PATHS[] = {
    "/sys/class/power_supply/battery/capacity",
    "/sys/class/power_supply/BAT0/capacity",
    "/sys/class/power_supply/BAT1/capacity",
    "/sys/class/power_supply/axp20x-battery/capacity",
    NULL
};
static const char *BATT_STATUS_PATHS[] = {
    "/sys/class/power_supply/battery/status",
    "/sys/class/power_supply/BAT0/status",
    "/sys/class/power_supply/BAT1/status",
    NULL
};

/* Olası ağ arayüz yolları */
static const char *NET_CARRIER_PATHS[] = {
    "/sys/class/net/wlan0/carrier",
    "/sys/class/net/wlan1/carrier",
    "/sys/class/net/eth0/carrier",
    "/sys/class/net/enp0s3/carrier",
    "/sys/class/net/rmnet_data0/carrier",
    NULL
};

/* Yardımcı: Dosyadan int oku */
static int read_int_from_file(const char *path, int *out)
{
    FILE *f = fopen(path, "r");
    if (!f) return 0;
    int ret = (fscanf(f, "%d", out) == 1);
    fclose(f);
    return ret;
}

/* hal_power_get_battery: Pil seviyesini okur */
hal_status_t hal_power_get_battery(int *pct)
{
    if (!pct) return HAL_ERR_INVALID_PARAM;

    for (int i = 0; BATT_CAP_PATHS[i]; i++) {
        if (read_int_from_file(BATT_CAP_PATHS[i], pct)) {
            *pct = HAL_MIN(HAL_MAX(*pct, 0), 100);
            HAL_LOG_DEBUG(POWER_TAG, "Pil: %%%d (%s)", *pct, BATT_CAP_PATHS[i]);
            return HAL_OK;
        }
    }

    HAL_LOG_WARN(POWER_TAG, "Pil bilgisi okunamadı");
    *pct = -1;
    return HAL_ERR_NOT_FOUND;
}

/* hal_power_get_battery_status: Şarj durumu (Charging/Discharging) */
hal_status_t hal_power_get_battery_status(char *buf, size_t len)
{
    if (!buf || len == 0) return HAL_ERR_INVALID_PARAM;

    for (int i = 0; BATT_STATUS_PATHS[i]; i++) {
        FILE *f = fopen(BATT_STATUS_PATHS[i], "r");
        if (f) {
            char tmp[64] = {0};
            if (fgets(tmp, sizeof(tmp), f)) {
                size_t slen = strlen(tmp);
                if (slen > 0 && tmp[slen-1] == '\n') tmp[slen-1] = '\0';
                snprintf(buf, len, "%s", tmp);
                fclose(f);
                return HAL_OK;
            }
            fclose(f);
        }
    }

    snprintf(buf, len, "Bilinmiyor");
    return HAL_ERR_NOT_FOUND;
}

/* hal_power_is_network_up: Ping atmadan ağ durumunu kontrol eder */
hal_status_t hal_power_is_network_up(int *is_up)
{
    if (!is_up) return HAL_ERR_INVALID_PARAM;

    for (int i = 0; NET_CARRIER_PATHS[i]; i++) {
        int status = 0;
        if (read_int_from_file(NET_CARRIER_PATHS[i], &status)) {
            *is_up = status; /* 1 = Bağlı, 0 = Bağlı değil */
            return HAL_OK;
        }
    }
    
    *is_up = 0;
    return HAL_ERR_NOT_FOUND;
}
