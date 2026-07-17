#include "anka_env.h"
#include "anka_env.h"
// core/engines/camera_engine.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

// ==========================================
// ANKA OS - CANLI GÖZ VE VİZYON MOTORU
// ==========================================

// 1. GÜVENLİ ANLIK ÇEKİM MOTORU (Yeni Mimariden)
// Sinek her an görebilmeli, fork ile komut enjeksiyonunu engeller.
int safe_capture_frame(const char* output_path, const char* resolution) {
    pid_t pid = fork();

    if (pid == 0) {
        // Çocuk süreç: Kamera görüntüsünü yakala
        char *args[] = {"fswebcam", "-r", (char*)resolution, "--no-banner", (char*)output_path, NULL};
        execvp("fswebcam", args);
        _exit(1); 
    } else if (pid > 0) {
        // Ana süreç: Çocuğun fotoğrafı diske tamamen yazmasını bekle (Zeka bozuk dosya okumasın diye)
        waitpid(pid, NULL, 0); 
        printf("[ANKA] Kamera tetiklendi: %s\n", output_path);
        return 0;
    }
    return -1;
}

// 2. ESKİ YAPI İLE UYUMLU: ANLIK ÇEKİM (Zeka Analizi İçin)
void capture_image() {
    printf("[DONANIM] Sinek gözünü kırptı. Fotoğraf çekiliyor...\n");
    anka_run_python("mkdir -p gallery"); 
    
    // Eski güvensiz anka_run_python() komutu yerine, yeni güvenli motoru kullanıyoruz:
    safe_capture_frame("gallery/son_bakis.jpg", "1280x720");
    
    printf("[DONANIM] Görüntü alındı. AI analizi için hazır.\n");
}

// 3. CANLI KAMERA AÇ (Canlı Akış)
void open_live_camera() {
    printf("👁️ [GÖZ]: Canlı yayın başlatılıyor...\n");
    // Linux'un yerleşik video motoru 'ffmpeg' ile kamerayı doğrudan ekrana (fb0) basıyoruz. 
    // Sonundaki '&' işareti bunun arka planda sürekli çalışmasını sağlar.
    anka_run_python("ffmpeg -f v4l2 -framerate 30 -video_size 640x480 -i /dev/video0 -pix_fmt bgra -f fbdev /dev/fb0 > /dev/null 2>&1 &");
}

// 4. CANLI KAMERA KAPAT
void close_live_camera() {
    printf("👁️ [GÖZ]: Canlı yayın kapatılıyor...\n");
    // Arka planda çalışan canlı yayını öldürür
    anka_run_python("killall ffmpeg > /dev/null 2>&1");
    anka_run_python("clear"); // Sinek'in geri gelmesi için ekranı temizle
}
