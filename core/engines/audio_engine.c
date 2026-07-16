// core/engines/audio_engine.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ==========================================
// ANKA OS - SES VE UYANDIRMA MOTORU (TAM DONANIMLI)
// ==========================================

// 1. KULAK: Sesi mikrofondan alıp RAM'e kaydeder
void record_audio(int duration_seconds) {
    char cmd[256];
    printf("[DONANIM] Mikrofon aktif. %d saniye dinleniyor...\n", duration_seconds);
    // Android/Termux uyumu için /tmp/ yerine /data/local/tmp/ kullanıldı
    sprintf(cmd, "arecord -D plughw:0,0 -d %d -f cd -t wav /data/local/tmp/anka_voice.wav > /dev/null 2>&1", duration_seconds);
    system(cmd);
    printf("[DONANIM] Ses kaydı hafızaya alındı.\n");
}

// 2. AĞIZ: Hoparlöre aktarır
void play_audio(const char* filepath) {
    char cmd[256];
    printf("[DONANIM] Hoparlör aktif.\n");
    sprintf(cmd, "aplay %s > /dev/null 2>&1", filepath);
    system(cmd);
}

// 3. SESLENDİR: Metni sese çevir ve oku (TTS)
void speak(const char* text) {
    char cmd[512];
    printf("[DONANIM] Seslendiriliyor: %s\n", text);
    // espeak motoru ile metni doğrudan hoparlöre bas
    sprintf(cmd, "espeak -v tr \"%s\" --stdout | aplay > /dev/null 2>&1", text);
    system(cmd);
}

// Yeni HAL (Donanım Köprüsü) ile uyumlu safe_speak sarmalayıcısı
void safe_speak(char* text) {
    speak(text); // Doğrudan gerçek TTS motorunu tetikler
}

// 4. UYANDIRMA (WAKE WORD): Seste "Sinek" veya "Click" var mı?
int check_wake_word(const char* wav_path) {
    char cmd[512];
    // Vosk ile ses analizi - Çıktı yolu Note 9 uyumlu yapıldı
    sprintf(cmd, "vosk-transcriber --model small-model %s > /data/local/tmp/ses_sonuc.txt", wav_path);
    system(cmd);

    FILE *fp = fopen("/data/local/tmp/ses_sonuc.txt", "r");
    if (fp) {
        char buffer[128];
        while (fgets(buffer, sizeof(buffer), fp)) {
            if (strstr(buffer, "Sinek") != NULL || strstr(buffer, "Click") != NULL) {
                fclose(fp);
                return 1; // Uyandırma kelimesi bulundu!
            }
        }
        fclose(fp);
    }
    return 0;
}
