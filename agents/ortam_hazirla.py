# agents/ortam_hazirla.py - ANKA OS ORTAM HAZIRLIK MOTORU
#
# Yüklendiği cihazı otomatik olarak tanır, eksik bağımlılıkları internet
# üzerinden indirir ve kurar. Termux (Android), iSH (iOS), ve Linux ortamlarını
# destekler. Boot sürecinde çağrılır; kurulum tamamsa hızla geçer.
#
# Kullanım:
#   from ortam_hazirla import OrtamHazirla
#   hazir = OrtamHazirla()
#   hazir.baslat()

import os
import sys
import json
import platform
import subprocess
import importlib
import shutil
import tempfile
import time

# Kalıcı verilerin tutulacağı klasör: Android'de /data/local/tmp, diğerlerinde temp
def _durum_yolu_bul() -> str:
    for tercih in ["/data/local/tmp", tempfile.gettempdir()]:
        try:
            os.makedirs(tercih, exist_ok=True)
            test = os.path.join(tercih, ".anka_yazma_testi")
            with open(test, "w") as f:
                f.write("ok")
            os.remove(test)
            return os.path.join(tercih, "anka_ortam.json")
        except OSError:
            continue
    return os.path.join(tempfile.gettempdir(), "anka_ortam.json")

_DURUM_YOLU = _durum_yolu_bul()
_VERSIYON   = "1.0.0"   # Bu değeri artırarak yeniden kurulumu zorla

# --- ZORUNLU PIP PAKETLERİ ---
# Her paket: {"import": "<import_adı>", "pkg": "<pip_adı>", "termux": "<pkg_adı>"}
ZORUNLU_PAKETLER = [
    {"import": "websockets",  "pip": "websockets",          "termux": "python-websockets"},
    {"import": "fastapi",     "pip": "fastapi",             "termux": "python-fastapi"},
    {"import": "uvicorn",     "pip": "uvicorn",             "termux": "python-uvicorn"},
    {"import": "sqlalchemy",  "pip": "sqlalchemy",          "termux": "python-sqlalchemy"},
    {"import": "requests",    "pip": "requests",            "termux": "python-requests"},
]

# --- OPSİYONEL PAKETLERİ: varsa kullan, yoksa es geç ---
OPSIYONEL_PAKETLER = [
    {"import": "psutil",      "pip": "psutil",              "termux": "python-psutil"},
    {"import": "dotenv",      "pip": "python-dotenv",       "termux": "python-dotenv"},
]


class OrtamHazirla:
    """
    Cihazı tanıyıp ortamı hazırlar.
    """

    def __init__(self):
        self.platform  = self._platform_tespit()
        self.pip_cmd   = self._pip_komutu()
        self.pkg_mgr   = self._paket_yoneticisi()
        self.durum     = self._durum_yukle()
        self.log_satir = []

    # -----------------------------------------------------------------------
    # Ana giriş noktası
    # -----------------------------------------------------------------------

    def baslat(self) -> dict:
        """
        Ortamı hazırlar. Daha önce hazırlanmışsa hızla döner.

        Returns:
            {"platform": str, "kurulan": list, "atlanan": list, "hata": list}
        """
        self._log(f"🌍 [ORTAM]: Platform → {self.platform}")

        # Versiyon aynıysa tekrar kurma
        if self.durum.get("versiyon") == _VERSIYON and self.durum.get("tamam"):
            self._log("✅ [ORTAM]: Ortam güncel, atlanıyor.")
            return {"platform": self.platform, "kurulan": [], "atlanan": ["önceden_kuruldu"], "hata": []}

        kurulan = []
        atlanan = []
        hatalar = []

        # Zorunlu paketleri kur
        for p in ZORUNLU_PAKETLER:
            sonuc = self._paket_kontrol_kur(p, zorunlu=True)
            if sonuc == "kuruldu":
                kurulan.append(p["import"])
            elif sonuc == "mevcut":
                atlanan.append(p["import"])
            else:
                hatalar.append(p["import"])

        # Opsiyonel paketleri dene
        for p in OPSIYONEL_PAKETLER:
            sonuc = self._paket_kontrol_kur(p, zorunlu=False)
            if sonuc == "kuruldu":
                kurulan.append(p["import"] + "(opsiyonel)")
            elif sonuc == "mevcut":
                atlanan.append(p["import"])

        # Sistem araçlarını kontrol et
        araclar = self._arac_kontrol()

        # Durumu kaydet
        self.durum = {
            "versiyon":  _VERSIYON,
            "tamam":     len(hatalar) == 0,
            "platform":  self.platform,
            "zaman":     time.time(),
            "kurulan":   kurulan,
            "hatalar":   hatalar,
            "araclar":   araclar,
        }
        self._durum_kaydet()

        ozet = {"platform": self.platform, "kurulan": kurulan, "atlanan": atlanan, "hata": hatalar}
        self._log(f"📦 [ORTAM]: Kurulum tamamlandı → {ozet}")
        return ozet

    # -----------------------------------------------------------------------
    # Platform tespiti
    # -----------------------------------------------------------------------

    def _platform_tespit(self) -> str:
        """Android/Termux, iOS/iSH, Linux veya Windows döndürür."""
        # Termux (Android) — /data/data/com.termux var mı?
        if os.path.isdir("/data/data/com.termux"):
            return "TERMUX_ANDROID"
        # iSH (iOS) — /etc/ish_version veya uname -a'da 'ish' var mı?
        if os.path.exists("/etc/ish_version"):
            return "ISH_IOS"
        uname = platform.uname()
        if "ish" in uname.release.lower():
            return "ISH_IOS"
        # Normal Linux
        if sys.platform.startswith("linux"):
            return "LINUX"
        if sys.platform == "darwin":
            return "MACOS"
        if sys.platform == "win32":
            return "WINDOWS"
        return "BILINMEYEN"

    def _pip_komutu(self) -> list:
        """pip3'ü yoksa pip'i döndürür."""
        if shutil.which("pip3"):
            return ["pip3", "install", "--quiet", "--upgrade"]
        return ["pip", "install", "--quiet", "--upgrade"]

    def _paket_yoneticisi(self) -> str | None:
        """Termux pkg, apt, apt-get veya None döndürür."""
        for mgr in ["pkg", "apt-get", "apt"]:
            if shutil.which(mgr):
                return mgr
        return None

    # -----------------------------------------------------------------------
    # Paket kontrol / kurulum
    # -----------------------------------------------------------------------

    def _paket_kontrol_kur(self, paket: dict, zorunlu: bool) -> str:
        """
        Paketi dener; eksikse pip üzerinden kurar.

        Returns:
            "mevcut" | "kuruldu" | "hata"
        """
        import_adi = paket["import"]
        pip_adi    = paket["pip"]

        # Önce import et
        if self._import_kontrol(import_adi):
            return "mevcut"

        self._log(f"📥 [ORTAM]: {import_adi} eksik, kuruluyor...")

        # Termux'ta önce pkg dene
        if self.platform == "TERMUX_ANDROID" and self.pkg_mgr == "pkg":
            termux_adi = paket.get("termux", pip_adi)
            if self._komut_calistir(["pkg", "install", "-y", termux_adi]):
                if self._import_kontrol(import_adi):
                    self._log(f"✅ [ORTAM]: {import_adi} pkg ile kuruldu.")
                    return "kuruldu"

        # pip ile kur
        if self._komut_calistir(self.pip_cmd + [pip_adi]):
            if self._import_kontrol(import_adi):
                self._log(f"✅ [ORTAM]: {import_adi} pip ile kuruldu.")
                return "kuruldu"

        if zorunlu:
            self._log(f"❌ [ORTAM]: {import_adi} kurulamadı!")
        else:
            self._log(f"⚠️  [ORTAM]: {import_adi} (opsiyonel) atlandı.")
        return "hata"

    def _import_kontrol(self, isim: str) -> bool:
        """Modülün import edilip edilemeyeceğini kontrol eder."""
        try:
            importlib.import_module(isim)
            return True
        except ImportError:
            return False

    def _komut_calistir(self, komut: list) -> bool:
        """Komutu sessizce çalıştırır; başarıysa True döner."""
        try:
            result = subprocess.run(
                komut,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
            )
            return result.returncode == 0
        except Exception as e:
            self._log(f"⚠️  [ORTAM]: Komut hatası ({' '.join(komut)}): {e}")
            return False

    # -----------------------------------------------------------------------
    # Sistem araçları kontrolü
    # -----------------------------------------------------------------------

    def _arac_kontrol(self) -> dict:
        """Önemli sistem araçlarının varlığını kontrol eder."""
        araclar = {}
        for arac in ["python3", "pip3", "git", "curl", "wget", "fastboot", "adb"]:
            araclar[arac] = bool(shutil.which(arac))
        self._log(f"🔧 [ORTAM]: Araçlar → {araclar}")
        return araclar

    # -----------------------------------------------------------------------
    # Durum dosyası
    # -----------------------------------------------------------------------

    def _durum_yukle(self) -> dict:
        try:
            if os.path.exists(_DURUM_YOLU):
                with open(_DURUM_YOLU, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _durum_kaydet(self):
        try:
            os.makedirs(os.path.dirname(_DURUM_YOLU), exist_ok=True)
            with open(_DURUM_YOLU, "w") as f:
                json.dump(self.durum, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"⚠️  [ORTAM]: Durum kaydedilemedi: {e}")

    # -----------------------------------------------------------------------
    # Yardımcı
    # -----------------------------------------------------------------------

    def _log(self, mesaj: str):
        print(mesaj)
        self.log_satir.append(mesaj)

    def platform_bilgisi(self) -> dict:
        """Anlık platform özetini döndürür."""
        return {
            "platform":  self.platform,
            "python":    sys.version,
            "pip":       " ".join(self.pip_cmd),
            "pkg_mgr":   self.pkg_mgr,
        }


# -----------------------------------------------------------------------
# Bağımsız çalıştırma / test
# -----------------------------------------------------------------------

if __name__ == "__main__":
    hazir = OrtamHazirla()
    print(f"\n📋 Platform Bilgisi: {hazir.platform_bilgisi()}\n")
    sonuc = hazir.baslat()
    print(f"\n🎯 Sonuç: {sonuc}")
