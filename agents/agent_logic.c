// agents/agent_logic.c
#include <stdio.h>
#include <string.h>

// ANKA OS: AJAN NİYET ANALİZ MOTORU
// Gelen girdiyi C tarafında hızlıca sınıflandırır.

void analyze_input(char* input) {
    // 1. Güvenlik Kontrolü: Girdi boşsa işleme
    if (input == NULL || strlen(input) == 0) {
        return;
    }

    // 2. Niyet (Intent) Analizi
    if (strstr(input, "nasıl")) {
        // Ajan bilgi verme moduna geçer
        printf("[NİYET]: BİLGİ_TALEP_EDİLDİ\n");
    } else if (strstr(input, "sinek") || strstr(input, "anka")) {
        // Ajan doğrudan komut dinleme moduna geçer
        printf("[NİYET]: KOMUT_BEKLENİYOR\n");
    } else {
        // Ajan genel sohbet (kişiselleşme) modunda devam eder
        printf("[NİYET]: GENEL_SOHBET\n");
    }
    
    printf("🪰 Ajan: %s mesajındaki niyet çözüldü.\n", input);
}
