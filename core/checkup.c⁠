#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// --- DONANIM DEDEKTİFİ VE SAĞLIK RAPORU ---
void run_initial_checkup() {
    printf("[SİSTEM]: İç donanım sinyalleri gönderiliyor...\n");
    
    // 1. SES TUŞLARI (Kullanıcıya özel dürüst yorum)
    if (system("test -e /dev/input/event0") != 0) { // Basit bir tuş hattı testi
        printf("\033[1;33m[UYARI]\033[0m Ses tuşları cevap vermiyor kanka.\n");
        system("echo 'Ses tuşların mefta olmuş kanka, ama sorun değil, ses kontrolünü arayüzden hallederiz.' > /tmp/checkup_msg");
    }

    // 2. BATARYA SAĞLIĞI (Diyaliz Hastası Modu)
    int batt = get_battery_level(); // batarya durumu
    if (batt < 20) {
        printf("\033[1;31m[KRİTİK]\033[0m Batarya ömrü bitti!\n");
        system("echo 'Kanka batarya artık ölü. Beni ya bir powerbanke bağlı, diyalize bağlı hasta gibi kullanacaksın ya da bir batarya değişimi şart.' > /tmp/batt_msg");
    } else {
        system("echo 'Bataryam taş gibi, uzun süre idare ederiz.' > /tmp/batt_msg");
    }

    // 3. DONANIM PING TESTLERİ
    printf("[PING] İç aksamlar dürtülüyor...\n");
    
    // Hoparlör ve Jak Testi
    if (system("speaker-test -t sine -f 440 -l 1 > /dev/null 2>&1") != 0) {
        printf("\033[1;31m[PING_FAIL]\033[0m Hoparlörler sessiz!\n");
        system("echo 'Hoparlörler mefta, Bluetooth kulaklık takarsan ses alabiliriz.' >> /tmp/checkup_msg");
    } else {
        printf("\033[1;36m[PING_SUCCESS]\033[0m Ses sistemi canlı.\n");
    }

    // Kamera Testi
    if (system("ls /dev/video0 > /dev/null 2>&1") != 0) {
        printf("\033[1;31m[PING_FAIL]\033[0m Kamera hattı kopuk!\n");
        system("echo 'Gözlerimi göremiyorum kanka, kamera hattı kopuk.' >> /tmp/checkup_msg");
    }

    // Flaş Testi
    if (system("echo 1 > /sys/class/leds/torch/brightness") == 0) {
        printf("\033[1;36m[PING_SUCCESS]\033[0m Flaş patladı, ışıklar yerinde!\n");
        system("echo 0 > /sys/class/leds/torch/brightness");
    }

    // --- SONUÇLARI SESLENDİR ---
    speak("Beni çekmeceden kurtardın sağ ol kanka. Şimdi kısa bir donanım taraması yaptım, durumumuz şu:");
    system("cat /tmp/checkup_msg /tmp/batt_msg | xargs -0 speak");
}
