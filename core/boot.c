#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <time.h>

// ANKA OS Kuantum Çekirdeği & Canlı Veri Köprüsü (IPC)
void sig_handler(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        printf("● [ANKA_CORE]: Kapatma sinyali alındı (%d). Geçici dosyalar temizleniyor...\n", sig);
        remove("/data/local/tmp/anka_state.txt");
        remove("/data/local/tmp/anka_state.tmp");
        exit(0);
    }
}

int main(int argc, char *argv[]) {
    // Sinyal yakalayıcıları bağla
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // Rastgele sayı üreteci başlangıcı (Kuantum Tozu için)
    srand(time(NULL));

    printf("====================================================\n");
    printf("● ANKA OS v1.0 — C Kuantum Çekirdeği (Canlı Veri Modu)\n");
    printf("====================================================\n");
    printf("● [ANKA_CORE]: C Çekirdeği başlatıldı...\n");
    printf("● [ANKA_CORE]: Canlı durum dosyası: /data/local/tmp/anka_state.txt\n");

    unsigned long long quantum_dust = 100;
    int state_counter = 0;
    char *modes[] = {"DEVRİYE", "KUANTUM SAVAŞI", "KOVAN İLETİŞİMİ", "ANALİZ MODU"};

    while (1) {
        quantum_dust += (rand() % 15) + 1;
        state_counter++;
        char *current_mode = modes[(state_counter / 5) % 4];

        // Java Overlay'in okuyacağı canlı durum dosyasını güvenli (atomik) yaz
        FILE *fp = fopen("/data/local/tmp/anka_state.tmp", "w");
        if (fp != NULL) {
            fprintf(fp, "KUANTUM TOZU: %llu\nMOD: %s\nSTATUS: SurfaceFlinger Kilitlendi\nTICK: %d", 
                    quantum_dust, current_mode, state_counter);
            fclose(fp);
            
            // Atomik dosya değişimi (okuma çakışmasını engeller)
            rename("/data/local/tmp/anka_state.tmp", "/data/local/tmp/anka_state.txt");
        }

        usleep(500000); // 500ms döngü (Saniyede 2 güncelleme)
    }

    return 0;
}
