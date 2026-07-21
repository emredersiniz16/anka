// core/engines/system_monitor.c - DONANIM NABIZ MOTORU
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Sinek'in diğer modüllerden (FSM) pili doğrudan okuyabilmesi için tekil fonksiyon
int anka_get_real_battery() {
    int batt = 100; // Okuyamazsa 100 dönsün, sahte panik yapmasın
    
    // Standart Android batarya yolu
    FILE *f_batt = fopen("/sys/class/power_supply/battery/capacity", "r");
    
    // Eğer bulamazsa Redmi/Xiaomi cihazlara özel bms (Battery Management System) yoluna bak
    if (!f_batt) {
        f_batt = fopen("/sys/class/power_supply/bms/capacity", "r");
    }

    if (f_batt) {
        fscanf(f_batt, "%d", &batt);
        fclose(f_batt);
    }
    return batt;
}

void get_sys_status(char *buffer) {
    // 🔋 Şarj Seviyesi
    int batt = anka_get_real_battery();

    // 📶 Wi-Fi (Sinyal gücü)
    int wifi = 0; // -1 yerine varsayılan 0
    FILE *f_wifi = fopen("/proc/net/wireless", "r");
    if (f_wifi) {
        char line[256];
        while (fgets(line, sizeof(line), f_wifi)) {
            if (strstr(line, "wlan0")) {
                sscanf(line, "%*s %*s %d", &wifi);
                // -100/0 arasını 0-100 yüzdesine çevir
                wifi = (wifi > -100) ? (wifi + 100) : 0; 
            }
        }
        fclose(f_wifi);
    }

    // 🌐 Hat / Sinyal (Network) - Google DNS ping kontrolü
    int net = (system("ping -c 1 8.8.8.8 > /dev/null 2>&1") == 0) ? 1 : 0;

    // Durumu tek satırda mühürle
    sprintf(buffer, "🔋 %d%% | Wi-Fi: %d%% | Hat: %s", 
            batt, wifi, net ? "ON" : "OFF");
}
