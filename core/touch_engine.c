#include "anka_env.h"
#include "anka_env.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>

// ANKA OS: DOKUNMATİK EKRAN MOTORU
// Cihazın ekranına yapılan fiziksel dokunuşları yakalar ve koordinatlara ayırır.

int touch_fd = -1;
int current_x = 0;
int current_y = 0;

// 1. Dokunmatik Sensörü Başlat
int init_touch() {
    // Redmi 10X 4G (Note 9) için dokunmatik panel donanım adresi: /dev/input/event4
    touch_fd = open("/dev/input/event4", O_RDONLY | O_NONBLOCK);
    if (touch_fd < 0) {
        printf("⚠️ [SİSTEM UYARISI]: Dokunmatik sensör (/dev/input/event4) şu an okunamıyor.\n");
        return -1;
    }
    printf("✅ [SENSÖR AKTİF]: Dokunmatik yüzey (/dev/input/event4) dinleniyor...\n");
    return 0;
}

// 2. Parmağın Ekrana Dokunduğu Anı ve Koordinatları Yakala
// Dönüş: 1 (Ekrana basıldı), 0 (Bekleniyor)
int get_touch_event(int *out_x, int *out_y) {
    if (touch_fd < 0) return 0;

    struct input_event ev;
    int touch_pressed = 0;

    // Sensörden gelen verileri okuyoruz (O_NONBLOCK sayesinde sistemi dondurmaz)
    while (read(touch_fd, &ev, sizeof(struct input_event)) > 0) {
        if (ev.type == EV_ABS) {
            // X ve Y koordinatlarını anlık güncelle
            if (ev.code == ABS_MT_POSITION_X || ev.code == ABS_X) {
                current_x = ev.value;
            }
            if (ev.code == ABS_MT_POSITION_Y || ev.code == ABS_Y) {
                current_y = ev.value;
            }
        }
        // Parmağın ekrana temas ettiği an (Tetikleme)
        if (ev.type == EV_KEY && (ev.code == BTN_TOUCH || ev.code == BTN_TOOL_FINGER)) {
            if (ev.value == 1) { // 1: Parmak bastı, 0: Parmak kalktı
                *out_x = current_x;
                *out_y = current_y;
                touch_pressed = 1;
            }
        }
    }
    return touch_pressed;
}

// 3. Hedef Vuruldu mu? (Parmak butonun içinde mi?)
int is_button_clicked(int touch_x, int touch_y, int btn_x, int btn_y, int btn_w, int btn_h) {
    // Dokunulan X ve Y, bizim butonun sınırları içindeyse 1 (Evet) döndür
    if (touch_x >= btn_x && touch_x <= (btn_x + btn_w) &&
        touch_y >= btn_y && touch_y <= (btn_y + btn_h)) {
        return 1; 
    }
    return 0;
}
