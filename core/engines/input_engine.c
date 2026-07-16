#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>
#include "hardware_types.h" // Tek merkezden referans alıyoruz

DeviceHardware current_hardware;

// Cihazın donanımını tarayan fonksiyon
void scan_hardware_inputs() {
    printf("[SİSTEM]: Donanim kontrol ediliyor... Tuş dizilimleri taranıyor.\n");
    
    // Simülasyon
    current_hardware.has_home_button = 1; 
    current_hardware.has_touch_screen = 1;
    
    // --- DONANIM GÜVENLİK KONTROLÜ (MÜHÜR) ---
    int eksik_parca = 0;

    if (!current_hardware.has_home_button) {
        printf("[HATA]: KRİTİK! Home tusu algilanamadi!\n");
        eksik_parca = 1;
    }
    if (!current_hardware.has_touch_screen) {
        printf("[HATA]: KRİTİK! Dokunmatik ekran algilanamadi!\n");
        eksik_parca = 1;
    }

    if (eksik_parca) {
        printf("[ANKA-GÜVENLİK]: Donanim mühürlenemedi. Kurulum durduruldu.\n");
        exit(1); 
    } else {
        printf("[SİSTEM]: Tum donanimlar onaylandi. Fiziksel yetenekler haritalandi.\n");
        printf("[ANKA-BİLİNÇ]: Donanim hazir, Sinek uyanisa geciyor...\n");
    }
}
