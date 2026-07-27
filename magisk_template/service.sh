#!/system/bin/sh
# ANKA OS boot servisi v12.2: Clean Overlay Mode + Otonom Canlı Evrim Bekçisi

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
ANKA_OVERLAY_JAR="$ANKA_CORE/AnkaOS_Overlay.jar"
ANKA_EVRIM_PY="$ANKA_CORE/agents/evrim_motoru.py"
LOGFILE=/data/local/tmp/anka_os.log
OVERLAY_LOGFILE=/data/local/tmp/anka_overlay.log
EVRIM_LOGFILE=/data/local/tmp/anka_evrim.log
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

# 1.5 Python3 PATH — Termux + Magisk modül dizini + fallback'ler
export PATH="/data/data/com.termux/files/usr/bin:$MODDIR/system/bin:/data/adb/modules/anka_os/system/bin:/system/bin:/system/xbin:/vendor/bin:$PATH"

# Python3 var mı kontrol et
if command -v python3 >/dev/null 2>&1; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Python3: $(which python3)" >> "$LOGFILE"
else
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] UYARI: python3 bulunamadi — C-only mod" >> "$LOGFILE"
fi

# Log dosyalarını oluştur
touch "$DEBUGLOG" 2>/dev/null
touch "$OVERLAY_LOGFILE" 2>/dev/null
touch "$EVRIM_LOGFILE" 2>/dev/null

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
    # 11.1 C Çekirdeğini Arka Planda Çalıştır
    nohup "$ANKA_BIN" 2>&1 | log_ts &
    local pid=$!
    sleep 1
    protect_oom $pid
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Sinek PID=$pid (OOM:-17)" >> "$LOGFILE"

    # 11.2 Java App_Process Overlay Katmanını Başlat
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

    # 11.3 Otonom Canlı Evrim Bekçisini Başlat (Hot-Reload / Kovan Senkronizasyonu)
    if command -v python3 >/dev/null 2>&1 && [ -f "$ANKA_EVRIM_PY" ]; then
        nohup python3 "$ANKA_EVRIM_PY" --daemon > "$EVRIM_LOGFILE" 2>&1 &
        local evrim_pid=$!
        sleep 1
        protect_oom $evrim_pid
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Otonom Evrim Bekcisi PID=$evrim_pid (OOM:-17) -> Log: $EVRIM_LOGFILE" >> "$LOGFILE"
    else
        echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] UYARI: Otonom Evrim Bekcisi baslatilamadi (Python3/Script yok)" >> "$LOGFILE"
    fi

    echo $pid
}

# 12. Log başlangıç
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ====================================" > "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ANKA OS basliyor (v12.2 Otonom Evrim Modu)..." >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] SELinux: $(getenforce)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Python3: $(which python3 2>/dev/null || echo YOK)" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Binary: $ANKA_BIN" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Overlay JAR: $ANKA_OVERLAY_JAR" >> "$LOGFILE"
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] OOM: -17 | WakeLock: $ANKA_WAKELOCK" >> "$LOGFILE"

# 13. Ortamı yapılandır ve Sineği başlat
configure_system_env
PID=$(start_anka)

# 14. KOMUT DİNLEYİCİ ARKA PLAN SERVİSİ (Arayüzden gelen tuş ve sohbet komutlarını işler)
start_command_listener() {
    CURRENT_MODE="KUANTUM SAVAŞI"
    
    while true; do
        if [ -f "/data/local/tmp/anka_cmd.txt" ]; then
            CMD_CONTENT=$(cat /data/local/tmp/anka_cmd.txt 2>/dev/null)
            if [ -n "$CMD_CONTENT" ]; then
                # Komutu işledikten sonra dosyayı sil
                rm -f /data/local/tmp/anka_cmd.txt
                
                case "$CMD_CONTENT" in
                    "CMD_MOD")
                        echo "[ANKA] Komut alindi: MOD degistiriliyor..." >> "$LOGFILE"
                        
                        # Mod döngüsü ve kuantum tozu güncellemesi
                        if [ "$CURRENT_MODE" = "KUANTUM SAVAŞI" ]; then
                            CURRENT_MODE="SİBER SAVUNMA"
                            NEW_DUST="6200"
                            NEW_THOUGHT="SİBER SAVUNMA: Duvarlar güçlendirildi, portlar kilitlendi!"
                        elif [ "$CURRENT_MODE" = "SİBER SAVUNMA" ]; then
                            CURRENT_MODE="OTONOM GÖZLEM"
                            NEW_DUST="7550"
                            NEW_THOUGHT="OTONOM GÖZLEM: Frekans dalgaları taranıyor, izler silindi."
                        else
                            CURRENT_MODE="KUANTUM SAVAŞI"
                            NEW_DUST="5515"
                            NEW_THOUGHT="KUANTUM SAVAŞI: Frekans tarayıcı ve gizleme aktif! +1000 Toz!"
                        fi
                        
                        # Anlık durumu state dosyasına yaz ki Java arayüzü anında yakalasın
                        echo "TIME: $(date '+%H:%M:%S')" > /data/local/tmp/anka_state.txt
                        echo "BATTERY: $(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo '75')" >> /data/local/tmp/anka_state.txt
                        echo "DUST: $NEW_DUST" >> /data/local/tmp/anka_state.txt
                        echo "MODE: $CURRENT_MODE" >> /data/local/tmp/anka_state.txt
                        echo "THOUGHT: $NEW_THOUGHT" >> /data/local/tmp/anka_state.txt
                        chmod 666 /data/local/tmp/anka_state.txt
                        ;;
                        
                    "CMD_SCAN")
                        echo "[ANKA] Komut alindi: Sistem taraniyor..." >> "$LOGFILE"
                        
                        # Tarama simülasyonu
                        echo "TIME: $(date '+%H:%M:%S')" > /data/local/tmp/anka_state.txt
                        echo "BATTERY: $(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo '75')" >> /data/local/tmp/anka_state.txt
                        echo "DUST: 8900" >> /data/local/tmp/anka_state.txt
                        echo "MODE: DERİN TARAMA" >> /data/local/tmp/anka_state.txt
                        echo "THOUGHT: TARA: Çevrede anomaliler inceleniyor... Sistem temiz komutanım." >> /data/local/tmp/anka_state.txt
                        chmod 666 /data/local/tmp/anka_state.txt
                        ;;
                        
                    SOHBET:*)
                        USER_MSG="${CMD_CONTENT#SOHBET: }"
                        echo "[ANKA] Sinek'e mesaj gonderiliyor: $USER_MSG" >> "$LOGFILE"
                        
                        if [ -f "$ANKA_CORE/agents/sinek_sohbet.py" ]; then
                            PYTHONPATH="$ANKA_CORE" python3 "$ANKA_CORE/agents/sinek_sohbet.py" "$USER_MSG" >> "$LOGFILE" 2>&1
                        else
                            # Fallback: Python scripti yoksa bile anında ekrana yansıt
                            echo "TIME: $(date '+%H:%M:%S')" > /data/local/tmp/anka_state.txt
                            echo "BATTERY: $(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo '75')" >> /data/local/tmp/anka_state.txt
                            echo "DUST: 5515" >> /data/local/tmp/anka_state.txt
                            echo "MODE: SOHBET MODU" >> /data/local/tmp/anka_state.txt
                            echo "THOUGHT: Sinek: '$USER_MSG' dedin komutanım, emir alınmıştır." >> /data/local/tmp/anka_state.txt
                            chmod 666 /data/local/tmp/anka_state.txt
                        fi
                        ;;
                esac
            fi
        fi
        sleep 0.5
    done
}

# Komut dinleyiciyi arka planda başlat
start_command_listener &
local cmd_listener_pid=$!
protect_oom $cmd_listener_pid
echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Komut Dinleyici PID=$cmd_listener_pid (OOM:-17)" >> "$LOGFILE"

# 15. WATCHDOG
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
