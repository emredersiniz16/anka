#!/system/bin/sh
# ANKA OS boot servisi - Cihaz tamamen açıldıktan sonra tetiklenir
MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
LOGFILE=/data/adb/anka_os.log

# KRİTİK EKLENTİ: Termux kütüphanelerini boot ortamına zorla tanıtıyoruz
# Bu olmazsa C çekirdeği (anka_os_bin) çalışırken çöker ve bootloop yapar!
export PREFIX=/data/data/com.termux/files/usr
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib

# Zaten çalışıyorsa iki kere tetiklenmesin
if pgrep -f "anka_os_bin" > /dev/null; then
    echo "[ANKA $(date '+%H:%M:%S')] Zaten çalistiriliyor, atlanıyor." >> "$LOGFILE"
    exit 0
fi

# Android'in tamamen açılmasını ve arayüzün yüklenmesini arkaplanda bekle
(
    # 1. KURAL: Android kilit ekranı/ana ekran gelene kadar güvenle bekle
    # Bu kontrol, Anka OS UI motoru ile Android SurfaceFlinger'ın çakışmasını %100 önler
    while [ "$(getprop sys.boot_completed)" != "1" ]; do
        sleep 5
    done
    
    # 2. KURAL: Sistem kendine geldikten sonra donanıma girmek için 10 saniye bekle
    sleep 10

    echo "[ANKA $(date '+%H:%M:%S')] Android sistemi tamamen hazir. Bagimliliklar kontrol ediliyor..." >> "$LOGFILE"

    # Termux python3 kontrolü (Maksimum 30 saniye daha bekle)
    WAIT=0
    while [ ! -f /data/data/com.termux/files/usr/bin/python3 ] && [ $WAIT -lt 30 ]; do
        sleep 2
        WAIT=$((WAIT + 2))
    done

    if [ ! -f /data/data/com.termux/files/usr/bin/python3 ]; then
        echo "[ANKA $(date '+%H:%M:%S')] HATA: Termux python3 bulunamadi" >> "$LOGFILE"
        exit 1
    fi

    if [ ! -f "$ANKA_BIN" ]; then
        echo "[ANKA $(date '+%H:%M:%S')] HATA: $ANKA_BIN bulunamadi" >> "$LOGFILE"
        exit 1
    fi

    chmod 755 "$ANKA_BIN"

    # Assets dizinine gec (yoksa modül kökünden devam et)
    if [ -d "$MODDIR/system/anka_core" ]; then
        cd "$MODDIR/system/anka_core"
    else
        cd "$MODDIR" || exit 1
    fi

    echo "[ANKA $(date '+%H:%M:%S')] Anka OS Guvenli Modda Baslatiliyor..." >> "$LOGFILE"
    
    # Kökten ayırma (setsid veya nohup) ile boot sürecinden bağımsız kılma
    if command -v setsid > /dev/null; then
        setsid "$ANKA_BIN" >> "$LOGFILE" 2>&1 &
    else
        nohup "$ANKA_BIN" >> "$LOGFILE" 2>&1 &
    fi

    echo "[ANKA $(date '+%H:%M:%S')] Baslatma komutu arkaplana firlatildi. PID: $!" >> "$LOGFILE"
) &
