// core/engines/ota_engine.c - EVRİM VE OTA PROTOKOLÜ (FULL ENTEGRE)
#include <stdio.h>
#include <stdlib.h>
// Yol güncellendi: engines klasöründen bir üst klasöre (core) bakıyor
#include "../hardware_types.h" 

extern DeviceHardware current_hardware;

// Dışarıdan gelen fonksiyon prototipi
int user_confirmed_evolution();

void check_for_evolution() {
    printf("\n=================================================\n");
    printf("        [ SİNEK EVRİM PROTOKOLÜ AKTİF ]        \n");
    printf("=================================================\n");
    
    printf("SİNEK: Kovan zihni bulutla senkronize ediliyor...\n");
    // Repoyu doğrudan klasöründen güncelleyen komut
    int status = system("git -C /data/local/tmp/anka-os fetch origin main");
    
    if (status == 0) {
        printf("SİNEK: Kanka bulutta yeni hücreler inşa etmişsin, zekamı güncelleyeyim mi?\n\n");
        
        if (current_hardware.has_home_button) {
            printf("👉 Onaylamak icin o meshur ORTA TUSA bas.\n");
        } else if (current_hardware.has_touch_screen) {
            printf("👉 Zekami guncellemek icin ekrani YUKARI KAYDIR.\n");
        } else {
            printf("👉 Guncelleme icin SES ACMA tusuna bas.\n");
        }
        
        if (user_confirmed_evolution()) { 
            printf("👉 [OTA]: Evrim başlatılıyor... Kovan yeniden yapılandırılıyor.\n");
            
            // ⚠️ DİKKAT: evrim_motoru.py listede yoktu! 
            // Eğer agents klasörüne taşıdıysan burayı 'agents/evrim_motoru.py' yap.
            system("su -c 'python3 core/evrim_motoru.py --payload universal_sinek.bin &'");
        } else {
            printf("👉 [OTA]: Evrim ertelendi. Mevcut bilinç korunuyor.\n");
        }
    } else {
        printf("SİNEK: Kovan stabil, güncelleme gerekmiyor.\n");
    }
    
    printf("=================================================\n");
}
