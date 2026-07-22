#!/system/bin/sh
# ANKA OS boot servisi - late_start sonrasi calisir
# DÜZELTME v3: Bootloop fix — boot tamamlanana kadar bekle, library path düzelt

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

# Boot tamamlanmadıysa başlatma
if [ "$(getprop sys.boot_completed)" != "1" ]; then
    echo "[ANKA $(date '+%H:%M:%S')] HATA: Boot tamamlanmadi, sinek baslatilmiyor" > "$LOGFILE"
    exit 0
fi

# 2. SELinux permissive (framebuffer için)
setenforce 0 2>/dev/null

# 3. Framebuffer izinlerini aç
chmod 666 /dev/graphics/fb0 2>/dev/null

# 4. Binary var mı kontrol
if [ ! -f "$ANKA_BIN" ]; then
    echo "[ANKA $(date '+%H:%M:%S')] HATA: $ANKA_BIN bulunamadi" >> "$LOGFILE"
    exit 0
fi

# 5. Library var mı kontrol
if [ ! -f "$ANKA_LIB/libanka_quantum.so" ]; then
    echo "[ANKA $(date '+%H:%M:%S')] HATA: libanka_quantum.so bulunamadi" >> "$LOGFILE"
    exit 0
fi

# 6. İzinler
chmod 755 "$ANKA_BIN"
chmod 755 "$ANKA_LIB/libanka_quantum.so"

# 7. ANKA core dizinine geç (assets ve agents burada) - Dizin yoksa oluştur
mkdir -p "$ANKA_CORE"
cd "$ANKA_CORE"

# 8. Library path set et (dlopen ve dynamic linker için)
export LD_LIBRARY_PATH="$ANKA_LIB:$LD_LIBRARY_PATH"
export ANKA_LIB_PATH="$ANKA_LIB/libanka_quantum.so"

# 9. Core/quantum dizini oluştur (boot.c dlopen için)
mkdir -p "$ANKA_CORE/core/quantum"
cp "$ANKA_LIB/libanka_quantum.so" "$ANKA_CORE/core/quantum/" 2>/dev/null
chmod 755 "$ANKA_CORE/core/quantum/libanka_quantum.so"

# 10. Log başlangıcı
echo "[ANKA $(date '+%H:%M:%S')] ====================================" > "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] ANKA OS baslatiliyor..." >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] SELinux: $(getenforce)" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Binary: $ANKA_BIN" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Library: $ANKA_LIB/libanka_quantum.so" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Core: $ANKA_CORE" >> "$LOGFILE"
echo "[ANKA $(date '+%H:%M:%S')] Boot: $(getprop sys.boot_completed)" >> "$LOGFILE"

# 11. Sineği arka planda başlat
# ÖNEMLİ: crash olursa sistem etkilenmesin — nohup + timeout koruması
nohup "$ANKA_BIN" >> "$LOGFILE" 2>&1 &
PID=$!
echo "[ANKA $(date '+%H:%M:%S')] Sinek baslatildi PID=$PID" >> "$LOGFILE"

# 12. Sinek çökerse yeniden başlat — ama MAKSİMUM 3 deneme
RETRY=0
MAX_RETRY=3
while [ $RETRY -lt $MAX_RETRY ]; do
    sleep 10
    if ! kill -0 $PID 2>/dev/null; then
        RETRY=$((RETRY + 1))
        echo "[ANKA $(date '+%H:%M:%S')] Sinek crasledi, yeniden baslatma $RETRY/$MAX_RETRY" >> "$LOGFILE"
        if [ $RETRY -lt $MAX_RETRY ]; then
            nohup "$ANKA_BIN" >> "$LOGFILE" 2>&1 &
            PID=$!
            echo "[ANKA $(date '+%H:%M:%S')] Yeni PID=$PID" >> "$LOGFILE"
        fi
    fi
done

echo "[ANKA $(date '+%H:%M:%S')] Sinek stabil veya max deneme asildi, servis tamamlandi" >> "$LOGFILE"
