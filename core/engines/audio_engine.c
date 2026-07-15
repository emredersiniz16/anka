// core/engines/audio_engine.c
#include <stdio.h>

void safe_speak(char* text) {
    // Burada Anka OS'in ses çıkışına metni gönderen komutlar olacak
    printf("[DONANIM] Ses motoru konuşuyor: %s\n", text);
}
