// boot.c - SİNEK UYANIŞ PROTOKOLÜ (FULL ENTEGRE - FINAL)
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <sys/ioctl.h>
#include <string.h>
#include <time.h>

// --- EKSİK FONKSİYON TANIMLARI ---
int get_battery_level() { return 100; }
int user_confirmed_evolution() { return 1; }

// --- DOKUNMATİK MOTORU (core/ klasöründe) ---
#include "touch_engine.c" 

// --- CORE MODÜLLERİ (core/engines/ klasöründe) ---
#include "engines/ui_engine.c"
#include "engines/anim_engine.c" 
#include "agent_logic.c"           // core/ içinde
#include "engines/input_handler.c"
#include "engines/audio_engine.c" 
#include "engines/camera_engine.c"  
#include "engines/gallery_engine.c" 
#include "engines/idle_engine.c"    
#include "checkup.c"               // core/ içinde
#include "engines/input_engine.c"    
#include "engines/ota_engine.c"      
#include "utils/formatter.c"       // core/utils/ içinde

// --- SİSTEMİN DİRİLİŞ KOMUTLARI (Güncellenen Yol Yapısı) ---
void start_kovan_zihni() {
    printf("🪰 [SİSTEM]: Kovan zihni (Nexus) uyanıyor...\n");
    system("su -c 'python3 agents/sinek_nexus.py &' "); 
}

void network_sync_protocol() {
    system("su -c 'python3 agents/net_sync.py --init &' ");
    printf("🪰 [AJAN]: Ağ optimizasyon ajanları aktif edildi.\n");
}

void splash_screen() {
    system("clear");
    system("su -c 'fbi -d /dev/fb0 -g 300x300+400+200 -a -noverbose -T 1 assets/sinek_icon.bmp &'");
    sleep(3); 
    system("pkill fbi");
}

void boot_sequence() {
    system("clear");
    printf("\033[1;36m --- ANKA OS: BİLİNÇLİ KOVAN --- \033[0m\n");
    // Yol güncellendi: core/ -> agents/ jammer_surfer'ın yerini kontrol et (agents'a taşıdıysan burayı agents/ yap)
    system("su -c 'python3 core/jammer_surfer.py --check-boot-env &'");
    printf("Sistem Senkronize... [ AKTİF ]\n");
    sleep(2);
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    srand(time(NULL));

    // --- 1. SİSTEMİN DİRİLİŞİ ---
    start_kovan_zihni(); 
    network_sync_protocol();
    splash_screen();
    boot_sequence();

    // --- 2. DONANIMLAR VE CHECK-UP ---
    if(system("su -c 'python3 agents/setup_engine.py'") != 0) {
        system("su -c 'python3 agents/rejenere_motoru.py --force-recover &'"); // Yol güncellendi
    }
    
    run_initial_checkup();
    scan_hardware_inputs();
    check_for_evolution();

    // ... (Geri kalan donanım ve dokunmatik kurulumu aynen kalıyor)
    int fb_fd = open("/dev/fb0", O_RDWR);
    if (fb_fd >= 0) {
        struct fb_var_screeninfo vinfo;
        if (ioctl(fb_fd, FBIOGET_VSCREENINFO, &vinfo) == 0) {
            int w = vinfo.xres;
            int h = vinfo.yres;
            float scale = (float)w / 1080.0f;
            update_fly_animation(0, w, h, scale);
        }
        close(fb_fd); 
    }
    
    if (init_touch() < 0) {
        printf("⚠️ [HATA]: Dokunmatik ekran donanımı aktif edilemedi!\n");
    }
    
    printf("🎙️ [SİSTEM]: Anka OS Aktif, Kovan tam kapasite.\n");

    // --- 3. SÜREKLİ YÜKSEK HIZLI NABIZ DÖNGÜSÜ ---
    int touch_x = 0, touch_y = 0;
    int pulse_counter = 0;
    while(1) {
        if (get_touch_event(&touch_x, &touch_y)) {
            printf("📍 [SİNEK AKSİYON]: Dokunuş -> X: %d, Y: %d\n", touch_x, touch_y);
        }

        pulse_counter++;
        if (pulse_counter >= 500) {
            system("su -c 'python3 agents/net_sync.py --verify &' > /dev/null 2>&1");
            system("su -c 'python3 agents/sinek_nexus.py --pulse &' > /dev/null 2>&1"); // Yol güncellendi
            pulse_counter = 0;
        }
        usleep(10000);
    }
    return 0;
}
