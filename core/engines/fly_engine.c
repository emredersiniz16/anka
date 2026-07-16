// core/engines/fly_engine.c - ENTEGRE VE GÜNCEL (Final)
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

typedef enum {
    FLY_IDLE, FLY_THINK, FLY_WAIT, FLY_GHOST, FLY_MIRROR
} FlyState;

// Global durum, UI Engine tarafından okunacak
FlyState current_state = FLY_IDLE;

// SİSTEM ZEKASI İLE BAĞLANTI
bool check_danger_level() {
    // Sinek, sistemin kara kutusunu (debug.log) dinliyor
    return system("grep -q 'JAMMER_AKTİF' /data/local/tmp/debug.log") == 0;
}

void update_fly_behavior() {
    // 1. Otonom Karar Mekanizması: Sinek artık durumuna kendi karar veriyor
    if (check_danger_level()) {
        current_state = FLY_GHOST; 
    } else if (system("grep -q 'USER_INPUT' /data/local/tmp/debug.log") == 0) {
        current_state = FLY_MIRROR;
    } else {
        current_state = FLY_IDLE;
    }

    // 2. Durum Uygulama: Sinek felsefesine göre donanım tepkisi
    switch(current_state) {
        case FLY_IDLE:
            // Pusu modu: Nexus nabzını koru, sistem uyanık kalsın (Yol güncellendi)
            system("su -c 'python3 agents/sinek_nexus.py --pulse &'");
            break;

        case FLY_THINK:
            // Arka planda veri işleniyor, Sinek işlemci gücüne odaklandı
            break;

        case FLY_WAIT:
            // Komut bekleme: RAM koruma modu
            break;

        case FLY_GHOST:
            // GHOST modu: Kaynakları boşalt, iz bırakma
            system("sync; echo 3 > /proc/sys/vm/drop_caches");
            system("pkill -f 'python3 agents/sinek_nexus.py'"); // Nexus'u pusu modunda dondur (Yol güncellendi)
            break;

        case FLY_MIRROR:
            // MIRROR modu: Kullanıcı niyetini yansıt (Nexus tam güç - Yol güncellendi)
            system("su -c 'python3 agents/sinek_nexus.py --full-power &'");
            break;
    }
}
