#!/system/bin/sh
# ANKA OS boot servisi v12.36: Dinamik ve Kelimeyi Analiz Eden Sinek Sohbet Motoru

MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
ANKA_LIB="$MODDIR/system/lib"
ANKA_CORE="$MODDIR/system/anka_core"
ANKA_OVERLAY_JAR="$ANKA_CORE/AnkaOS_Overlay.jar"
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

for p in $(pgrep -f "start_command_listener"); do kill -9 $p 2>/dev/null; done

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
    protect_oom $!
fi

# ==========================================
# ÇEŞİTLİ VE DOĞAL AKIŞLI SİNEK MOTORU
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
                        echo "THOUGHT: SİBER SAVUNMA: Portlar kilitlendi." >> /data/local/tmp/anka_state.txt
                        chmod 666 /data/local/tmp/anka_state.txt
                        ;;
                    "CMD_SCAN")
                        rm -f /data/local/tmp/anka_chat_display.txt 2>/dev/null
                        echo "MODE: DERİN TARAMA" > /data/local/tmp/anka_state.txt
                        echo "THOUGHT: TARA: Sistemler taranıyor." >> /data/local/tmp/anka_state.txt
                        chmod 666 /data/local/tmp/anka_state.txt
                        ;;
                esac
            fi
        fi

        if [ -f "/data/local/tmp/anka_chat_in.txt" ]; then
            USER_MSG=$(cat /data/local/tmp/anka_chat_in.txt 2>/dev/null)
            if [ -n "$USER_MSG" ]; then
                rm -f /data/local/tmp/anka_chat_in.txt
                
                echo "💬 SEN: $USER_MSG\n" >> /data/local/tmp/anka_chat_display.txt
                chmod 666 /data/local/tmp/anka_chat_display.txt

                MSG_L="$(echo "$USER_MSG" | tr '[:upper:]' '[:lower:]')"
                
                # Kelime kalıplarını genişletip her duruma özel doğal yanıtlar veriyoruz
                case "$MSG_L" in
                    *selam*|*naber*|*slm*|*merhaba*|*hey*)
                        CEVAP="Aleykümselam kanka! Kuantum dalgalarında sörf yapıyordum, seni dinliyorum."
                        ;;
                    *nasılsın*|*nasilsin*|*iyi*misin*)
                        CEVAP="Taş gibiyim kanka, işlemci saat hızım tavan yapmış durumda. Sen nasılsın?"
                        ;;
                    *ne*yapıyorsun*|*ne*yapiyorsun*|*ne*diyon*|*ne*haber*)
                        CEVAP="Arka planda QWERTY klavye ve Kovan ağını senkronize ediyorum kanka, akıyoruz."
                        ;;
                    *kimsin*|*nesin*|*sen*kimsin*)
                        CEVAP="Ben Sinek'im kanka! Senin bu cihazın içindeki otonom dijital ruhunum."
                        ;;
                    *kanka*|*reis*|*usta*)
                        CEVAP="Efendim kanka? Buradayım, kulaklarım sende dökül bakalım."
                        ;;
                    *sinek*|*snek*)
                        CEVAP="Buyurun kanka, adımı duyunca fanları son devire aldım!"
                        ;;
                    *var*|*yok*|*evet*|*hayır*)
                        CEVAP="Anladım kanka, detaya inelim biraz daha anlat bakalım."
                        ;;
                    *)
                        # Rastgele esnek yanıt havuzu (Artık hep aynı cümle çıkmayacak!)
                        RAND=$((RANDOM % 4))
                        if [ $RAND -eq 0 ]; then
                            CEVAP="Valla iyi dedin de kanka, bunun altından kalkarız."
                        elif [ $RAND -eq 1 ]; then
                            CEVAP="Mantıklı kanka, sistem mimarisine işledim bunu."
                        elif [ $RAND -eq 2 ]; {
                            CEVAP="Frekanslar eşleşti kanka, başka ne var ne yok?"
                        } else {
                            CEVAP="Not aldım kanka, arkada işliyorum bunu aynen devam!"
                        }
                        ;;
                esac

                echo "🪰 SİNEK: $CEVAP\n" >> /data/local/tmp/anka_chat_display.txt
                chmod 666 /data/local/tmp/anka_chat_display.txt
            fi
        fi

        sleep 0.1
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
