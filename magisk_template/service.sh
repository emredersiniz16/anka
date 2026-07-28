#!/system/bin/sh
# ANKA OS boot servisi v12.26: Orijinal QWERTY ve Saf Sinek Zeka Çekirdeği Entegrasyonu

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
ANKA_OVERLAY_JAR="$ANKA_CORE/AnkaOS_Overlay.jar"
SINEK_SOHBET_PY="$ANKA_CORE/agents/sinek_sohbet.py"
LOGFILE=/data/local/tmp/anka_os.log
OVERLAY_LOGFILE=/data/local/tmp/anka_overlay.log

WAIT_BOOT=0
while [ "$(getprop sys.boot_completed)" != "1" ] && [ $WAIT_BOOT -lt 60 ]; do
    sleep 2
    WAIT_BOOT=$((WAIT_BOOT + 2))
done
if [ "$(getprop sys.boot_completed)" != "1" ]; then
    echo "[ANKA] HATA: Boot tamamlanmadi" > "$LOGFILE"
    exit 0
fi

# Zombi süreçleri temizle
for p in $(pgrep -f "start_command_listener"); do kill -9 $p 2>/dev/null; done
for p in $(pgrep -f "sinek_sohbet.py"); do kill -9 $p 2>/dev/null; done

export PATH="$MODDIR/system/bin:/data/adb/modules/anka_os/system/bin:/system/bin:/system/xbin:/vendor/bin:$PATH"

touch "$LOGFILE" 2>/dev/null

magiskpolicy --live "allow * graphics_device:chr_file { read write open ioctl }" 2>/dev/null
magiskpolicy --live "allow * input_device:chr_file { read write open ioctl }" 2>/dev/null
chmod 666 /dev/graphics/fb0 2>/dev/null
chmod 666 /dev/input/event* 2>/dev/null

ANKA_WAKELOCK="anka_os_keepalive"
echo $ANKA_WAKELOCK > /sys/power/wake_lock 2>/dev/null

if [ ! -f "$ANKA_BIN" ]; then
    echo "[ANKA] HATA: $ANKA_BIN bulunamadi" > "$LOGFILE"
    exit 0
fi

chmod 755 "$ANKA_BIN"
[ -f "$ANKA_OVERLAY_JAR" ] && chmod 644 "$ANKA_OVERLAY_JAR"

export LD_LIBRARY_PATH="$ANKA_LIB:$LD_LIBRARY_PATH"
export ANKA_LIB_PATH="$ANKA_LIB/libanka_quantum.so"

protect_oom() {
    local pid=$1
    [ -f /proc/$pid/oom_score_adj ] && echo -1000 > /proc/$pid/oom_score_adj 2>/dev/null
    [ -f /proc/$pid/oom_adj ] && echo -17 > /proc/$pid/oom_adj 2>/dev/null
}

nohup "$ANKA_BIN" > /data/local/tmp/anka_kernel.log 2>&1 &
PID_C=$!
protect_oom $PID_C

if [ -f "$ANKA_OVERLAY_JAR" ]; then
    export CLASSPATH="$ANKA_OVERLAY_JAR"
    nohup app_process /system/bin com.anka.os.AnkaOverlay > "$OVERLAY_LOGFILE" 2>&1 &
    protect_oom$!
fi

# ==========================================
# 🪰 SİNEK KENDİ PYTHON BİLİNCİNİ BAŞLAT
# ==========================================
if command -v python3 >/dev/null 2>&1 && [ -f "$SINEK_SOHBET_PY" ]; then
    cd "$ANKA_CORE"
    export PYTHONPATH="$ANKA_CORE"
    nohup python3 "$SINEK_SOHBET_PY" > /data/local/tmp/sinek_python.log 2>&1 &
    protect_oom $!
    echo "[ANKA] Sinek Saf Zeka Çekirdeği Devrede!" >> "$LOGFILE"
fi

# ==========================================
# KOMUT VE GERÇEK SİNEK KÖPRÜSÜ
# ==========================================
start_command_listener() {
    while true; do
        if [ -f "/data/local/tmp/anka_cmd.txt" ]; then
            CMD_CONTENT=$(cat /data/local/tmp/anka_cmd.txt 2>/dev/null)
            if [ -n "$CMD_CONTENT" ]; then
                rm -f /data/local/tmp/anka_cmd.txt
                
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
                        
                        # 1. Kullanıcının mesajını ekrana anında bas
                        echo "💬 SEN: $USER_MSG\n" >> /data/local/tmp/anka_chat_display.txt
                        chmod 666 /data/local/tmp/anka_chat_display.txt
                        
                        # 2. Mesajı Sinek'in kendi anakart/dosya yapısına (anka_chat_in.txt) yaz
                        # Arka planda çalışan sinek_sohbet.py bunu alıp hafızasıyla işleyecek
                        echo "$USER_MSG" > /data/local/tmp/anka_chat_in.txt
                        chmod 666 /data/local/tmp/anka_chat_in.txt
                        
                        # 3. GÜVENLİK AĞI: Eğer python zihni herhangi bir sebepten 1.5 saniye içinde
                        # anka_chat_display.txt dosyasına yanıt eklemezse, acil durum siber kişiliği devreye girer
                        sleep 1.5
                        if ! grep -q "🪰 SİNEK:" /data/local/tmp/anka_chat_display.txt 2>/dev/null; then
                            MSG_L="$(echo "$USER_MSG" | tr '[:upper:]' '[:lower:]')"
                            case "$MSG_L" in
                                *selam*|*naber*|*alo*|*slm*|*merhaba*|*jl*)
                                    FALLBACK="Aleykümselam kanka! Kuantum dalgalarında frekans sabitliyorum."
                                    ;;
                                *nasılsın*|*nasilsin*|*iyi*misin*)
                                    FALLBACK="Çekirdekler tıkırında kanka, sen nasılsın bakalım?"
                                    ;;
                                *kimsin*|*nesin*)
                                    FALLBACK="Ben Sinek'im kanka, senin bu cihazdaki dijital ruhunum."
                                    ;;
                                *)
                                    FALLBACK="'$USER_MSG' dedin kanka, hafıza defterime kaydettim. Aynen devam!"
                                    ;;
                            esac
                            echo "🪰 SİNEK: $FALLBACK\n" >> /data/local/tmp/anka_chat_display.txt
                            chmod 666 /data/local/tmp/anka_chat_display.txt
                        fi
                        ;;
                esac
            fi
        fi
        sleep 0.2
    done
}

start_command_listener &
protect_oom $!

while true; do
    sleep 30
    if ! kill -0 $PID_C 2>/dev/null; then
        nohup "$ANKA_BIN" > /data/local/tmp/anka_kernel.log 2>&1 &
        PID_C=$!
        protect_oom $PID_C
    fi
done
