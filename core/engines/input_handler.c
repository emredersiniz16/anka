#include "anka_env.h"
#include "anka_env.h"
// core/engines/input_handler.c
#include <stdio.h>
#include <stdlib.h>

// ==========================================
// ANKA OS - AKILLI GİRİŞ VE JEST KONTROLCÜSÜ
// ==========================================

// Akıllı Jest Tespiti (Smart Swipe)
// Ekranda parmağın başladığı yer ile bittiği yer arasındaki farka bakar.
// Dönüş değerleri: 1 -> Sağa Kaydırma (Geri), 2 -> Sola Kaydırma (İleri), 0 -> Hareket Yok
int detect_swipe(int start_x, int end_x, int threshold) {
    if (end_x - start_x > threshold) {
        return 1; // Sağa kaydırma (Geri git)
    } else if (start_x - end_x > threshold) {
        return 2; // Sola kaydırma (İleri git)
    }
    return 0; // Bariz bir kaydırma hareketi yok
}

void listen_input() {
    printf("--- ANKA OS: Giriş Kontrolcüsü Beklemede ---\n");
    printf("1. Wake-word (Hey Sinek/Click/Anka) dinleniyor...\n");
    printf("2. Kanat (Gönder) butonu dinleniyor...\n");
    printf("3. Akıllı Jestler (Smart Swipe) aktif...\n");
}

void trigger_ai_process() {
    printf("🪰 Sinek: Düşünme moduna geçildi. (AI aktif)\n");
}

// Göz tetiklendiğinde çalışacak Vision AI fonksiyonu
void trigger_vision_process() {
    printf("📸 Sinek: Gözler açıldı, Vision AI köprüsü aktif!\n");
}
