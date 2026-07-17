#!/system/bin/sh
# ANKA OS boot servisi - late_start sonrasi calisir
MODDIR=${0%/*}
ANKA_BIN="$MODDIR/system/bin/anka_os_bin"
LOGFILE=/data/adb/anka_os.log

# Termux python3 bekle (max 30 sn)
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

# Assets dizinine gec
if [ -d "$MODDIR/system/anka_core" ]; then
    cd "$MODDIR/system/anka_core"
fi

echo "[ANKA $(date '+%H:%M:%S')] Baslatiliyor..." >> "$LOGFILE"
nohup "$ANKA_BIN" >> "$LOGFILE" 2>&1 &
echo "[ANKA $(date '+%H:%M:%S')] PID: $!" >> "$LOGFILE"

