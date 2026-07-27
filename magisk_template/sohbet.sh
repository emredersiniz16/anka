#!/system/bin/sh
# Sinek ile sohbet baslat
# Kullanim: sh /data/adb/modules/anka_os/sohbet.sh

MODDIR=${0%/*}
ANKA_CORE="$MODDIR/system/anka_core"
export PATH="$MODDIR/system/bin:/data/adb/modules/anka_os/system/bin:/system/bin:$PATH"
export LD_LIBRARY_PATH="$MODDIR/system/lib:$LD_LIBRARY_PATH"

cd "$ANKA_CORE"
python3 "$ANKA_CORE/agents/sinek_sohbet.py"
