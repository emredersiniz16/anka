#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// SINEK GÖRSEL VE KOORDİNAT MOTORU (MİLİMETRİK HİZALAMA)
void update_fly_animation(int current_state, int screen_w, int screen_h, float scale) {
    
    // Ekrandaki eski görseli temizle ki yenisi tam üstüne otursun
    system("pkill -f fbi > /dev/null 2>&1");

    // Sinek boyutları (Ölçeğe göre otomatik ayarlanır)
    int fly_w = (int)(250 * scale); // Sinek genişliği varsayılan 250 piksel
    int fly_h = (int)(250 * scale); // Sinek yüksekliği varsayılan 250 piksel

    // Sinek Koordinatları (Ekranın sağ üst köşesindeki neon panelin içi)
    int pos_x = screen_w - fly_w - (int)(50 * scale); // Sağdan 50 piksel içeride
    int pos_y = (int)(80 * scale);                   // Üstten 80 piksel aşağıda

    char command[1024];

    if (current_state == 0) {
        // 0 = FLY_IDLE: Senin yaptığın uçan sinek gifi devreye girer
        printf("\n🪰 [GÖRSEL PANEL]: Uçan Sinek koordinatına oturtuluyor... (%d, %d) Boyut: %dx%d\n", pos_x, pos_y, fly_w, fly_h);
        
        // fbi komutuna geometri, konum ve zoom parametrelerini gömüyoruz
        sprintf(command, "fbi -d /dev/fb0 -g %dx%d+%d+%d -a -noverbose -T 1 assets/sinek_ucuyor.GIF &", fly_w, fly_h, pos_x, pos_y);
        system(command);
    } 
    else if (current_state == 1) {
        // 1 = FLY_THINK: Elini yüzünü ovuşturan o efsane düşünen sinek gifi
        printf("\n⚡ [BEYİN PANELİ]: Düşünen Sinek elini yüzünü ovuşturuyor... Konum: (%d, %d)\n", pos_x, pos_y);
        
        sprintf(command, "fbi -d /dev/fb0 -g %dx%d+%d+%d -a -noverbose -T 1 assets/sinek_dusunen.GIF &", fly_w, fly_h, pos_x, pos_y);
        system(command);
    }
}
