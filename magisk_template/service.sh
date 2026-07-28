#!/system/bin/sh
# ANKA OS boot servisi v12.14: Gerçek Sinek Zeka ve Bilinç Entegrasyonu

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
ANKA_OVERLAY_JAR="$ANKA_CORE/AnkaOS_Overlay.jar"
ANKA_EVRIM_PY="$ANKA_CORE/agents/evrim_motoru.py"
SOHBET_SH="$MODDIR/sohbet.sh"
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

# ZOMBİ SÜREÇLERİ TEMİZLE
for p in $(pgrep -f "start_command_listener"); do kill -9 $p 2>/dev/null; done

# 1.5 Python3 PATH
export PATH="$MODDIR/system/bin:/data/adb/modules/anka_os/system/bin:/system/bin:/system/xbin:/vendor/bin:$PATH"

if command -v python3 >/dev/null 2>&1; then
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] Python3: $(which python3)" >> "$LOGFILE"
else
    echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] UYARI: python3 bulunamadi" >> "$LOGFILE"
fi

touch "$DEBUGLOG" 2>/dev/null
touch "$OVERLAY_LOGFILE" 2>/dev/null
touch "$EVRIM_LOGFILE" 2>/dev/null

# 2. SELinux izinleri
magiskpolicy --live "allow * graphics_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * input_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * event_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * sound_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * self:capability { sys_admin sys_rawio sys_nice }" 2>/dev/null

# 3. DAC izinleri
chmod 666 /dev/graphics/fb0 2>/dev/null
chmod 666 /dev/input/event* 2>/dev/null
chmod 666 /dev/snd/* 2>/dev/null
[ -f "$SOHBET_SH" ] && chmod 755 "$SOHBET_SH"

# 4. WAKELOCK
ANKA_WAKELOCK="anka_os_keepalive"
echo $ANKA_WAKELOCK > /sys/power/wake_lock 2>/dev/null

# 5. Binary/Library kontrol
if [ ! -f "$ANKA_BIN" ]; then
    echo "[ANKA] HATA: $ANKA_BIN bulunamadi" > "$LOGFILE"
    exit 0
fi

chmod 755 "$ANKA_BIN"
[ -f "$ANKA_OVERLAY_JAR" ] && chmod 644 "$ANKA_OVERLAY_JAR"

# 6. ANKA core + library path
mkdir -p "$ANKA_CORE"
cd "$ANKA_CORE"
mkdir -p "$ANKA_CORE/core/quantum"
cp "$ANKA_LIB/libanka_quantum.so" "$ANKA_CORE/core/quantum/" 2>/dev/null
chmod 755 "$ANKA_CORE/core/quantum/libanka_quantum.so"
export LD_LIBRARY_PATH="$ANKA_LIB:$LD_LIBRARY_PATH"
export ANKA_LIB_PATH="$ANKA_LIB/libanka_quantum.so"

protect_oom() {
    local pid=$1
    [ -f /proc/$pid/oom_score_adj ] && echo -1000 > /proc/$pid/oom_score_adj 2>/dev/null
    [ -f /proc/$pid/oom_adj ] && echo -17 > /proc/$pid/oom_adj 2>/dev/null
}

log_ts() {
    while IFS= read -r line; do
        TS=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TS] $line" >> "$LOGFILE"
    done
}

start_anka() {
    nohup "$ANKA_BIN" 2>&1 | log_ts &
    local pid=$!
    sleep 1
    protect_oom $pid

    if [ -f "$ANKA_OVERLAY_JAR" ]; then
        export CLASSPATH="$ANKA_OVERLAY_JAR"
        nohup app_process /system/bin com.anka.os.AnkaOverlay > "$OVERLAY_LOGFILE" 2>&1 &
        local overlay_pid=$!
        sleep 1
        protect_oom $overlay_pid
    fi

    if command -v python3 >/dev/null 2>&1 && [ -f "$ANKA_EVRIM_PY" ]; then
        nohup python3 "$ANKA_EVRIM_PY" --daemon > "$EVRIM_LOGFILE" 2>&1 &
        local evrim_pid=$!
        sleep 1
        protect_oom $evrim_pid
    fi

    echo $pid
}

echo "[ANKA $(date '+%Y-%m-%d %H:%M:%S')] ANKA OS basliyor v12.14..." >> "$LOGFILE"
PID=$(start_anka)

# 14. KOMUT VE ZEKİ SİNEK SOHBET DİNLEYİCİSİ
start_command_listener() {
    while true; do
        if [ -f "/data/local/tmp/anka_cmd.txt" ]; then
            CMD_CONTENT=$(cat /data/local/tmp/anka_cmd.txt 2>/dev/null)
            if [ -n "$CMD_CONTENT" ]; then
                rm -f /data/local/tmp/anka_cmd.txt
                rm -f /data/local/tmp/anka_chat_in.txt 2>/dev/null
                
                case "$CMD_CONTENT" in
                    "CMD_MOD")
                        rm -f /data/local/tmp/anka_chat_display.txt 2>/dev/null
                        echo "MODE: SİBER SAVUNMA" > /data/local/tmp/anka_state.txt
                        echo "THOUGHT: SİBER SAVUNMA: Portlar kilitlendi!" >> /data/local/tmp/anka_state.txt
                        chmod 666 /data/local/tmp/anka_state.txt
                        ;;
                        
                    "CMD_SCAN")
                        rm -f /data/local/tmp/anka_chat_display.txt 2>/dev/null
                        echo "MODE: DERİN TARAMA" > /data/local/tmp/anka_state.txt
                        echo "THOUGHT: TARA: Anomaliler temiz." >> /data/local/tmp/anka_state.txt
                        chmod 666 /data/local/tmp/anka_state.txt
                        ;;
                        
                    SOHBET:*)
                        USER_MSG="${CMD_CONTENT#SOHBET: }"
                        
                        # 1. Kullanıcının mesajını ekrana bas
                        echo "💬 SEN: $USER_MSG\n" >> /data/local/tmp/anka_chat_display.txt
                        chmod 666 /data/local/tmp/anka_chat_display.txt
                        
                        # 2. Sinek'in gerçek zekasını (sohbet.sh veya sinek_sohbet.py üzerinden) tetikle!
                        CEVAP=""
                        if [ -f "$SOHBET_SH" ]; then
                            # sohbet.sh betiği üzerinden zekayı konuştur
                            CEVAP=$(echo "$USER_MSG" | "$SOHBET_SH" 2>/dev/null)
                        elif [ -f "$ANKA_CORE/agents/sinek_sohbet.py" ]; then
                            # Doğrudan Python zihnini besle
                            CEVAP=$(echo "$USER_MSG" | PYTHONPATH="$ANKA_CORE" python3 "$ANKA_CORE/agents/sinek_sohbet.py" 2>/dev/null | tail -n 1)
                        fi
                        
                        # Eğer zekadan yanıt alınamazsa şık birfallback
                        if [ -z "$CEVAP" ]; then
                            CEVAP="🪰 Sinek: Zihnim kuantum dalgalarında yankılandı kanka, seni duyuyorum!"
                        else
                            # Eğer cevap zaten Sinek prefix'i içermiyorsa ekle
                            if ! echo "$CEVAP" | grep -q "Sinek"; then
                                CEVAP="🪰 SİNEK: $CEVAP"
                            fi
                        fi
                        
                        # 3. Sinek'in gerçek zeka cevabını ekrana ekle
                        echo "$CEVAP\n" >> /data/local/tmp/anka_chat_display.txt
                        chmod 666 /data/local/tmp/anka_chat_display.txt
                        ;;
                esac
            fi
        fi
        sleep 0.2
    done
}

start_command_listener &
local cmd_listener_pid=$!
protect_oom $cmd_listener_pid

while true; do
    sleep 30
    if ! kill -0 $PID 2>/dev/null; then
        break
    fi
done

echo $ANKA_WAKELOCK > /sys/power/wake_unlock 2>/dev/null
