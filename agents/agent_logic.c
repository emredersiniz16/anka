#include <stdio.h>
#include <string.h>

void analyze_input(char* input) {
    // 1. Artık sadece "kanka"yı değil, gelen cümlenin anlamını (intent) çözüyoruz
    if (strstr(input, "nasıl")) {
        // Ajan bilgi verme moduna geçer
    } else if (strstr(input, "sinek") || strstr(input, "anka")) {
        // Ajan doğrudan komut dinleme moduna geçer
    } else {
        // Ajan genel sohbet (kişiselleşme) modunda devam eder
    }
    
    printf("🪰 Ajan: %s mesajındaki niyet çözüldü.\n", input);
}
