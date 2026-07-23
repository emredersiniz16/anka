// sinek_warfare.c - ANKA OS: SİNEK TAKTİKSEL SAVAŞ VE KUM HAVUZU
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <stdbool.h>
#include <sys/types.h>
#include <sys/wait.h>

// MIUI SurfaceFlinger'ın Process ID'sini bulur
static pid_t find_surfaceflinger_pid() {
    FILE *fp = popen("pidof surfaceflinger", "r");
    if (!fp) return -1;
    
    char buf[32] = {0};
    if (fgets(buf, sizeof(buf), fp) != NULL) {
        pclose(fp);
        return (pid_t)atoi(buf);
    }
    pclose(fp);
    return -1;
}

// KUM HAVUZU TESTİ: Çökmeden dondurma yapabiliyor muyuz?
bool sinek_sandbox_test(pid_t sf_pid) {
    fprintf(stderr, "🛡️ [SİNEK]: Kum Havuzu Testi Başlatılıyor... Hedef PID: %d\n", sf_pid);
    
    // 1. Taktik: Dondur (Öldürme!)
    if (kill(sf_pid, SIGSTOP) == 0) {
        fprintf(stderr, "🛡️ [SİNEK]: MIUI donduruldu. Android uyutuldu (Panic tetiklenmedi).\n");
        
        // Sinek 1 saniye bekler, sistemin çöküp çökmediğini dinler
        usleep(1000000); 
        
        // 2. Taktik: Çöz (Test başarılı, sistemi geri ver)
        kill(sf_pid, SIGCONT);
        fprintf(stderr, "🛡️ [SİNEK]: MIUI uyandırıldı. Kum Havuzu testi BAŞARILI!\n");
        return true;
    }
    
    fprintf(stderr, "⚠️ [SİNEK]: Dondurma başarısız! Yetki reddedildi veya hedef yok.\n");
    return false;
}

// ANA SAVAŞ FONKSİYONU: Gerçek Devralma
int sinek_execute_takeover() {
    fprintf(stderr, "⚔️ [SİNEK]: Savaş Protokolü Aktif. MIUI By-Pass Ediliyor.\n");

    pid_t sf_pid = find_surfaceflinger_pid();
    if (sf_pid <= 0) {
        fprintf(stderr, "⚠️ [SİNEK]: Düşman bulunamadı (SurfaceFlinger yok). Zaten yalnızım.\n");
        return 0; // Zaten bizde
    }

    // Önce Kum Havuzunda güvenliği test et
    if (!sinek_sandbox_test(sf_pid)) {
        fprintf(stderr, "⚠️ [SİNEK]: Taktiksel geri çekilme. Çökme riski var, gölge modda kalıyorum.\n");
        return -1; // Riski gördü, vazgeçti (Telefon kapanmaz)
    }

    // Test başarılıysa, GERÇEK SALDIRI
    fprintf(stderr, "⚔️ [SİNEK]: SİSTEM KİLİTLENİYOR...\n");
    
    // Zamanı dondur!
    kill(sf_pid, SIGSTOP);
    
    // Ekrana glitch atacak zamanımız var (Burada boot.c'deki ui_render devreye girecek)
    return sf_pid; // PID'yi döndür ki kapanışta geri açabilelim
}

// KAPANIŞ: MIUI'ı geri ver (Güvenli Çıkış)
void sinek_retreat(pid_t sf_pid) {
    if (sf_pid > 0) {
        fprintf(stderr, "🛡️ [SİNEK]: Anka OS kapanıyor. MIUI serbest bırakılıyor...\n");
        kill(sf_pid, SIGCONT); // Sistemi uyandır, telefon normale dönsün
    }
}
