#include "anka_env.h"
#include "anka_env.h"
// core/engines/input_engine.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>

// ⚠️ DİKKAT: hardware_types.h listede yoktu!
// Bu motor 'core/engines/' içinde olduğu için, eğer hardware_types.h dosyasını
// 'core/' ana klasörüne attıysan yol aşağıdaki gibi '../hardware_types.h' olmalı.
// Eğer onu da 'engines' klasörüne attıysan başındaki '../' kısmını sil kanka.
#include "../hardware_types.h" // Tek merkezden referans alıyoruz

DeviceHardware current_hardware;

// Cihazın donanımını tarayan fonksiyon
void scan_hardware_inputs() {
    printf("[SİSTEM]: Donanım kontrol ediliyor... Tuş dizilimleri taranıyor.\n");
    
    // Simülasyon (Note 9 donanım yetenekleri)
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
