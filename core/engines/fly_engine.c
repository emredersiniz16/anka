// core/engines/fly_engine.c - ENTEGRE VE GÜNCEL (Düzeltilmiş)
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include "fly_engine.h" // Kendi header'ına bağımlı hale getirildi

// Global durum (header'da tanımlı olanın gerçek değeri)
FlyState current_state = FLY_IDLE;

// SİSTEM ZEKASI İLE BAĞLANTI (static ile sadece bu dosyaya özel kıldık)
static bool check_danger_level() {
    return system("grep -q 'JAMMER_AKTİF' /data/local/tmp/debug.log") == 0;
}

void update_fly_behavior() {
    // 1. Otonom Karar Mekanizması
    if (check_danger_level()) {
        current_state = FLY_GHOST; 
    } else if (system("grep -q 'USER_INPUT' /data/local/tmp/debug.log") == 0) {
        current_state = FLY_MIRROR;
    } else {
        current_state = FLY_IDLE;
    }

    // 2. Durum Uygulama
    switch(current_state) {
        case FLY_IDLE:
            system("su -c 'python3 agents/sinek_nexus.py --pulse > /dev/null 2>&1 &'");
            break;

        case FLY_GHOST:
            system("sync; echo 3 > /proc/sys/vm/drop_caches");
            system("pkill -f 'agents/sinek_nexus.py'"); 
            break;

        case FLY_MIRROR:
            system("su -c 'python3 agents/sinek_nexus.py --full-power > /dev/null 2>&1 &'");
            break;
            
        case FLY_THINK:
        case FLY_WAIT:
        default:
            break;
    }
}
