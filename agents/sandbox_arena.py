# agents/sandbox_arena.py - ANKA OS SANDBOX DENEME ALANI
#
# Ajanın güvenli biçimde denemeler yapabileceği izole bir alan.
# İnternetten paket indirebilir, kod çalıştırabilir, sonuçları değerlendirebilir
# ve başarılı deneyleri kalıcı hafızaya alabilir.
#
# Özellikler:
#   - Kod çalıştırma (subprocess izolasyonu, timeout korumalı)
#   - Paket indirme / test kurulumu (geçici venv)
#   - HTTP fetch (başlık + içerik önizlemesi)
#   - Deney geçmişi (JSON kaydı)
#   - Otomatik temizlik
#
# Kullanım:
#   from sandbox_arena import SandboxArena
#   arena = SandboxArena()
#   sonuc = arena.kod_calistir("print('merhaba dünya')")
#   sonuc = arena.paket_test_et("requests")
#   sonuc = arena.url_fetch("https://example.com")

import os
import sys
import json
import time
import shutil
import hashlib
import tempfile
import subprocess
import urllib.request
import urllib.error
from typing import Any

# Sandbox geçici dizini
_SANDBOX_KOKU = os.path.join(tempfile.gettempdir(), "anka_sandbox")
_GECMIS_DOSYA = os.path.join(_SANDBOX_KOKU, "deney_gecmisi.json")

# Güvenlik sınırları
_MAX_SURE    = 30    # saniye — tek deney için
_MAX_CIKTI   = 8192  # bayt  — stdout/stderr kırpma
_MAX_GECMIS  = 100   # kaydedilen deney sayısı


class SandboxArena:
    """
    Anka'nın güvenli deney ve keşif alanı.
    Her deney izole bir subprocess'te çalışır, sonuçlar kaydedilir.
    """

    def __init__(self, verbose: bool = True):
        self.verbose  = verbose
        self.gecmis   = self._gecmis_yukle()
        os.makedirs(_SANDBOX_KOKU, exist_ok=True)
        self._log("🧪 [SANDBOX]: Deneme alanı hazır.")

    # -----------------------------------------------------------------------
    # 1. Kod çalıştırma
    # -----------------------------------------------------------------------

    def kod_calistir(self, kod: str, timeout: int = _MAX_SURE) -> dict:
        """
        Verilen Python kodunu izole subprocess'te çalıştırır.

        Args:
            kod:     Çalıştırılacak Python kaynak kodu
            timeout: Saniye cinsinden maksimum süre

        Returns:
            {"basari": bool, "cikti": str, "hata": str, "sure": float}
        """
        self._log(f"▶️  [SANDBOX]: Kod çalıştırılıyor ({len(kod)} karakter)...")

        # Kodu geçici dosyaya yaz
        kod_id   = hashlib.sha1(kod.encode()).hexdigest()[:8]
        kod_yolu = os.path.join(_SANDBOX_KOKU, f"deneme_{kod_id}.py")
        try:
            with open(kod_yolu, "w", encoding="utf-8") as f:
                f.write(kod)

            baslangic = time.time()
            result = subprocess.run(
                [sys.executable, kod_yolu],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                cwd=_SANDBOX_KOKU,
            )
            sure = round(time.time() - baslangic, 3)

            cikti = result.stdout.decode("utf-8", errors="replace")[:_MAX_CIKTI]
            hata  = result.stderr.decode("utf-8", errors="replace")[:_MAX_CIKTI]
            basari = result.returncode == 0

        except subprocess.TimeoutExpired:
            sure   = timeout
            cikti  = ""
            hata   = f"⏰ Zaman aşımı ({timeout}s)"
            basari = False
        except Exception as e:
            sure   = 0.0
            cikti  = ""
            hata   = str(e)
            basari = False
        finally:
            if os.path.exists(kod_yolu):
                os.remove(kod_yolu)

        sonuc = {"basari": basari, "cikti": cikti.strip(), "hata": hata.strip(), "sure": sure}
        self._kaydet("KOD", kod[:120], sonuc)
        self._log(f"{'✅' if basari else '❌'} [SANDBOX]: Kod → {sure}s | {cikti[:80] if basari else hata[:80]}")
        return sonuc

    # -----------------------------------------------------------------------
    # 2. Paket test kurulumu
    # -----------------------------------------------------------------------

    def paket_test_et(self, paket_adi: str, timeout: int = 120) -> dict:
        """
        Paketi geçici bir dizine pip ile kurar; sistemi kirletmeden test eder.
        Deney bitince geçici dizin silinir.

        Args:
            paket_adi: pip paket adı (ör. "requests", "httpx==0.24.0")

        Returns:
            {"basari": bool, "mesaj": str, "sure": float}
        """
        self._log(f"📥 [SANDBOX]: Paket test kuruluyor → {paket_adi}")

        gecici_dizin = tempfile.mkdtemp(prefix="anka_pkg_", dir=_SANDBOX_KOKU)
        try:
            baslangic = time.time()
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", gecici_dizin,
                 "--quiet", "--no-deps",
                 paket_adi],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
            sure = round(time.time() - baslangic, 3)

            basari = result.returncode == 0
            cikti  = result.stdout.decode("utf-8", errors="replace")
            hata   = result.stderr.decode("utf-8", errors="replace")
            mesaj  = (cikti if basari else hata).strip()[:400]

        except subprocess.TimeoutExpired:
            sure   = timeout
            basari = False
            mesaj  = f"⏰ Zaman aşımı ({timeout}s)"
        except Exception as e:
            sure   = 0.0
            basari = False
            mesaj  = str(e)
        finally:
            shutil.rmtree(gecici_dizin, ignore_errors=True)

        sonuc = {"basari": basari, "mesaj": mesaj, "sure": sure}
        self._kaydet("PAKET", paket_adi, sonuc)
        self._log(f"{'✅' if basari else '❌'} [SANDBOX]: {paket_adi} → {sure}s")
        return sonuc

    # -----------------------------------------------------------------------
    # 3. URL fetch (başlık + içerik önizlemesi)
    # -----------------------------------------------------------------------

    def url_fetch(self, url: str, max_bayt: int = 4096, timeout: int = 10) -> dict:
        """
        Belirtilen URL'den içerik çeker (yalnızca önizleme).

        Args:
            url:      Hedef URL
            max_bayt: Maksimum içerik boyutu (varsayılan 4 KB)
            timeout:  Bağlantı zaman aşımı (saniye)

        Returns:
            {"basari": bool, "durum": int, "icerik": str, "boyut": int, "hata": str}
        """
        self._log(f"🌐 [SANDBOX]: Fetch → {url[:80]}")

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AnkaOS/1.0 SandboxArena"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as r:
                durum   = r.status
                ham     = r.read(max_bayt)
                icerik  = ham.decode("utf-8", errors="replace")
                boyut   = len(ham)
            sonuc = {"basari": True, "durum": durum, "icerik": icerik[:1000], "boyut": boyut, "hata": ""}
        except urllib.error.HTTPError as e:
            sonuc = {"basari": False, "durum": e.code, "icerik": "", "boyut": 0, "hata": str(e)}
        except Exception as e:
            sonuc = {"basari": False, "durum": 0, "icerik": "", "boyut": 0, "hata": str(e)}

        self._kaydet("FETCH", url[:80], sonuc)
        self._log(f"{'✅' if sonuc['basari'] else '❌'} [SANDBOX]: {url[:50]} → HTTP {sonuc['durum']}")
        return sonuc

    # -----------------------------------------------------------------------
    # 4. Kabuk komutu çalıştırma (salt okunur araçlar için)
    # -----------------------------------------------------------------------

    def kabuk_calistir(self, komut: str, timeout: int = _MAX_SURE) -> dict:
        """
        Kabuk komutunu izole subprocess'te çalıştırır.
        Yalnızca bilgi toplama komutları için kullan (uname, cat, ls, vb.).

        Returns:
            {"basari": bool, "cikti": str, "hata": str}
        """
        self._log(f"🖥️  [SANDBOX]: Kabuk → {komut[:60]}")
        try:
            result = subprocess.run(
                komut,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                cwd=_SANDBOX_KOKU,
            )
            cikti  = result.stdout.decode("utf-8", errors="replace")[:_MAX_CIKTI]
            hata   = result.stderr.decode("utf-8", errors="replace")[:_MAX_CIKTI]
            basari = result.returncode == 0
        except subprocess.TimeoutExpired:
            cikti  = ""
            hata   = f"⏰ Zaman aşımı ({timeout}s)"
            basari = False
        except Exception as e:
            cikti  = ""
            hata   = str(e)
            basari = False

        sonuc = {"basari": basari, "cikti": cikti.strip(), "hata": hata.strip()}
        self._kaydet("KABUK", komut[:60], sonuc)
        return sonuc

    # -----------------------------------------------------------------------
    # 5. Deney geçmişi
    # -----------------------------------------------------------------------

    def gecmis_al(self, tur: str | None = None, son_n: int = 10) -> list:
        """
        Deney geçmişini döndürür.

        Args:
            tur:   Filtre: "KOD", "PAKET", "FETCH", "KABUK" veya None (hepsi)
            son_n: Döndürülecek en son N kayıt

        Returns:
            List[dict]
        """
        kayitlar = self.gecmis
        if tur:
            kayitlar = [k for k in kayitlar if k.get("tur") == tur]
        return kayitlar[-son_n:]

    def temizle(self):
        """Sandbox dizinini ve geçmiş dosyasını temizler."""
        shutil.rmtree(_SANDBOX_KOKU, ignore_errors=True)
        os.makedirs(_SANDBOX_KOKU, exist_ok=True)
        self.gecmis = []
        self._log("🧹 [SANDBOX]: Alan temizlendi.")

    # -----------------------------------------------------------------------
    # Yardımcı: kayıt / log
    # -----------------------------------------------------------------------

    def _kaydet(self, tur: str, girdi: Any, sonuc: dict):
        kayit = {
            "tur":    tur,
            "girdi":  girdi,
            "sonuc":  sonuc,
            "zaman":  time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.gecmis.append(kayit)
        # Hafızayı sınırla
        if len(self.gecmis) > _MAX_GECMIS:
            self.gecmis = self.gecmis[-_MAX_GECMIS:]
        # Diske yaz
        try:
            with open(_GECMIS_DOSYA, "w", encoding="utf-8") as f:
                json.dump(self.gecmis, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _gecmis_yukle(self) -> list:
        try:
            if os.path.exists(_GECMIS_DOSYA):
                with open(_GECMIS_DOSYA, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _log(self, mesaj: str):
        if self.verbose:
            print(mesaj)


# -----------------------------------------------------------------------
# Bağımsız çalıştırma / test
# -----------------------------------------------------------------------

if __name__ == "__main__":
    arena = SandboxArena()

    print("\n--- TEST 1: Basit Python kodu ---")
    sonuc = arena.kod_calistir("import sys\nprint(f'Python: {sys.version}')")
    print(sonuc)

    print("\n--- TEST 2: Platform bilgisi ---")
    sonuc = arena.kod_calistir(
        "import platform, os\n"
        "print(platform.uname())\n"
        "print('Termux:', os.path.isdir('/data/data/com.termux'))\n"
        "print('iSH:', os.path.exists('/etc/ish_version'))"
    )
    print(sonuc)

    print("\n--- TEST 3: Paket test ---")
    sonuc = arena.paket_test_et("httpx")
    print(sonuc)

    print("\n--- TEST 4: URL fetch ---")
    sonuc = arena.url_fetch("https://httpbin.org/get")
    print(sonuc)

    print(f"\n📋 Son 5 deney: {arena.gecmis_al(son_n=5)}")
