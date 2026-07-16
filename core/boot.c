// boot.c - SİNEK UYANIŞ PROTOKOLÜ (FULL ENTEGRE - FINAL)
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <sys/ioctl.h>
#include <string.h>
#include <time.h>

// --- EKSİK FONKSİYON TANIMLARI (Linker Hatalarını Önlemek İçin) ---
int get_battery_level() {
    return 100; // Şimdilik pili %100 göster
}

int user_confirmed_evolution() {
    return 1; // Kullanıcı her zaman onaylamış gibi davran
}

// Boş init_touch() gölgesi kaldırıldı, gerçek motor aşağıda dahil edildi.
// ----------------------------------------------------------------

// --- GERÇEK DOKUNMATİK MOTORU ENTEGRASYONU ---
#include "../touch_engine.c" 

// --- CORE MODÜLLERİ ---
#include "ui_engine.c"
#include "anim_engine.c" 
#include "agent_logic.c" 
#include "input_handler.c"
#include "audio_engine.c" 
#include "camera_engine.c"  
#include "gallery_engine.c" 
#include "idle_engine.c"    
#include "checkup.c"        
#include "input_engine.c"    
#include "ota_engine.c"      
#include "formatter.c"       

// --- SİSTEMİN DİRİLİŞ KOMUTLARI ---
void start_kovan_zihni() {
    printf("🪰 [SİSTEM]: Kovan zihni (Nexus) uyanıyor...\n");
    system("su -c 'python3 core/sinek_nexus.py &' "); 
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
    system("su -c 'python3 core/jammer_surfer.py --check-boot-env &'");
    printf("Sistem Senkronize... [ AKTİF ]\n");
    sleep(2);
}

int main() {
    // Canlı debug takibi için ekran çıktı yönlendirmeleri geçici olarak kapatıldı.
    // freopen("/data/local/tmp/debug.log", "w", stdout);
    // freopen("/data/local/tmp/debug.log", "w", stderr);

    // Terminal çıktılarını anlık ekrana basmaya zorla (Buffering önleyici)
    setvbuf(stdout, NULL, _IONBF, 0);

    srand(time(NULL));

    // --- 1. SİSTEMİN DİRİLİŞİ ---
    start_kovan_zihni(); 
    network_sync_protocol();
    splash_screen();
    boot_sequence();

    // --- 2. DONANIMLAR VE CHECK-UP ---
    if(system("su -c 'python3 agents/setup_engine.py'") != 0) {
        system("su -c 'python3 core/rejenere_motoru.py --force-recover &'");
    }
    
    run_initial_checkup();
    scan_hardware_inputs();
    check_for_evolution();

    // Ekran ve Dokunmatik yapılandırması
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
    
    // Gerçek dokunmatik sensörümüzü başlatıyoruz
    if (init_touch() < 0) {
        printf("⚠️ [HATA]: Dokunmatik ekran donanımı (/dev/input/event4) aktif edilemedi!\n");
    }
    
    printf("🎙️ [SİSTEM]: Anka OS Aktif, Kovan tam kapasite.\n");

    int touch_x = 0, touch_y = 0;
    int pulse_counter = 0;

    // --- 3. SÜREKLİ YÜKSEK HIZLI NABIZ DÖNGÜSÜ ---
    while(1) {
        // 3.1. Hassas Dokunmatik Takibi (Gecikmesiz - 100Hz)
        if (get_touch_event(&touch_x, &touch_y)) {
            printf("📍 [SİNEK AKSİYON]: Ekranda dokunuş yakalandı -> X: %d, Y: %d\n", touch_x, touch_y);
            // İleride dokunma koordinatlarını doğrudan input_handler'a paslayacağız:
            // handle_input(touch_x, touch_y);
        }

        // 3.2. Arka Plan Senkronizasyon Nabzı (Her 5 saniyede bir - Ana akışı dondurmadan)
        pulse_counter++;
        if (pulse_counter >= 500) { // 10ms * 500 = 5000ms (5 Saniye)
            // Sistem çağrılarını arka plana '&' ile gönderiyoruz ki dokunmatik kilitlenmesin
            system("su -c 'python3 agents/net_sync.py --verify &' > /dev/null 2>&1");
            system("su -c 'python3 core/sinek_nexus.py --pulse &' > /dev/null 2>&1");
            pulse_counter = 0;
        }

        usleep(10000); // 10ms dinlenme (İşlemciyi şişirmez, dokunmatiği canavar gibi akıcı tutar)
    }
    return 0;
}
