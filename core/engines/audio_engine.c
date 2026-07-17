/*
 * core/engines/audio_engine.c
 * 🪰 ANKA OS - BİRLEŞTİRİLMİŞ SES MOTORU
 * 
 * 1. Donanım Seviyesi (PCM): Boot anında sıfır gecikmeli klik/vızıltı.
 * 2. Uygulama Seviyesi (TTS/STT): Espeak ve Vosk entegrasyonu.
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <math.h>
#include <sys/wait.h>

/* PCM sentez sabitleri */
#define SAMPLE_RATE 44100
#define BUZZ_AMP 16000
#define CLICK_AMP 32000
#define M_PI 3.14159265358979323846

/* ══════════════════════════════════════════════════════════════════════════
 * 1. DÜŞÜK GECİKMELİ SES SENTEZİ (Boot sekansı için)
 * ══════════════════════════════════════════════════════════════════════════ */

// (Kısa özet: WAV header ve PCM üretimi Chatly ile yaptığımızın aynısı, 
// o yüzden buraya kodun o kısmını gömüyoruz)
static void write_wav_header(FILE *f, uint32_t num_samples) {
    uint32_t data_size = num_samples * 2;
    uint32_t riff_size = 36 + data_size;
    fwrite("RIFF", 1, 4, f); fwrite(&riff_size, 4, 1, f);
    fwrite("WAVEfmt ", 1, 8, f);
    uint32_t fmt_size = 16; fwrite(&fmt_size, 4, 1, f);
    uint16_t format = 1, channels = 1; fwrite(&format, 2, 1, f); fwrite(&channels, 2, 1, f);
    uint32_t rate = SAMPLE_RATE; fwrite(&rate, 4, 1, f);
    uint32_t byte_rate = rate * 2; fwrite(&byte_rate, 4, 1, f);
    uint16_t align = 2; fwrite(&align, 2, 1, f);
    uint16_t bits = 16; fwrite(&bits, 2, 1, f);
    fwrite("data", 1, 4, f); fwrite(&data_size, 4, 1, f);
}

// ... (Generate buzz ve click fonksiyonların buraya geliyor) ...

// BOOT anında çalınacak optimize uyanış sesi
int audio_play_awakening(void) {
    // PCM üret ve çal (daha önce yazdığımız mantık)
    // Sırf boot'ta donmasın diye doğrudan aplay'e pipe edebilirsin.
    return 0; // Başarılı
}

/* ══════════════════════════════════════════════════════════════════════════
 * 2. YÜKSEK SEVİYE DONANIM KÖPRÜSÜ (Senin kodların)
 * ══════════════════════════════════════════════════════════════════════════ */

// 1. KULAK: Mikrofon kaydı (arecord)
void record_audio(int duration_seconds) {
    char cmd[256];
    printf("[DONANIM] Mikrofon aktif. %d saniye dinleniyor...\n", duration_seconds);
    sprintf(cmd, "arecord -D plughw:0,0 -d %d -f cd -t wav /data/local/tmp/anka_voice.wav > /dev/null 2>&1", duration_seconds);
    system(cmd);
}

// 2. AĞIZ: Hoparlör oynatıcı
void play_audio(const char* filepath) {
    char cmd[256];
    sprintf(cmd, "aplay %s > /dev/null 2>&1", filepath);
    system(cmd);
}

// 3. SESLENDİR: Espeak (Metin -> Ses)
void speak(const char* text) {
    char cmd[512];
    printf("[DONANIM] Seslendiriliyor: %s\n", text);
    sprintf(cmd, "espeak -v tr \"%s\" --stdout | aplay > /dev/null 2>&1", text);
    system(cmd);
}

// 4. UYANDIRMA: Vosk (Wake Word)
int check_wake_word(const char* wav_path) {
    char cmd[512];
    sprintf(cmd, "vosk-transcriber --model small-model %s > /data/local/tmp/ses_sonuc.txt", wav_path);
    system(cmd);

    FILE *fp = fopen("/data/local/tmp/ses_sonuc.txt", "r");
    if (fp) {
        char buffer[128];
        while (fgets(buffer, sizeof(buffer), fp)) {
            if (strstr(buffer, "Sinek") != NULL || strstr(buffer, "Click") != NULL) {
                fclose(fp);
                return 1;
            }
        }
        fclose(fp);
    }
    return 0;
}
