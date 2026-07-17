#include "anka_env.h"
#include "anka_env.h"
// core/engines/gallery_engine.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

// ==========================================
// ANKA OS - AKICI (FLUID) GALERİ MOTORU
// ==========================================

int current_photo_index = 0;
char photo_list[100][256]; // En fazla 100 fotoğraf listelesin
int total_photos = 0;

// 1. KÜTÜPHANEYİ TARA: Gallery klasöründeki fotoğrafları hafızaya alır
void load_gallery() {
    struct dirent *de;
    // Proje ana dizinindeki 'gallery' klasörünü okur
    DIR *dr = opendir("gallery");

    total_photos = 0;
    if (dr == NULL) {
        return; // Galeri henüz boş veya klasör yok
    }

    // Klasördeki tüm .jpg dosyalarını listeye ekle
    while ((de = readdir(dr)) != NULL) {
        if (strstr(de->d_name, ".jpg") != NULL) {
            sprintf(photo_list[total_photos], "gallery/%s", de->d_name);
            total_photos++;
            if (total_photos >= 100) break; // Sınır
        }
    }
    closedir(dr);
}

// 2. EKRANA BAS VE KAYDIR: Aktif fotoğrafı framebuffer'a yansıtır
void show_current_photo() {
    if (total_photos == 0) {
        // Galeri boşsa ekrana şık bir yazı bas
        anka_run_python("clear");
        printf("📂 [KÜTÜPHANE]: Henüz hiç fotoğraf çekilmemiş kanka!\n");
        return;
    }

    char cmd[512];
    // Linux'un en hafif görsel oynatıcısı 'fbi' ile fotoğrafı ekrana gömüyoruz.
    sprintf(cmd, "fbi -d /dev/fb0 -T 1 -noverbose -a %s > /dev/null 2>&1", photo_list[current_photo_index]);
    anka_run_python(cmd);
    
    printf("🖼️ [GALERİ]: %d/%d fotoğraf gösteriliyor: %s\n", current_photo_index + 1, total_photos, photo_list[current_photo_index]);
}

// 3. AKILLI JESTLER (SMART SWIPE): Sağa sola kaydırma motoru
void gallery_next() {
    if (current_photo_index < total_photos - 1) {
        current_photo_index++;
        show_current_photo();
    }
}

void gallery_prev() {
    if (current_photo_index > 0) {
        current_photo_index--;
        show_current_photo();
    }
}
