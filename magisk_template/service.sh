#!/system/bin/sh
# ANKA OS boot servisi - late_start sonrasi calisir
# DÜZELTME v5: OOM korumasi (-17) + Watchdog (sürekli izleme)
#              SELinux Enforcing — setenforce 0 YOK.

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
LOGFILE=/data/adb/anka_os.log

# 1. Boot tamamlanana kadar bekle (bootloop önlemi)
WAIT_BOOT=0
while [ "$(getprop sys.boot_completed)" != "1" ] && [ $WAIT_BOOT -lt 60 ]; do
    sleep 2
    WAIT_BOOT=$((WAIT_BOOT + 2))
done

if [ "$(getprop sys.boot_completed)" != "1" ]; then
    echo "[ANKA $(date '+%H:%M:%S')] HATA: Boot tamamlanmadi, sinek baslatilmiyor" > "$LOGFILE"
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

# 3. Framebuffer + input + sound DAC izinleri
chmod 666 /dev/graphics/fb0 2>/dev/null
chmod 666 /dev/input/event* 2>/dev/null
chmod 666 /dev/snd/* 2>/dev/null

# 4. Binary/Library kontrol
if [ ! -f "$ANKA_BIN" ]; then
    echo "[ANKA $(date '+%H:%M:%S')] HATA: $ANKA_BIN bulunamadi" >> "$LOGFILE"
    exit 0
fi
if [ ! -f "$ANKA_LIB/libanka_quantum.so" ]; then
    echo "[ANKA $(date '+%H:%M:%S')] HATA: libanka_quantum.so bulunamadi" >> "$LOGFILE"
    exit 0
fi

# 5. İzinler
chmod 755 "$ANKA_BIN"
chmod 755 "$ANKA_LIB/libanka_quantum.so"

# 6. ANKA core dizini + library path
mkdir -p "$ANKA_CORE"
cd "$ANKA_CORE"
mkdir -p "$ANKA_CORE/core/quantum"
cp "$ANKA_LIB/libanka_quantum.so" "$ANKA_CORE/core/quantum/" 2>/dev/null
chmod 755 "$ANKA_CORE/core/quantum/libanka_quantum.so"
export LD_LIBRARY_PATH="$ANKA_LIB:$LD_LIBRARY_PATH"
export ANKA_LIB_PATH="$ANKA_LIB/libanka_quantum.so"

# 7. OOM Killer'dan koruma fonksiyonu
#    oom_adj=-17 → OOM killer bu süreci öldürmez (dokunulmaz)
#    oom_score_adj=-1000 → modern kernel için aynı etki
protect_oom() {
    local pid=$1
    if [ -f /proc/$pid/oom_score_adj ]; then
        echo -1000 > /proc/$pid/oom_score_adj 2>/dev/null
    fi
    if [ -f /proc/$pid/oom_adj ]; then
        echo -17 > /proc/$pid/oom_adj 2>/dev/null
    fi
}

# 8. Süreç başlatma fonksiyonu (OOM koruması ile)
start_anka() {
    nohup "$ANKA_BIN" >> "$LOGFILE" 2>&1 &
    local pid=$!
    sleep 1
    protect_oom $pid
    echo "[ANKA $(date '+%H:%M:%S')] Sinek baslatildi PID=$PID (OOM: korumali)" >> "$LOGFILE"
    echo $pid
}

# 9. Log başlangıcı
echo "[ANKA $(date '+%H:%M:%S')] ====================================" > "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] ANKA OS baslatiliyor..." >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] SELinux: $(getenforce) (Enforcing + magiskpolicy)" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Binary: $ANKA_BIN" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Library: $ANKA_LIB/libanka_quantum.so" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Core: $ANKA_CORE" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Boot: $(getprop sys.boot_completed)" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] OOM: -17 (dokunulmaz mod aktif)" >> "$LOGFILE"

# 10. Sineği başlat
PID=$(start_anka)

# 11. WATCHDOG — sürekli izleme döngüsü
#     - anka_os_bin çökerse yeniden başlat
#     - python3 ajanı çökerse anka_os_bin'i restart et (ankö python3'ü o başlatıyor)
#     - Maksimum 5 restart (sonra pes et, bootloop riski)
WATCHDOG_RESTART=0
MAX_RESTART=5
CRASH_COOLDOWN=30   # 30 sn bekleme (rapid crash loop önlemi)

while [ $WATCHDOG_RESTART -lt $MAX_RESTART ]; do
    sleep 10

    # anka_os_bin hâlâ ayakta mı?
    if ! kill -0 $PID 2>/dev/null; then
        WATCHDOG_RESTART=$((WATCHDOG_RESTART + 1))
        echo "[ANKA $(date '+%H:%M:%S')] WATCHDOG: anka_os_bin öldü (restart $WATCHDOG_RESTART/$MAX_RESTART)" >> "$LOGFILE"

        if [ $WATCHDOG_RESTART -lt $MAX_RESTART ]; then
            echo "[ANKA $(date '+%H:%M:%S')] Cooldown: ${CRASH_COOLDOWN}s bekleniyor..." >> "$LOGFILE"
            sleep $CRASH_COOLDOWN
            PID=$(start_anka)
        else
            echo "[ANKA $(date '+%H:%M:%S')] WATCHDOG: Max restart asildi, pes edildi" >> "$LOGFILE"
        fi
        continue
    fi

    # anka_os_bin ayakta ama python3 ajanı var mı?
    # (anka_os_bin python3'ü fork ile başlatır — o ölünce buradan anlarız)
    PYTHON_PIDS=$(pgrep -f "python3.*sinek" 2>/dev/null)
    if [ -z "$PYTHON_PIDS" ]; then
        # Python ajanı yok — ama anka_os_bin hâlâ çalışıyor olabilir
        # Sadece anka_os_bin 60+ saniyedir ayakta ama python yoksa restart
        sleep 5
        PYTHON_PIDS=$(pgrep -f "python3.*sinek" 2>/dev/null)
        if [ -z "$PYTHON_PIDS" ] && kill -0 $PID 2>/dev/null; then
            echo "[ANKA $(date '+%H:%M:%S')] WATCHDOG: Python ajanı bulunamadi, anka_os_bin restart ediliyor" >> "$LOGFILE"
            kill $PID 2>/dev/null
            sleep 2
            PID=$(start_anka)
        fi
    fi
done

echo "[ANKA $(date '+%H:%M:%S')] Watchdog tamamlandi — sistem stabil veya pes edildi" >> "$LOGFILE"
