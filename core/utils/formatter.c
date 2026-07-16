#include <stdio.h>
#include <unistd.h>

void print_human_readable(const char *text) {
    int i = 0;
    while(text[i] != '\0') {
        // Cümle bitişlerini algıla ve nefes payı bırak
        if (text[i] == '.' || text[i] == '!' || text[i] == '?') {
            putchar(text[i]);
            putchar('\n');
            printf("\n"); // Satır arası boşluk: Gözün dinlenmesi için
            usleep(300000); // 0.3 saniye "düşünme/okuma" payı
        } 
        // Paragraf başı veya yeni madde için otomatik boşluk
        else if (text[i] == '\n') {
            putchar('\n');
            printf("\n"); 
        }
        else {
            putchar(text[i]);
        }
        i++;
        // Harf yazma hızı: İnsan okuma hızına yakın bir tıkırtı
        usleep(15000); 
    }
    printf("\n\n"); // Mesaj sonunda geniş bir boşluk
}
