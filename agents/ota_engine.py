# agents/ota_engine.py - ANKA OS OTA GÜNCELLEME MOTORU
# GitHub Releases API üzerinden günde bir kontrol yapar.
# Yeni AnkaOS_Quantum_v1.zip varsa indirir, Magisk modül klasörüne açar.
#
# Çağrı şekilleri:
#   from ota_engine import OTAMotoru
#   ota = OTAMotoru()
#   ota.gunluk_kontrol()         # bloklayıcı — kontrol + indirme
#   ota.gunluk_kontrol_bg()      # arka plan thread'i
#
#   python3 agents/ota_engine.py --check   # manuel kontrol
#   python3 agents/ota_engine.py --force    # zorla indir + kur

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.error
import zipfile
import shutil
import subprocess
import threading
from datetime import datetime

# --- YAPILANDIRMA ---
GITHUB_REPO = "emredersiniz16/anka"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
TARGET_ASSET_NAME = "AnkaOS_Quantum_v1.zip"
TARGET_SHA_NAME = "AnkaOS_Quantum_v1.zip.sha256"

# Magisk modül dizini (service.sh'teki $MODDIR ile aynı)
MAGISK_MODDIR = "/data/adb/modules/anka_os"

# İndirme dizini (geçici)
DOWNLOAD_DIR = "/data/local/tmp/anka_os"
DOWNLOAD_PATH = os.path.join(DOWNLOAD_DIR, TARGET_ASSET_NAME)

# OTA durum dosyası (son kontrol, son sürüm, retry sayısı)
OTA_STATE_FILE = os.path.join(DOWNLOAD_DIR, "ota_durum.json")

# Günde bir kontrol et (saniye)
KONTROL_ARALIK_SANIYE = 86400  # 24 saat

# HTTP timeout
HTTP_TIMEOUT = 30


class OTAMotoru:
    """
    Anka OS için GitHub tabanlı OTA güncelleme motoru.
    Günde bir kez Releases'i kontrol eder, yeni sürüm varsa indirir ve
    Magisk modül klasörüne açarak kendini günceller.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        self._log("📡 [OTA]: Motor başlatıldı")

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def gunluk_kontrol_bg(self):
        """Arka planda günlük kontrol döngüsünü başlatır (daemon thread)."""
        t = threading.Thread(target=self._gunluk_dongu, daemon=True)
        t.start()
        return t

    def gunluk_kontrol(self):
        """Tek seferlik kontrol — yeni sürüm varsa indir ve kur."""
        return self._kontrol_ve_guncelle()

    def zorla_guncelle(self):
        """Sürüm kontrolü yapmadan doğrudan en son release'i indirir."""
        self._log("🔄 [OTA]: Zorla güncelleme başlatıldı")
        release = self._release_bilgi_al()
        if not release:
            return False
        return self._indir_ve_kur(release)

    # -----------------------------------------------------------------------
    # İç döngü
    # -----------------------------------------------------------------------

    def _gunluk_dongu(self):
        """Sonsuz döngü — her 24 saatte bir kontrol yapar."""
        while True:
            try:
                self._kontrol_ve_guncelle()
            except Exception as e:
                self._log(f"⚠️  [OTA]: Döngü hatası: {e}")
            # 24 saat bekle
            time.sleep(KONTROL_ARALIK_SANIYE)

    def _kontrol_ve_guncelle(self) -> bool:
        """GitHub Releases'i kontrol et, yeni sürüm varsa indir + kur."""
        self._log("🔍 [OTA]: GitHub Releases kontrol ediliyor...")

        # 1. Son kontrol zamanını oku
        durum = self._durum_yukle()
        son_kontrol = durum.get("son_kontrol_zamani", 0)
        simdi = time.time()

        # 24 saat geçmediysedi ve force değilse atla
        if (simdi - son_kontrol) < KONTROL_ARALIK_SANIYE:
            kalan_saat = (KONTROL_ARALIK_SANIYE - (simdi - son_kontrol)) / 3600
            self._log(f"⏭️  [OTA]: Son kontrol {int((simdi - son_kontrol)/3600)}s önce, {kalan_saat:.1f}s sonra tekrar")
            return False

        # 2. Release bilgisini al
        release = self._release_bilgi_al()
        if not release:
            self._log("❌ [OTA]: Release bilgisine ulaşılamadı")
            return False

        tag = release.get("tag_name", "")
        published_at = release.get("published_at", "")

        # 3. Yeni sürüm var mı kontrol et
        son_yuklu_surum = durum.get("son_yuklu_surum", "")
        if tag and tag == son_yuklu_surum:
            self._log(f"✅ [OTA]: Sistem güncel (v{tag})")
            durum["son_kontrol_zamani"] = simdi
            self._durum_kaydet(durum)
            return False

        self._log(f"🆕 [OTA]: Yeni sürüm bulundu: {tag} (yayın: {published_at})")
        self._log(f"    Mevcut: {son_yuklu_surum or 'yok'} → Yeni: {tag}")

        # 4. İndir ve kur
        basarili = self._indir_ve_kur(release)

        # 5. Durumu güncelle
        durum["son_kontrol_zamani"] = simdi
        if basarili:
            durum["son_yuklu_surum"] = tag
            durum["son_guncelleme_zamani"] = simdi
            self._log(f"🎉 [OTA]: Güncelleme başarılı! Yeni sürüm: {tag}")
        else:
            durum["retry_sayisi"] = durum.get("retry_sayisi", 0) + 1
            self._log(f"❌ [OTA]: Güncelleme başarısız (retry #{durum['retry_sayisi']})")
        self._durum_kaydet(durum)

        return basarili

    # -----------------------------------------------------------------------
    # GitHub API
    # -----------------------------------------------------------------------

    def _release_bilgi_al(self) -> dict | None:
        """GitHub Releases API'sinden en son release bilgisini alır."""
        try:
            req = urllib.request.Request(
                GITHUB_API_RELEASES,
                headers={
                    "User-Agent": "AnkaOS-OTA/1.0",
                    "Accept": "application/vnd.github+json",
                },
            )
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            self._log(f"❌ [OTA]: GitHub API hatası HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            self._log(f"❌ [OTA]: GitHub API hatası: {e}")
            return None

    def _asset_bul(self, release: dict, isim: str) -> dict | None:
        """Release asset'leri arasında isim eşleşmesi ara."""
        for a in release.get("assets", []):
            if a.get("name") == isim:
                return a
        return None

    # -----------------------------------------------------------------------
    # İndirme + SHA256 doğrulama
    # -----------------------------------------------------------------------

    def _indir(self, url: str, hedef: str) -> bool:
        """URL'yi indir, hedef dosyaya yaz."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AnkaOS-OTA/1.0"},
            )
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
                toplam = int(r.headers.get("Content-Length", 0))
                indirilen = 0
                with open(hedef, "wb") as f:
                    while True:
                        blok = r.read(65536)
                        if not blok:
                            break
                        f.write(blok)
                        indirilen += len(blok)
                self._log(f"📥 [OTA]: İndirme tamam: {indirilen} byte")
                return True
        except Exception as e:
            self._log(f"❌ [OTA]: İndirme hatası: {e}")
            return False

    def _sha256_dogrula(self, dosya: str, beklenen: str) -> bool:
        """Dosyanın SHA256 hash'ini hesapla ve beklenenle karşılaştır."""
        h = hashlib.sha256()
        with open(dosya, "rb") as f:
            for blok in iter(lambda: f.read(65536), b""):
                h.update(blok)
        hesaplanan = h.hexdigest()
        if hesaplanan.lower() != beklenen.lower().strip():
            self._log(f"❌ [OTA]: SHA256 uyuşmazlığı!")
            self._log(f"    Beklenen: {beklenen}")
            self._log(f"    Hesaplanan: {hesaplanan}")
            return False
        self._log(f"🔐 [OTA]: SHA256 doğrulandı: {hesaplanan[:16]}...")
        return True

    # -----------------------------------------------------------------------
    # Kurma — Magisk modül klasörüne açma
    # -----------------------------------------------------------------------

    def _indir_ve_kur(self, release: dict) -> bool:
        """Release'i indir, SHA256 doğrula, Magisk modülüne aç."""
        # 1. Asset'leri bul
        zip_asset = self._asset_bul(release, TARGET_ASSET_NAME)
        if not zip_asset:
            self._log(f"❌ [OTA]: {TARGET_ASSET_NAME} asset bulunamadı")
            return False

        sha_asset = self._asset_bul(release, TARGET_SHA_NAME)

        # 2. ZIP'i indir
        self._log(f"📥 [OTA]: {TARGET_ASSET_NAME} indiriliyor...")
        if not self._indir(zip_asset["browser_download_url"], DOWNLOAD_PATH):
            return False

        # 3. SHA256 doğrula (varsa)
        if sha_asset:
            self._log("🔐 [OTA]: SHA256 kontrol ediliyor...")
            sha_url = sha_asset["browser_download_url"]
            sha_path = DOWNLOAD_PATH + ".sha256"
            if self._indir(sha_url, sha_path):
                try:
                    with open(sha_path, "r") as f:
                        beklenen_sha = f.read().strip().split()[0]
                    if not self._sha256_dogrula(DOWNLOAD_PATH, beklenen_sha):
                        os.remove(DOWNLOAD_PATH)
                        return False
                except Exception as e:
                    self._log(f"⚠️  [OTA]: SHA okuma hatası, atlanıyor: {e}")
        else:
            self._log("⚠️  [OTA]: SHA256 dosyası yok, doğrulama atlandı")

        # 4. Magisk modül klasörüne aç
        return self._magisk_modulune_ac(DOWNLOAD_PATH)

    def _magisk_modulune_ac(self, zip_yolu: str) -> bool:
        """ZIP'i Magisk modül dizinine aç ve yeniden başlatma bayrağı koy."""
        if not os.path.exists(MAGISK_MODDIR):
            self._log(f"❌ [OTA]: Magisk modül dizini yok: {MAGISK_MODDIR}")
            self._log(f"    Magisk modülü kurulu mu?")
            return False

        self._log(f"📦 [OTA]: {MAGISK_MODDIR} dizinine açılıyor...")

        # Önce eski binary ve library'yi yedekle
        backup_dir = os.path.join(DOWNLOAD_DIR, "backup")
        os.makedirs(backup_dir, exist_ok=True)

        for src, dst in [
            (os.path.join(MAGISK_MODDIR, "system/bin/anka_os_bin"), os.path.join(backup_dir, "anka_os_bin.bak")),
            (os.path.join(MAGISK_MODDIR, "system/lib/libanka_quantum.so"), os.path.join(backup_dir, "libanka_quantum.so.bak")),
        ]:
            if os.path.exists(src):
                shutil.copy2(src, dst)
                self._log(f"    Yedeklendi: {os.path.basename(src)}")

        # ZIP'i geçici dizine aç
        extract_dir = os.path.join(DOWNLOAD_DIR, "extract")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)
        os.makedirs(extract_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_yolu, "r") as zf:
                zf.extractall(extract_dir)
            self._log(f"📦 [OTA]: ZIP açıldı ({len(os.listdir(extract_dir))} dosya)")
        except Exception as e:
            self._log(f"❌ [OTA]: ZIP açma hatası: {e}")
            return False

        # Yeni dosyaları kopyala
        kopyalandi = 0
        for root, dirs, files in os.walk(extract_dir):
            rel = os.path.relpath(root, extract_dir)
            target_dir = MAGISK_MODDIR if rel == "." else os.path.join(MAGISK_MODDIR, rel)
            os.makedirs(target_dir, exist_ok=True)
            for fname in files:
                src = os.path.join(root, fname)
                dst = os.path.join(target_dir, fname)
                try:
                    shutil.copy2(src, dst)
                    os.chmod(dst, 0o755)
                    kopyalandi += 1
                except Exception as e:
                    self._log(f"⚠️  [OTA]: {fname} kopyalanamadı: {e}")

        self._log(f"✅ [OTA]: {kopyalandi} dosya Magisk modülüne kopyalandı")

        # Geçici dizini temizle
        shutil.rmtree(extract_dir, ignore_errors=True)

        # Yeniden başlatma bayrağı — service.sh bir sonraki boot'ta
        # yeni binary'yi yükleyecek
        flag_path = os.path.join(MAGISK_MODDIR, "update_pending")
        try:
            with open(flag_path, "w") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self._log("🚩 [OTA]: update_pending bayrağı yazıldı — bir sonraki boot'ta aktif olacak")
        except Exception as e:
            self._log(f"⚠️  [OTA]: update_pending yazılamadı: {e}")

        # Temizlik
        try:
            os.remove(zip_yolu)
        except Exception:
            pass

        return True

    # -----------------------------------------------------------------------
    # Durum dosyası
    # -----------------------------------------------------------------------

    def _durum_yukle(self) -> dict:
        try:
            if os.path.exists(OTA_STATE_FILE):
                with open(OTA_STATE_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _durum_kaydet(self, durum: dict):
        try:
            os.makedirs(os.path.dirname(OTA_STATE_FILE), exist_ok=True)
            with open(OTA_STATE_FILE, "w") as f:
                json.dump(durum, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"⚠️  [OTA]: Durum kaydedilemedi: {e}")

    # -----------------------------------------------------------------------
    # Log
    # -----------------------------------------------------------------------

    def _log(self, mesaj: str):
        if self.verbose:
            print(mesaj)


# -----------------------------------------------------------------------
# Bağımsız çalıştırma
# -----------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Anka OS OTA Motoru")
    parser.add_argument("--check", action="store_true", help="Tek seferlik kontrol")
    parser.add_argument("--force", action="store_true", help="Zorla güncelle")
    args = parser.parse_args()

    ota = OTAMotoru(verbose=True)

    if args.force:
        print("🔄 Zorla güncelleme başlatılıyor...")
        ok = ota.zorla_guncelle()
        print(f"{'✅ Başarılı' if ok else '❌ Başarısız'}")
        sys.exit(0 if ok else 1)
    else:
        # --check veya varsayılan: tek seferlik kontrol
        print("🔍 Günlük kontrol başlatılıyor...")
        ok = ota.gunluk_kontrol()
        print(f"{'✅ Güncellendi' if ok else 'ℹ️  Güncelleme yok veya atlandı'}")
        sys.exit(0 if ok else 0)
