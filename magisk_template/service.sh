#!/system/bin/sh
# ANKA OS boot servisi v12.1: Clean Overlay Mode + Overlay Log Yönlendirmesi

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
ANKA_OVERLAY_JAR="$ANKA_CORE/AnkaOS_Overlay.jar"
LOGFILE=/data/local/tmp/anka_os.log
OVERLAY_LOGFILE=/data/local/tmp/anka_overlay.log
KOVANLOG=/cache/anka_os_kovan.log
DEBUGLOG=/data/local/tmp/debug.log

# 1. Boot bekle
WAIT_BOOT=0
while [ "$(getprop sys.boot_completed)" != "1" ] && [ $WAIT_BOOT -lt 60 ]; do
    sleep 2
    WAIT_BOOT=$((WAIT_BOOT + 2))
done
if [ "$(getprop sys.boot_completed)" != "1" ]; then
    echo "[ANKA] HATA: Boot tamamlanmadi" > "$LOGFILE"
    exit 0
fi

# 1.5 Python3 PATH — Magisk modül dizini + fallback'ler
export PATH="$MODDIR/system/bin:/data/adb/modules/anka_os/system/bin:/system/bin:/system/xbin:/vendor/bin:$PATH"

# Python3 var mı kontrol et
if command -v python3 >/dev/null 2>&1; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Python3: $(which python3)" >> "$LOGFILE"
else
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] UYARI: python3 bulunamadi — C-only mod" >> "$LOGFILE"
fi

# debug.log oluştur (fly_engine.c patlamasın)
touch "$DEBUGLOG" 2>/dev/null
touch "$OVERLAY_LOGFILE" 2>/dev/null

# 2. SELinux
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
magiskpolicy --live "allow * power_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * wake_lock:chr_file { read write open ioctl }" 2>/dev/null

# 3. DAC izinleri
chmod 666 /dev/graphics/fb0 2>/dev/null
chmod 666 /dev/input/event* 2>/dev/null
chmod 666 /dev/snd/* 2>/dev/null
chmod 666 /sys/power/wake_lock 2>/dev/null
chmod 666 /sys/power/wake_unlock 2>/dev/null
# MIUI Tema Uyumluluk Hatasını Engelle
mkdir -p /data/system/theme_config 2>/dev/null
touch /data/system/theme_config/theme_compatibility.xml 2>/dev/null
chmod 666 /data/system/theme_config/theme_compatibility.xml 2>/dev/null


# 4. WAKELOCK
ANKA_WAKELOCK="anka_os_keepalive"
echo $ANKA_WAKELOCK > /sys/power/wake_lock 2>/dev/null

# 5. Binary/Library kontrol
if [ ! -f "$ANKA_BIN" ]; then
    echo "[ANKA] HATA: $ANKA_BIN bulunamadi" > "$LOGFILE"
    exit 0
fi
if [ ! -f "$ANKA_LIB/libanka_quantum.so" ]; then
    echo "[ANKA] HATA: libanka_quantum.so bulunamadi" > "$LOGFILE"
    exit 0
fi

# 6. İzinler
chmod 755 "$ANKA_BIN"
chmod 755 "$ANKA_LIB/libanka_quantum.so"
[ -f "$ANKA_OVERLAY_JAR" ] && chmod 644 "$ANKA_OVERLAY_JAR"

# 7. ANKA core + library path
mkdir -p "$ANKA_CORE"
cd "$ANKA_CORE"
mkdir -p "$ANKA_CORE/core/quantum"
cp "$ANKA_LIB/libanka_quantum.so" "$ANKA_CORE/core/quantum/" 2>/dev/null
chmod 755 "$ANKA_CORE/core/quantum/libanka_quantum.so"
export LD_LIBRARY_PATH="$ANKA_LIB:$LD_LIBRARY_PATH"
export ANKA_LIB_PATH="$ANKA_LIB/libanka_quantum.so"

# 8. OOM koruma
protect_oom() {
    local pid=$1
    [ -f /proc/$pid/oom_score_adj ] && echo -1000 > /proc/$pid/oom_score_adj 2>/dev/null
    [ -f /proc/$pid/oom_adj ] && echo -17 > /proc/$pid/oom_adj 2>/dev/null
}

# 9. Log fonksiyonu
log_ts() {
    while IFS= read -r line; do
        TS=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TS] $line" >> "$LOGFILE"
        echo "[$TS] $line" >> "$KOVANLOG" 2>/dev/null
    done
}

# 10. Sistem Ayarları Yapılandırması
configure_system_env() {
    settings put global system_screen_off_timeout 2147483647 2>/dev/null
    cmd lock_settings set-disabled true 2>/dev/null
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Sistem ortam ayarları sabitlendi" >> "$LOGFILE"
}

# 11. Süreç başlat
start_anka() {
    # C Çekirdeğini Arka Planda Çalıştır
    nohup "$ANKA_BIN" 2>&1 | log_ts &
    local pid=$!
    sleep 1
    protect_oom $pid
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Sinek PID=$pid (OOM:-17)" >> "$LOGFILE"

    # Java App_Process Overlay Katmanını Başlat (Loglar /data/local/tmp/anka_overlay.log dosyasına aktarılır)
    if [ -f "$ANKA_OVERLAY_JAR" ]; then
        export CLASSPATH="$ANKA_OVERLAY_JAR"
        nohup app_process /system/bin com.anka.os.AnkaOverlay > "$OVERLAY_LOGFILE" 2>&1 &
        local overlay_pid=$!
        sleep 1
        protect_oom $overlay_pid
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Java Overlay PID=$overlay_pid (OOM:-17) -> Log: $OVERLAY_LOGFILE" >> "$LOGFILE"
    else
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] UYARI: $ANKA_OVERLAY_JAR bulunamadi!" >> "$LOGFILE"
    fi

    echo $pid
}

# 12. Log başlangıç
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ====================================" > "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ANKA OS basliyor (v12.1 Clean Overlay Modu)..." >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] SELinux: $(getenforce)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Python3: $(which python3 2>/dev/null || echo YOK)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Binary: $ANKA_BIN" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Overlay JAR: $ANKA_OVERLAY_JAR" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] OOM: -17 | WakeLock: $ANKA_WAKELOCK" >> "$LOGFILE"

# 13. Ortamı yapılandır ve Sineği başlat
configure_system_env
PID=$(start_anka)

# 14. WATCHDOG
WATCHDOG_RESTART=0
MAX_RESTART=5
while [ $WATCHDOG_RESTART -lt $MAX_RESTART ]; do
    sleep 10
    grep -q "$ANKA_WAKELOCK" /sys/power/wake_lock 2>/dev/null || echo $ANKA_WAKELOCK > /sys/power/wake_lock 2>/dev/null
    
    if ! kill -0 $PID 2>/dev/null; then
        WATCHDOG_RESTART=$((WATCHDOG_RESTART + 1))
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] WATCHDOG: öldü ($WATCHDOG_RESTART/$MAX_RESTART)" >> "$LOGFILE"
        [ $WATCHDOG_RESTART -lt $MAX_RESTART ] && sleep 30 && PID=$(start_anka)
    fi
done

echo $ANKA_WAKELOCK > /sys/power/wake_unlock 2>/dev/null
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Tamamlandi" >> "$LOGFILE"
