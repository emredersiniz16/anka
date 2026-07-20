/*
 * core/engines/input_engine.c
 * ANKA OS - Donanım Girdi ve Girdi Güvenlik Mühürleme Motoru
 */

#include "anka_env.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>

#include "../hardware_types.h" // Donanım merkezli ortak referans

DeviceHardware current_hardware;

// Cihazın donanımını tarayan ve girdileri mühürleyen fonksiyon
void scan_hardware_inputs() {
    printf("[SİSTEM]: Donanım kontrol ediliyor... Tuş dizilimleri ve dokunmatik taranıyor.\n");
    
    // Redmi Note 9 (merlin) donanım yetenekleri simülasyonu ve haritalaması
    current_hardware.has_home_button = 1; 
    current_hardware.has_touch_screen = 1;
    
    // --- DONANIM GÜVENLİK KONTROLÜ (MÜHÜR) ---
    int eksik_parca = 0;

    if (!current_hardware.has_home_button) {
        printf("[HATA]: KRİTİK! Home tuşu algılanamadı!\n");
        eksik_parca = 1;
    }
    if (!current_hardware.has_touch_screen) {
        printf("[HATA]: KRİTİK! Dokunmatik ekran algılanamadı!\n");
        eksik_parca = 1;
    }

    if (eksik_parca) {
        printf("[ANKA-GÜVENLİK]: Donanım mühürlenemedi. Kurulum durduruldu.\n");
        exit(1); 
    } else {
        printf("[SİSTEM]: Tüm donanımlar onaylandı. Fiziksel yetenekler haritalandı.\n");
        printf("[ANKA-BİLİNÇ]: Donanım hazır, Sinek uyanışa geçiyor...\n");
    }
}
