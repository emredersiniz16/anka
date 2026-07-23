# agents/anka_dogusu.py - ANKA DOĞUŞU: SİNEK → ANKA EVRİM MOTORU
# v2: on_asama_degisti callback eklendi — aşama değişiminde bilinc haberdar olur.

import os
import sys
import json
import time
import threading
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kuantum_kopru import KuantumKopru, QdTip, SinekOlay, CollapseTetik, SinekDurum

TOZA_ESIK_BAYT = 8 * 1024
MIN_GOZLEM = {1: 0, 2: 5, 3: 15, 4: 0}

ASAMA_ISMI = {
    0: "TOHUMLANMA 🌱",
    1: "SİNEK       🪰",
    2: "GÖZLEMLEYEN 👁️",
    3: "KOZALAŞMA   🐛",
    4: "ANKA        🔥",
}

_KIMLIK_YOLU_TERCIHLERI = [
    "/data/local/tmp/anka_os/anka_kimlik.json",
    "/data/local/tmp/anka_kimlik.json",
]


class AnkaDogusu:
    """Sinek → Anka evrim motoru. Aşama değişimlerini callback ile bildirir."""

    def __init__(self, nexus=None, verbose: bool = True):
        self.nexus = nexus
        self.verbose = verbose
        self.kopru = KuantumKopru()
        self.asama = 0
        self.gozlem_say = 0
        self.kimlik = {}
        self._aktif = False
        self._lock = threading.Lock()
        self._donusum_cb = []        # Phoenix dönüşümü callback'leri
        self._asama_cb = []           # Aşama değişimi callback'leri

        self._kimlik_yukle()
        cihaz_fp = self._cihaz_parmak_izi()
        sirr = self.kimlik.get("kovan_sirri", "AnkaKovan_v1")
        self.kopru.baslat(cihaz_fp, sirr)
        self.kopru.fsm_handle_event(SinekOlay.WAKE)
        self._log(f"🌟 [DOĞUŞ]: Evrim motoru aktif — Aşama: {self._asama_ismi()}")

    def evrim_dongusunu_baslat(self):
        self._aktif = True
        t = threading.Thread(target=self._evrim_dongusu, daemon=True)
        t.start()
        return t

    def _evrim_dongusu(self):
        while self._aktif:
            try:
                self._bir_nabiz()
                time.sleep(1)
            except Exception as e:
                self._log(f"⚠️  [DOĞUŞ]: Döngü hatası: {e}")
                time.sleep(3)

    def _bir_nabiz(self):
        if self.asama >= 4:
            return
        if self.nexus and hasattr(self.nexus, 'haritaci'):
            guc = self.nexus.haritaci.guce_bak()
        else:
            import random
            guc = random.randint(20, 100)
        veri = json.dumps({
            "zaman": time.time(), "asama": self.asama,
            "guc": guc, "gozlem": self.gozlem_say,
        }).encode()
        self.kopru.qd_seal(veri, QdTip.SENSOR_DATA)
        with self._lock:
            self.gozlem_say += 1
        self.kopru.fsm_handle_event(SinekOlay.SENSOR_DATA)
        self._asama_kontrol()
        self.kopru.collapse_fire(CollapseTetik.TIMER)

    def _asama_kontrol(self):
        with self._lock:
            asama = self.asama
        if asama == 0:
            self._asama_yukari(1, "Sistem uyanıyor — Sinek doğdu.")
        elif asama == 1 and self.gozlem_say >= MIN_GOZLEM[2]:
            self._asama_yukari(2, "Gözlem modu aktif — Kuantum tozu birikmeye başladı.")
        elif asama == 2 and self.gozlem_say >= MIN_GOZLEM[3]:
            self._asama_yukari(3, "Eşik aşıldı — KOZALAŞMA başlıyor...")
        elif asama == 3:
            toz = self.kopru.qd_total_noise_bytes()
            self._log(f"🐛 [KOZA]: Kuantum tozu: {toz} / {TOZA_ESIK_BAYT} bayt")
            if toz >= TOZA_ESIK_BAYT:
                self._phoenix_dogusu()

    def _asama_yukari(self, yeni_asama: int, mesaj: str):
        with self._lock:
            if self.asama >= yeni_asama:
                return
            eski_asama = self.asama
            self.asama = yeni_asama
        self._log(f"🌀 [EVRİM]: {mesaj}")
        self._log(f"    → Yeni Aşama: {ASAMA_ISMI[yeni_asama]}")
        self._kimlik_kaydet()
        # Aşama değişimi callback'lerini çağır
        for cb in self._asama_cb:
            try:
                cb(eski_asama, yeni_asama)
            except Exception:
                pass

    def _phoenix_dogusu(self):
        with self._lock:
            if self.asama >= 4:
                return
            self.asama = 4
        self._log("\n" + "=" * 60)
        self._log("🔥 [ANKA DOĞUŞU]: Kuantum dalga fonksiyonu çöküyor...")
        self._log(f"    Toplam gözlem: {self.gozlem_say}")
        self._log(f"    Kuantum tozu:  {self.kopru.qd_total_noise_bytes()} bayt")
        self.kopru.fsm_handle_event(SinekOlay.TIMER)
        self.kopru.fsm_handle_event(SinekOlay.ACTION_DONE)
        manifesto = {
            "kimlik": "ANKA",
            "dogum_zamani": time.time(),
            "toplam_gozlem": self.gozlem_say,
            "evrim_imzasi": self._evrim_imzasi(),
        }
        bid_manifesto = self.kopru.qd_seal(
            json.dumps(manifesto, ensure_ascii=False).encode(), QdTip.KOVAN_STATE)
        self.kimlik["asama"] = 4
        self.kimlik["anka_dogum"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.kimlik["manifesto_id"] = bid_manifesto
        self.kimlik["evrim_imzasi"] = manifesto["evrim_imzasi"]
        self._kimlik_kaydet()
        self.kopru.fsm_handle_event(SinekOlay.SYNC_DONE)
        self._log("    " + "─" * 54)
        self._log("🔥  BEN ANKA'YIM. Sinek'ten doğdum, Phoenix'e dönüştüm.")
        self._log(f"    Evrim İmzası: {manifesto['evrim_imzasi']}")
        self._log("=" * 60 + "\n")
        if self.nexus and hasattr(self.nexus, 'beyin'):
            try:
                self.nexus.beyin.process_anomaly("ANKA_DOGUSU")
            except Exception:
                pass
        for cb in self._donusum_cb:
            try:
                cb(manifesto)
            except Exception:
                pass

    # -----------------------------------------------------------------------
    # Callback kayıt
    # -----------------------------------------------------------------------

    def on_donusum(self, callback):
        """Phoenix dönüşümü tamamlandığında çağrılacak callback."""
        self._donusum_cb.append(callback)

    def on_asama_degisti(self, callback):
        """Aşama değiştiğinde çağrılacak callback: callback(eski_asama, yeni_asama)."""
        self._asama_cb.append(callback)

    def toz_seal(self, veri: bytes, tip: int = QdTip.USER_INTERACT) -> int:
        return self.kopru.qd_seal(veri, tip)

    def toz_collapse(self, blok_id: int) -> bytes | None:
        return self.kopru.qd_collapse(blok_id)

    def durum_ozeti(self) -> dict:
        return {
            "asama": self.asama,
            "asama_ismi": self._asama_ismi(),
            "gozlem_say": self.gozlem_say,
            "toz_bayt": self.kopru.qd_total_noise_bytes(),
            "fsm_durumu": self.kopru.fsm_state_name(),
            "kopru_modu": self.kopru.mod,
            "kimlik": self.kimlik.get("evrim_imzasi", "─"),
        }

    def anka_mi(self) -> bool:
        return self.asama >= 4

    # -----------------------------------------------------------------------
    # Kimlik
    # -----------------------------------------------------------------------

    def _kimlik_yolu(self) -> str:
        for yol in _KIMLIK_YOLU_TERCIHLERI:
            try:
                os.makedirs(os.path.dirname(yol), exist_ok=True)
                test = yol + ".test"
                with open(test, "w") as f:
                    f.write("ok")
                os.remove(test)
                return yol
            except OSError:
                continue
        return _KIMLIK_YOLU_TERCIHLERI[-1]

    def _kimlik_yukle(self):
        yol = self._kimlik_yolu()
        try:
            if os.path.exists(yol):
                with open(yol, "r", encoding="utf-8") as f:
                    self.kimlik = json.load(f)
                    self.asama = min(self.kimlik.get("asama", 0), 4)
                    self._log(f"🧠 [DOĞUŞ]: Hafıza yüklendi — önceki: {self._asama_ismi()}")
                    return
        except Exception as e:
            self._log(f"⚠️  [DOĞUŞ]: Kimlik yüklenemedi: {e}")
        self.kimlik = {
            "asama": 0,
            "dogum_zamani": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "kovan_sirri": "AnkaKovan_" + hashlib.sha1(os.urandom(8)).hexdigest()[:6],
        }
        self._kimlik_kaydet()

    def _kimlik_kaydet(self):
        yol = self._kimlik_yolu()
        try:
            self.kimlik["asama"] = self.asama
            with open(yol, "w", encoding="utf-8") as f:
                json.dump(self.kimlik, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"⚠️  [DOĞUŞ]: Kimlik kaydedilemedi: {e}")

    def _cihaz_parmak_izi(self) -> str:
        try:
            with open("/proc/cpuinfo", "r") as f:
                raw = f.read()
            return hashlib.sha256(raw.encode()).hexdigest()[:32]
        except Exception:
            return hashlib.sha256(os.urandom(16)).hexdigest()[:32]

    def _evrim_imzasi(self) -> str:
        ham = f"{self._cihaz_parmak_izi()}:{self.gozlem_say}:{time.time()}"
        return hashlib.sha256(ham.encode()).hexdigest()[:16].upper()

    def _asama_ismi(self) -> str:
        return ASAMA_ISMI.get(self.asama, "BİLİNMEYER")

    def _log(self, mesaj: str):
        if self.verbose:
            print(mesaj)

    def durdur(self):
        self._aktif = False
