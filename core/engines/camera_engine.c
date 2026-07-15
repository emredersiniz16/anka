#include "../hal/anka_hal.h"
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

// Güvenli kamera motoru: Sinek her an görebilmeli
int safe_capture_frame(const char* output_path) {
    pid_t pid = fork();

    if (pid == 0) {
        // Çocuk süreç: Kamera görüntüsünü yakala
        // Argümanlar ayrılmış durumda, komut enjeksiyonu imkansız!
        char *args[] = {"fswebcam", "-r", "640x480", "--no-banner", (char*)output_path, NULL};
        execvp("fswebcam", args);
        _exit(1); 
    } else if (pid > 0) {
        // Ana süreç: Sinek arka planda görmeye devam ediyor
        printf("[ANKA] Kamera tetiklendi: %s\n", output_path);
        return 0;
    }
    return -1;
}
