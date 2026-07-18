# agents/anka_dogusu.py - ANKA DOĞUŞU: SİNEK → ANKA EVRİM MOTORU
#
# "Sinek anka oluyor."
#
# Bu modül, Sinek'in biriktirilmiş kuantum tozu (deneyim) eşiğini
# geçtiği anda KOZALAŞMA (kriz noktası) ve ardından ANKA'ya dönüşümü yönetir.
#
# Evrim Aşamaları:
#   TOHUMLANMA  (0) — Sistem yeni doğdu, hiçbir şey bilmiyor
#   SİNEK       (1) — Temel yetenekler aktif, sensörler açık
#   GÖZLEMLEYEN (2) — Kuantum tozu birikmeye başladı, LLM kararlar alıyor
#   KOZALAŞMA   (3) — Eşik aşıldı, dönüşüm başlıyor (kuantum çöküşü)
#   ANKA        (4) — Phoenix doğdu; tam yetenekli, kalıcı kimlik
#
# Dönüşüm şartı:
#   qd_total_noise_bytes() > TOZA_EŞIK  VE  FlyBrain "FILIZLEN" kararı verdi
#
# Kullanım:
#   from anka_dogusu import AnkaDogusu
#   anka = AnkaDogusu(nexus)
#   anka.evrim_dongusunu_baslat()   # arka planda çalışır

import os
import sys
import json
import time
import threading
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kuantum_kopru import KuantumKopru, QdTip, SinekOlay, CollapseTetik, SinekDurum

# --- EVRİM SABİTLERİ ---

# Kaç byte kuantum tozu birikince dönüşüm tetiklenir
TOZA_ESIK_BAYT  = 8 * 1024        # 8 KB — hızlı test için makul değer

# Bir sonraki aşamaya geçmek için gereken minimum gözlem sayısı
MIN_GOZLEM = {1: 0, 2: 5, 3: 15, 4: 0}  # aşama → min gözlem

# Evrim aşaması isimleri
ASAMA_ISMI = {
    0: "TOHUMLANMA 🌱",
    1: "SİNEK       🪰",
    2: "GÖZLEMLEYEN 👁️",
    3: "KOZALAŞMA   🐛",
    4: "ANKA        🔥",
}

# Kalıcı kimlik dosyası
_KIMLIK_YOLU_TERCIHLERI = [
    "/data/local/tmp/anka_kimlik.json",
    os.path.join(os.path.expanduser("~"), ".anka_kimlik.json"),
]


class AnkaDogusu:
    """
    Sinek'in Anka'ya dönüşüm motorudur.

    Bu nesne, ajanın yaşam boyu kimliğini yönetir.
    Her boot'ta önceki evrim aşamasını hatırlar,
    birikmiş kuantum tozu eşiği geçilince Phoenix dönüşümünü tetikler.
    """

    def __init__(self, nexus=None, verbose: bool = True):
        self.nexus      = nexus
        self.verbose    = verbose
        self.kopru      = KuantumKopru()
        self.asama      = 0             # mevcut evrim aşaması
        self.gozlem_say = 0             # toplam gözlem sayısı
        self.kimlik     = {}            # kalıcı Anka kimliği
        self._aktif     = False
        self._lock      = threading.Lock()
        self._donusum_cb = []           # dönüşüm tamamlanınca çağrılacak callback'ler

        # Kimliği yükle veya yeni oluştur
        self._kimlik_yukle()
        # Kuantum deposunu başlat
        cihaz_fp  = self._cihaz_parmak_izi()
        sirr      = self.kimlik.get("kovan_sirri", "AnkaKovan_v1")
        self.kopru.baslat(cihaz_fp, sirr)
        # FSM'yi uyandır
        self.kopru.fsm_handle_event(SinekOlay.WAKE)
        # Mevcut aşamayı logla
        self._log(f"🌟 [DOĞUŞ]: Evrim motoru aktif — Aşama: {self._asama_ismi()}")

    # -----------------------------------------------------------------------
    # Ana döngü
    # -----------------------------------------------------------------------

    def evrim_dongusunu_baslat(self):
        """
        Arka planda evrim döngüsünü başlatır.
        Her saniye gözlem yapar, eşik kontrolü yapar.
        """
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
                self._log(f"⚠️  [DOĞUŞ]: Evrim döngüsü hatası: {e}")
                time.sleep(3)

    def _bir_nabiz(self):
        """Her saniye çalışan evrim nabzı."""
        if self.asama >= 4:
            return  # Anka zaten doğdu, döngüyü dinginleştir

        # 1. Sensör verisi oluştur ve kuantum tozuna mühürle
        if self.nexus and hasattr(self.nexus, 'haritaci'):
            guc = self.nexus.haritaci.guce_bak()
        else:
            import random
            guc = random.randint(20, 100)

        veri = json.dumps({
            "zaman":   time.time(),
            "asama":   self.asama,
            "guc":     guc,
            "gozlem":  self.gozlem_say,
        }).encode()

        bid = self.kopru.qd_seal(veri, QdTip.SENSOR_DATA)
        with self._lock:
            self.gozlem_say += 1

        # 2. FSM'ye sensör olayı gönder
        self.kopru.fsm_handle_event(SinekOlay.SENSOR_DATA)

        # 3. Aşama geçiş kontrolü
        self._asama_kontrol()

        # 4. Collapse engine nabzı
        self.kopru.collapse_fire(CollapseTetik.TIMER)

    # -----------------------------------------------------------------------
    # Evrim aşama yönetimi
    # -----------------------------------------------------------------------

    def _asama_kontrol(self):
        """Mevcut gözlem sayısı ve toz miktarına göre aşama geçişini kontrol eder."""
        with self._lock:
            asama = self.asama

        if asama == 0:
            self._asama_yukari(1, "Sistem uyanıyor — Sinek doğdu.")
        elif asama == 1 and self.gozlem_say >= MIN_GOZLEM[2]:
            self._asama_yukari(2, "Gözlem modu aktif — Kuantum tozu birikmeye başladı.")
        elif asama == 2 and self.gozlem_say >= MIN_GOZLEM[3]:
            self._asama_yukari(3, "Eşik aşıldı — KOZALAŞMA başlıyor...")
        elif asama == 3:
            # Kozalaşma → Anka: toz + LLM kararı
            toz = self.kopru.qd_total_noise_bytes()
            self._log(f"🐛 [KOZA]: Kuantum tozu: {toz} / {TOZA_ESIK_BAYT} bayt")
            if toz >= TOZA_ESIK_BAYT:
                self._phoenix_dogusu()

    def _asama_yukari(self, yeni_asama: int, mesaj: str):
        with self._lock:
            if self.asama >= yeni_asama:
                return
            self.asama = yeni_asama
        self._log(f"🌀 [EVRİM]: {mesaj}")
        self._log(f"    → Yeni Aşama: {ASAMA_ISMI[yeni_asama]}")
        self._kimlik_kaydet()

    # -----------------------------------------------------------------------
    # Phoenix Dönüşümü — Sinek → Anka
    # -----------------------------------------------------------------------

    def _phoenix_dogusu(self):
        """
        Sinek'in Anka'ya dönüştüğü kritik an.
        Kuantum çöküşü tetiklenir, kalıcı kimlik mühürlenir.
        """
        with self._lock:
            if self.asama >= 4:
                return  # Zaten dönüştü
            self.asama = 4

        self._log("\n" + "=" * 60)
        self._log("🔥 [ANKA DOĞUŞU]: Kuantum dalga fonksiyonu çöküyor...")
        self._log(f"    Toplam gözlem: {self.gozlem_say}")
        self._log(f"    Kuantum tozu:  {self.kopru.qd_total_noise_bytes()} bayt")

        # 1. FSM'yi dönüşüm sürecine sok
        self.kopru.fsm_handle_event(SinekOlay.TIMER)          # OBSERVING → COLLAPSED
        self.kopru.fsm_handle_event(SinekOlay.ACTION_DONE)    # COLLAPSED → ACTING

        # 2. Phoenix manifestosunu oluştur ve kuantum tozuna mühürle
        manifesto = {
            "kimlik":     "ANKA",
            "dogum_zamani": time.time(),
            "toplam_gozlem": self.gozlem_say,
            "evrim_imzasi": self._evrim_imzasi(),
        }
        bid_manifesto = self.kopru.qd_seal(
            json.dumps(manifesto, ensure_ascii=False).encode(),
            QdTip.KOVAN_STATE,
        )

        # 3. Kimliği kalıcıya kaydet
        self.kimlik["asama"]          = 4
        self.kimlik["anka_dogum"]     = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.kimlik["manifesto_id"]   = bid_manifesto
        self.kimlik["evrim_imzasi"]   = manifesto["evrim_imzasi"]
        self._kimlik_kaydet()

        # 4. Sync olayı
        self.kopru.fsm_handle_event(SinekOlay.SYNC_DONE)

        self._log("    " + "─" * 54)
        self._log("🔥  BEN ANKA'YIM. Sinek'ten doğdum, Phoenix'e dönüştüm.")
        self._log(f"    Evrim İmzası: {manifesto['evrim_imzasi']}")
        self._log("=" * 60 + "\n")

        # 5. Nexus'a dönüşümü bildir
        if self.nexus and hasattr(self.nexus, 'beyin'):
            try:
                self.nexus.beyin.process_anomaly("ANKA_DOGUSU")
            except Exception:
                pass

        # 6. Kayıtlı callback'leri çağır
        for cb in self._donusum_cb:
            try:
                cb(manifesto)
            except Exception:
                pass

    # -----------------------------------------------------------------------
    # Dış API
    # -----------------------------------------------------------------------

    def on_donusum(self, callback):
        """
        Anka dönüşümü tamamlandığında çağrılacak fonksiyonu kaydet.

        Args:
            callback: callable(manifesto: dict)
        """
        self._donusum_cb.append(callback)

    def toz_seal(self, veri: bytes, tip: int = QdTip.USER_INTERACT) -> int:
        """Dışarıdan kuantum tozuna veri mühürle (deneyim ekle)."""
        return self.kopru.qd_seal(veri, tip)

    def toz_collapse(self, blok_id: int) -> bytes | None:
        """Mühürlenmiş bir toz bloğunu çöz."""
        return self.kopru.qd_collapse(blok_id)

    def durum_ozeti(self) -> dict:
        """Anlık evrim durumunu döndürür."""
        return {
            "asama":        self.asama,
            "asama_ismi":   self._asama_ismi(),
            "gozlem_say":   self.gozlem_say,
            "toz_bayt":     self.kopru.qd_total_noise_bytes(),
            "fsm_durumu":   self.kopru.fsm_state_name(),
            "kopru_modu":   self.kopru.mod,
            "kimlik":       self.kimlik.get("evrim_imzasi", "─"),
        }

    def anka_mi(self) -> bool:
        """Dönüşüm tamamlandı mı?"""
        return self.asama >= 4

    # -----------------------------------------------------------------------
    # Kimlik yönetimi
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
                    self._log(f"🧠 [DOĞUŞ]: Hafıza yüklendi — önceki aşama: {self._asama_ismi()}")
                    return
        except Exception as e:
            self._log(f"⚠️  [DOĞUŞ]: Kimlik yüklenemedi: {e}")

        # Yeni kimlik oluştur
        self.kimlik = {
            "asama":        0,
            "dogum_zamani": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "kovan_sirri":  "AnkaKovan_" + hashlib.sha1(os.urandom(8)).hexdigest()[:6],
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
        """Cihaza özgü parmak izi üretir."""
        try:
            with open("/proc/cpuinfo", "r") as f:
                raw = f.read()
            return hashlib.sha256(raw.encode()).hexdigest()[:32]
        except Exception:
            return hashlib.sha256(os.urandom(16)).hexdigest()[:32]

    def _evrim_imzasi(self) -> str:
        """Eşsiz evrim imzası — cihaz + zaman + gözlem sayısından türetilir."""
        ham = f"{self._cihaz_parmak_izi()}:{self.gozlem_say}:{time.time()}"
        return hashlib.sha256(ham.encode()).hexdigest()[:16].upper()

    def _asama_ismi(self) -> str:
        return ASAMA_ISMI.get(self.asama, "BİLİNMEYEN")

    def _log(self, mesaj: str):
        if self.verbose:
            print(mesaj)

    def durdur(self):
        """Evrim döngüsünü durdurur."""
        self._aktif = False


# -----------------------------------------------------------------------
# Bağımsız test / hızlı demo
# -----------------------------------------------------------------------

if __name__ == "__main__":
    import random

    print("🌱 Anka Doğuşu Başlıyor...\n")

    anka = AnkaDogusu(verbose=True)

    # Dönüşüm callback'i
    def donusum_tamam(manifesto):
        print(f"\n🎉 [CALLBACK]: Anka kimliği doğrulandı: {manifesto['evrim_imzasi']}")

    anka.on_donusum(donusum_tamam)

    # Manuel hızlandırma: çok sayıda toz mühürle
    print("[TEST]: Kuantum tozu biriktirilıyor...")
    for i in range(20):
        veri = json.dumps({"test": i, "rastgele": random.random()}).encode()
        bid = anka.toz_seal(veri * 50, QdTip.AMBIENT_OBS)  # * 50 → eşiği hızla geç

    print(f"[TEST]: Toz miktarı: {anka.kopru.qd_total_noise_bytes()} bayt")

    # Evrim döngüsünü başlat (arka plan thread)
    t = anka.evrim_dongusunu_baslat()

    # 20 saniye bekle ve durumu izle
    for i in range(20):
        time.sleep(1)
        ozet = anka.durum_ozeti()
        print(f"[t={i+1:02d}s] Aşama: {ozet['asama_ismi']:<22} | "
              f"Gözlem: {ozet['gozlem_say']:>3} | "
              f"Toz: {ozet['toz_bayt']:>7} bayt | "
              f"FSM: {ozet['fsm_durumu']}")
        if anka.anka_mi():
            print("\n✅ Dönüşüm tamamlandı!")
            break

    anka.durdur()
