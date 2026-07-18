/*
 * core/engines/audio_engine.c
 * Ses motoru — Termux/Android ortamında stub implementasyon
 */

#include <stdio.h>

/* Uyanış sesi çal. Gerçek donanımda TinyAlsa/AAudio ile implemente edilir.
 * Termux ortamında sessiz geçer. */
int audio_play_awakening(void) {
    fprintf(stderr, "🔊 [SES]: Uyanış sesi tetiklendi.\n");
    return 0;
}
