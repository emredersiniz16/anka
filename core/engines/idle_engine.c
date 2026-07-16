#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// ==========================================
// ANKA OS - BOŞTA BEKLEME (IDLE ENGINE) MOTORU
// ==========================================

// 1. HAYALET GEÇİŞİ EFEKTİ (Ghost Stream)
void trigger_ghost_stream(int w, int h) {
    printf("[IDLE] Hayalet veri akışı tetiklendi...\n");
    
    for(int i = 0; i < 5; i++) {
        int random_y = rand() % h;
        printf("\033[%d;0H\033[1;36m[SYS_DATA_STREAM_OK] 0x%X -> GLITCH_ACTIVE\033[0m", random_y, rand());
        fflush(stdout);
        usleep(20000); 
    }
}

// 2. SİBER RADAR TARAMASI (Cyber Radar & Tech Terms)
void trigger_cyber_radar(int w, int h) {
    printf("[IDLE] Siber radar taraması başlatıldı...\n");
    
    printf("\033[2;2H\033[1;32m⚡ SYS: ACTIVE\033[0m");
    printf("\033[3;2H\033[1;32m🔋 BAT: ONLINE\033[0m");
    
    // Projeye ait siber kelime havuzu
    char* terimler[] = {"Github", "ChatGPT", "Anka OS", "Click"};
    int rastgele_indeks = rand() % 4; // 0 ile 3 arasında rastgele seçer
    
    // Seçilen kelimeyi ekranın üst köşesinde parlatır
    printf("\033[2;%dH\033[1;36mCORE: %s\033[0m", w / 10 - 15, terimler[rastgele_indeks]);
    fflush(stdout);
    
    usleep(500000); // Yarım saniye ekranda parlasın
    
    // Temizleme adımı
    printf("\033[2;2H                ");
    printf("\033[3;2H                ");
    printf("\033[2;%dH               ", w / 10 - 15);
    fflush(stdout);
}

// 3. MASTER IDLE MANAGER: Efekt orkestrasını yönetir
void run_idle_orchestrator(int w, int h) {
    int sans = rand() % 100;
    
    if (sans < 15) {
        trigger_ghost_stream(w, h);
    } 
    else if (sans >= 15 && sans < 25) {
        trigger_cyber_radar(w, h);
    }
}
