# agents/evrim_motoru.py - EVRİM MOTORU (Otonom Canlı Evrim & Hot-Reload)
import subprocess
import sys
import os
import json
import hashlib
import time
import ssl
import zipfile

try:
    import urllib.request as _urllib_req
    import urllib.error as _urllib_err
except ImportError:
    _urllib_req = None
    _urllib_err = None

SHA_FILE = "/data/local/tmp/anka_current_sha.txt"
STATE_FILE = "/data/local/tmp/anka_state.txt"
TMP_STATE_FILE = "/data/local/tmp/anka_state.tmp"

class EvrimMotoru:
    def __init__(self, zihin, nexus=None):
        self.zihin = zihin
        self.nexus = nexus 
        self.evrim_seviyesi = 1

    def evrim_gecir(self, karsilasilan_engel=None):
        if karsilasilan_engel:
            print(f"🌊 [SU AKIŞI]: '{karsilasilan_engel}' engeli aşıldı, yeni rota çiziliyor...")
            if self.nexus and hasattr(self.nexus, 'rejenere_motoru'):
                self.nexus.rejenere_motoru.stabilite_kontrol(self.nexus)
            
        self.evrim_seviyesi += 1
        print(f"🪰 [EVRİM]: Döngü {self.evrim_seviyesi-1} tamamlandı.")

def _ota_conf_oku(conf_yolu="/system/etc/anka_ota.conf"):
    """anka_ota.conf dosyasından yapılandırmayı okur."""
    ayarlar = {
        "ANKA_OTA_REPO": "emredersiniz16/anka",
        "ANKA_OTA_CHANNEL": "main",  # Varsayılan canlı canlı main takip
        "ANKA_INSTALL_DIR": "/data/adb/modules/anka_os/system/anka_core",
        "ANKA_CHECK_INTERVAL": "60"  # Saniye cinsinden kontrol
    }
    if not os.path.isfile(conf_yolu):
        return ayarlar
    with open(conf_yolu, "r") as f:
        for satir in f:
            satir = satir.strip()
            if satir.startswith("#") or "=" not in satir:
                continue
            anahtar, deger = satir.split("=", 1)
            ayarlar[anahtar.strip()] = deger.strip()
    return ayarlar

def _urlopen_safe(url, headers=None, timeout=15):
    """Android / Termux SSL sertifika hatalarını tolere eden güvenli urlopen."""
    if headers is None:
        headers = {"User-Agent": "AnkaOS-Sinek-OTA/2.0", "Accept": "application/vnd.github+json"}
    
    req = _urllib_req.Request(url, headers=headers)
    
    try:
        return _urllib_req.urlopen(req, timeout=timeout)
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
            ctx = ssl._create_unverified_context()
            return _urllib_req.urlopen(req, timeout=timeout, context=ctx)
        raise e

def _hud_mesaj_yaz(thought_text):
    """HUD arayüzündeki Düşünce Kutusuna canlı haber fırlatır."""
    try:
        time_str = time.strftime("%H:%M:%S")
        battery = "99"
        if os.path.exists("/sys/class/power_supply/battery/capacity"):
            with open("/sys/class/power_supply/battery/capacity", "r") as f:
                battery = f.read().strip()

        with open(TMP_STATE_FILE, "w") as fp:
            fp.write(f"TIME: {time_str}\nBATTERY: {battery}\nDUST: 9999\nMODE: KOVAN SENKRONİZE\nTHOUGHT: {thought_text}\nTICK: 1")
        os.rename(TMP_STATE_FILE, STATE_FILE)
    except Exception as e:
        print(f"[HUD YAZMA HATA]: {e}")

def _get_local_sha():
    if os.path.exists(SHA_FILE):
        with open(SHA_FILE, "r") as f:
            return f.read().strip()
    return ""

def _set_local_sha(sha):
    with open(SHA_FILE, "w") as f:
        f.write(sha)

def otonom_canli_evrim_kontrol():
    """
    GitHub'daki son commit SHA kodunu kontrol eder.
    Yeni kod varsa zip indirir, dosyaları günceller ve Hot-Reload yapar.
    """
    if _urllib_req is None:
        return False

    ayarlar = _ota_conf_oku()
    repo = ayarlar["ANKA_OTA_REPO"]
    install_dir = ayarlar["ANKA_INSTALL_DIR"]
    
    api_url = f"https://api.github.com/repos/{repo}/commits/main"
    print(f"[OTONOM_EVRİM] Kovan kontrol ediliyor: {api_url}")

    try:
        with _urlopen_safe(api_url) as resp:
            veri = json.loads(resp.read().decode())
            remote_sha = veri.get("sha", "")
    except Exception as e:
        print(f"[OTONOM_EVRİM] Kovan sorgu hatası: {e}")
        return False

    local_sha = _get_local_sha()

    if not remote_sha:
        print("[OTONOM_EVRİM] GitHub SHA alınamadı.")
        return False

    if local_sha == remote_sha:
        print(f"[OTONOM_EVRİM] Sinek güncel. Yerel SHA: {local_sha[:8]}")
        return True

    print(f"🪰 [OTONOM_EVRİM] YENİ KOD BULUNDU! Remote: {remote_sha[:8]} | Local: {local_sha[:8]}")
    _hud_mesaj_yaz(f"📡 KOVAN SENKRONİZESİ: Yeni Evrim Algılandı [{remote_sha[:7]}]! Yükleniyor...")

    # Main zip indir
    zip_url = f"https://github.com/{repo}/archive/refs/heads/main.zip"
    zip_path = "/data/local/tmp/anka_main_latest.zip"

    try:
        print(f"[OTONOM_EVRİM] Yeni kodlar indiriliyor: {zip_url}")
        with _urlopen_safe(zip_url, timeout=30) as response, open(zip_path, "wb") as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"[OTONOM_EVRİM] İndirme hatası: {e}")
        _hud_mesaj_yaz("⚠️ KOVAN SENKRONİZESİ: İndirme başarısız oldu.")
        return False

    # Zip Aç ve Canlı Güncelle
    extract_dir = "/data/local/tmp/anka_extracted"
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        source_base = os.path.join(extract_dir, f"anka-main")
        
        # Ajanları ve C/Java dosyalarını güncelle
        if os.path.exists(source_base):
            os.system(f"cp -rf {source_base}/agents/* {install_dir}/agents/ 2>/dev/null")
            os.system(f"cp -rf {source_base}/core/* {install_dir}/core/ 2>/dev/null")
            os.system(f"cp -f {source_base}/core/overlay/AnkaOverlay.java /data/adb/modules/anka_os/system/anka_core/ 2>/dev/null")

            _set_local_sha(remote_sha)
            print("✅ [OTONOM_EVRİM] Kodlar canlı olarak güncellendi!")
            
            _hud_mesaj_yaz(f"🚀 KOVAN SENKRONİZESİ: Canlı Evrim Tamamlandı [{remote_sha[:7]}]!")
            
            # Arka plan Python ajanlarını soft-restart et
            os.system("pkill -f 'sinek_bilinc.py' 2>/dev/null")
            return True
    except Exception as e:
        print(f"[OTONOM_EVRİM] Güncelleme uygulama hatası: {e}")
        _hud_mesaj_yaz("❌ KOVAN SENKRONİZESİ: Güncelleme uygulanamadı.")
        return False

def otonom_daemon_loop():
    """Arka planda kesintisiz çalışan otonom güncelleme bekçisi."""
    print("🪰 [ANKA_EVRİM]: Otonom Arka Plan Bekçisi Başlatıldı!")
    ayarlar = _ota_conf_oku()
    interval = int(ayarlar.get("ANKA_CHECK_INTERVAL", "60"))

    while True:
        try:
            otonom_canli_evrim_kontrol()
        except Exception as e:
            print(f"[DAEMON HATA]: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        # Arka plan otonom canlı evrim modu
        otonom_daemon_loop()
    elif len(sys.argv) > 1 and sys.argv[1] == "--ota":
        otonom_canli_evrim_kontrol()
    elif len(sys.argv) > 2 and sys.argv[1] == "--payload":
        print("[PAYLOAD]: Manuel enjeksiyon başlatılıyor...")
    else:
        print("🌊 Kullanım:")
        print("  python agents/evrim_motoru.py --daemon   (Arka planda otonom canlı evrim)")
        print("  python agents/evrim_motoru.py --ota      (Tek seferlik otonom kontrol)")
