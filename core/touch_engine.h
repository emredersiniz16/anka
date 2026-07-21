/*
 * core/touch_engine.h
 * ANKA OS - Dokunmatik Motoru Başlık Dosyası
 */

#ifndef TOUCH_ENGINE_H
#define TOUCH_ENGINE_H

// Dokunmatik sensörü başlatır (/dev/input/event4)
int init_touch(void);

// Dokunmatik sensörü güvenle kapatır
void close_touch(void);

// Ekrana basılma anını ve koordinatları yakalar
int get_touch_event(int *out_x, int *out_y);

// Belirtilen koordinatların ve butonun sınırları içinde tıklama olup olmadığını kontrol eder
int is_button_clicked(int touch_x, int touch_y, int btn_x, int btn_y, int btn_w, int btn_h);

#endif // TOUCH_ENGINE_H
