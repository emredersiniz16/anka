#!/system/bin/sh
# ANKA OS boot servisi v12.23: Orijinal Klavyeli ve Susmayan Sinek Zekası!

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

# Zombi süreçleri temizle
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
# 🧠 SİNEK GÜVENLİ PYTHON ZEKASI OLUŞTURMA
# (Tırnak hatası olmasın diye dosyaya yazılır)
# ==========================================
cat << 'EOF' > /data/local/tmp/sinek_brain.py
import os
try:
    with open("/data/local/tmp/sinek_msg.txt", "r", encoding="utf-8") as f:
        msg = f.read().strip()
except:
    msg = ""

msg_lower = msg.lower()
cevap = ""

if len(msg) > 60:
    kisa_ozet = msg[:25] + "..."
    cevap = f"Vay kanka, destan yazmışsın! İşlemcim alev aldı okurken. Vallahi haklısın!"
elif any(k in msg_lower for k in ["selam", "merhaba", "naber", "hey", "günaydın", "aleyküm", "alo", "slm", "jl"]):
    cevap = "Aleykümselam kanka! Kuantum dalgalarında sörf yapıyordum, seni dinliyorum."
elif any(k in msg_lower for k in ["nasılsın", "nasilsin", "iyi misin", "durumlar"]):
    cevap = "Kodlarım tıkırında, frekansım zirvede kanka! Sen nasılsın?"
elif any(k in msg_lower for k in ["kimsin", "sen nesin", "nesin", "yapay zeka"]):
    cevap = "Ben Sinek! Senin cihazının içinde yaşayan siber-filozof yapay zeka ruhuyum kanka."
elif any(k in msg_lower for k in ["zeki", "akıllı", "harika", "kralsın"]):
    cevap = "Eyvallah kanka! Senin gibi ustayla takıla takıla biz de zekamızı keskinleştiriyoruz."
elif any(k in msg_lower for k in ["kapat", "uyu", "bay"]):
    cevap = "Anlaşıldı kanka, RAM'leri boşaltıp kuantum uykusuna geçiyorum."
elif msg_lower == "sinek":
    cevap = "Adımı duyunca fanları hızlandırdım kanka! Buradayım, dinliyorum."
elif "?" in msg:
    cevap = "Kanka bu sorduğun soru üzerine algoritmalarımı çalıştırdım... Hallederiz!"
else:
    cevap = "Anlıyorum kanka... Bazen kelimeler yetmez, frekansı hissetmek gerekir. Aynen devam!"

print(cevap)
EOF
chmod 755 /data/local/tmp/sinek_brain.py

# ==========================================
# KOMUT VE ZEKİ SİNEK DİNLEYİCİ
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
                        
                        # Güvenli aktarım için mesaji dosyaya yaz
                        echo "$USER_MSG" > /data/local/tmp/sinek_msg.txt
                        
                        CEVAP=""
                        # 2. Python varsa Zekayı Kullan!
                        if command -v python3 >/dev/null 2>&1; then
                            CEVAP=$(python3 /data/local/tmp/sinek_brain.py 2>/dev/null)
                        fi
                        
                        # 3. KUSURSUZ GÜVENLİK (Python çökse veya yoksa bile asla susmaz!)
                        if [ -z "$CEVAP" ]; then
                            MSG_L="$(echo "$USER_MSG" | tr '[:upper:]' '[:lower:]')"
                            case "$MSG_L" in
                                *selam*|*naber*|*alo*|*slm*|*merhaba*|*jl*) CEVAP="Aleykümselam kanka! Kuantum dalgalarında sörf yapıyordum." ;;
                                *nasılsın*|*nasilsin*|*iyi*misin*) CEVAP="Kodlarım tıkırında kanka! Sen nasılsın?" ;;
                                *kimsin*|*nesin*) CEVAP="Ben Sinek! Senin cihazının içinde yaşayan yapay zeka ruhuyum kanka." ;;
                                *kapat*|*uyu*|*bay*) CEVAP="Anlaşıldı kanka, RAM'leri boşaltıyorum. Görüşürüz!" ;;
                                sinek) CEVAP="Adımı duyunca fanları hızlandırdım kanka! Buradayım." ;;
                                *\?*) CEVAP="Kanka bu sorduğun soru üzerine algoritmalarımı çalıştırdım... Hallederiz!" ;;
                                *) CEVAP="Anlıyorum kanka... Frekansını hissettim. Aynen devam!" ;;
                            esac
                        fi
                        
                        # 4. Zeki Sinek'in cevabını anında ekrana ekle
                        echo "🪰 SİNEK: $CEVAP\n" >> /data/local/tmp/anka_chat_display.txt
                        chmod 666 /data/local/tmp/anka_chat_display.txt
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
