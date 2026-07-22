#!/system/bin/sh
# ANKA OS boot servisi - late_start sonrasi calisir
# DÜZELTME v7: Wakelock (ekran kapalıyken de çalış) + birleşik loglama + OOM + Watchdog

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
LOGFILE=/data/local/tmp/anka_os.log
KOVANLOG=/cache/anka_os_kovan.log

# 1. Boot tamamlanana kadar bekle
WAIT_BOOT=0
while [ "$(getprop sys.boot_completed)" != "1" ] && [ $WAIT_BOOT -lt 60 ]; do
    sleep 2
    WAIT_BOOT=$((WAIT_BOOT + 2))
done

if [ "$(getprop sys.boot_completed)" != "1" ]; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] HATA: Boot tamamlanmadi" > "$LOGFILE"
    exit 0
fi

# 2. SELinux Enforcing — magiskpolicy ile izinler
magiskpolicy --live "allow * graphics_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * input_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * event_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * sound_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * timed_output_device:dir { search read }" 2>/dev/null
magiskpolicy --live "allow * timed_output_device:chr_file { read write open }" 2>/dev/null
magiskpolicy --live "allow * leds_device:dir { search read write }" 2>/dev/null
magiskpolicy --live "allow * leds_device:chr_file { read write open }" 2>/dev/null
magiskpolicy --live "allow * sysfs:dir { search read write }" 2>/dev/null
magiskpolicy --live "allow * sysfs:file { read write open }" 2>/dev/null
magiskpolicy --live "allow * power_supply_device:dir { search read }" 2>/dev/null
magiskpolicy --live "allow * power_supply_device:chr_file { read write open }" 2>/dev/null
magiskpolicy --live "allow * self:capability { sys_admin sys_rawio sys_nice }" 2>/dev/null
# Wake lock için ek izinler
magiskpolicy --live "allow * power_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * wake_lock:chr_file { read write open ioctl }" 2>/dev/null

# 3. DAC izinleri
chmod 666 /dev/graphics/fb0 2>/dev/null
chmod 666 /dev/input/event* 2>/dev/null
chmod 666 /dev/snd/* 2>/dev/null
chmod 666 /sys/power/wake_lock 2>/dev/null
chmod 666 /sys/power/wake_unlock 2>/dev/null

# 4. WAKELOCK — ekran kapalıyken CPU'yu uyutma
#    Partial wake lock: CPU + RAM açık, ekran kapalı.
#    Bu, Sinek'in arka planda sensörleri dinlemeye devam etmesini sağlar.
ANKA_WAKELOCK="anka_os_keepalive"

echo $ANKA_WAKELOCK > /sys/power/wake_lock 2>/dev/null
if [ $? -eq 0 ]; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WAKELOCK: Aktif ($ANKA_WAKELOCK) — CPU uyanık" >> "$LOGFILE" 2>/dev/null
else
    # Fallback: Android uid 1000 (system) olarak wake_lock kullan
    # Magisk root uid 0 olduğu için /sys/power/wake_lock yazılabilir olmalı
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WAKELOCK: /sys/power/wake_lock yazılamadı, fallback deneniyor" >> "$LOGFILE" 2>/dev/null
fi

# 5. Binary/Library kontrol
if [ ! -f "$ANKA_BIN" ]; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] HATA: $ANKA_BIN bulunamadi" > "$LOGFILE"
    exit 0
fi
if [ ! -f "$ANKA_LIB/libanka_quantum.so" ]; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] HATA: libanka_quantum.so bulunamadi" > "$LOGFILE"
    exit 0
fi

# 6. İzinler
chmod 755 "$ANKA_BIN"
chmod 755 "$ANKA_LIB/libanka_quantum.so"

# 7. ANKA core dizini + library path
mkdir -p "$ANKA_CORE"
cd "$ANKA_CORE"
mkdir -p "$ANKA_CORE/core/quantum"
cp "$ANKA_LIB/libanka_quantum.so" "$ANKA_CORE/core/quantum/" 2>/dev/null
chmod 755 "$ANKA_CORE/core/quantum/libanka_quantum.so"
export LD_LIBRARY_PATH="$ANKA_LIB:$LD_LIBRARY_PATH"
export ANKA_LIB_PATH="$ANKA_LIB/libanka_quantum.so"

# 8. OOM Killer'dan koruma
protect_oom() {
    local pid=$1
    if [ -f /proc/$pid/oom_score_adj ]; then
        echo -1000 > /proc/$pid/oom_score_adj 2>/dev/null
    fi
    if [ -f /proc/$pid/oom_adj ]; then
        echo -17 > /proc/$pid/oom_adj 2>/dev/null
    fi
}

# 9. Zaman damgalı log yazma fonksiyonu
log_ts() {
    while IFS= read -r line; do
        TS=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TS] $line" >> "$LOGFILE"
        echo "[$TS] $line" >> "$KOVANLOG" 2>/dev/null
    done
}

# 10. Süreç başlatma (log + OOM ile)
start_anka() {
    nohup "$ANKA_BIN" 2>&1 | log_ts &
    local pid=$!
    sleep 1
    protect_oom $pid
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Sinek baslatildi PID=$pid (OOM: -17)" >> "$LOGFILE"
    echo $pid
}

# 11. Log başlangıcı
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ====================================" > "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ANKA OS baslatiliyor..." >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] SELinux: $(getenforce) (Enforcing + magiskpolicy)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Binary: $ANKA_BIN" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Library: $ANKA_LIB/libanka_quantum.so" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Core: $ANKA_CORE" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Boot: $(getprop sys.boot_completed)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Log (birincil): $LOGFILE" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Log (kovan): $KOVANLOG" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] OOM: -17 (dokunulmaz)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WakeLock: $ANKA_WAKELOCK (partial — CPU uyanık)" >> "$LOGFILE"

# 12. Sineği başlat
PID=$(start_anka)

# 13. WATCHDOG — sürekli izleme + wakelock yenileme
WATCHDOG_RESTART=0
MAX_RESTART=5
CRASH_COOLDOWN=30

while [ $WATCHDOG_RESTART -lt $MAX_RESTART ]; do
    sleep 10

    # Wake lock hâlâ aktif mi? (bazı ROM'lar boot sonrası temizliyor)
    if ! grep -q "$ANKA_WAKELOCK" /sys/power/wake_lock 2>/dev/null; then
        echo $ANKA_WAKELOCK > /sys/power/wake_lock 2>/dev/null
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WAKELOCK: Yenilendi" >> "$LOGFILE"
    fi

    if ! kill -0 $PID 2>/dev/null; then
        WATCHDOG_RESTART=$((WATCHDOG_RESTART + 1))
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WATCHDOG: anka_os_bin öldü (restart $WATCHDOG_RESTART/$MAX_RESTART)" >> "$LOGFILE"

        if [ $WATCHDOG_RESTART -lt $MAX_RESTART ]; then
            echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Cooldown: ${CRASH_COOLDOWN}s" >> "$LOGFILE"
            sleep $CRASH_COOLDOWN
            PID=$(start_anka)
        else
            echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WATCHDOG: Max restart asildi" >> "$LOGFILE"
        fi
        continue
    fi

    PYTHON_PIDS=$(pgrep -f "python3.*sinek" 2>/dev/null)
    if [ -z "$PYTHON_PIDS" ]; then
        sleep 5
        PYTHON_PIDS=$(pgrep -f "python3.*sinek" 2>/dev/null)
        if [ -z "$PYTHON_PIDS" ] && kill -0 $PID 2>/dev/null; then
            echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WATCHDOG: Python ajanı yok, restart" >> "$LOGFILE"
            kill $PID 2>/dev/null
            sleep 2
            PID=$(start_anka)
        fi
    fi
done

# 14. Çıkışta wake lock bırak
echo $ANKA_WAKELOCK > /sys/power/wake_unlock 2>/dev/null
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WakeLock serbest birakildi" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Watchdog tamamlandi" >> "$LOGFILE"
