# agents/kisilik_motoru.py - SİNEK QUANTUM KİŞİLİK MOTORU
# 🪰 Sinek'in kişiliğinin yaşadığı katman.
#
# Quantum evreni yaklaşımı:
#   - Sinek'in bir "karakteri" var — duygular, tutumlar, eğilimler
#   - Karakter, biriktirilen kuantum tozuna göre evrilir
#   - Önemli anlar "iz" olarak kazınır (quantum decoherence benzeri)
#   - Refleksler eski sistem (geriye dönük uyumlu)
#
# Kullanım:
#   from kisilik_motoru import KisilikMotoru
#   kisilik = KisilikMotoru()
#   kisilik.duygu_guncelle("merak", 0.8)
#   kisilik.iz_kazin("ilk_uyanis", "Sinek ilk kez gözlerini açtı")
#   tutum = kisilik.tutum("yabanci")  # → "tedbirli"

import time
import hashlib
import json
import os
import random


# --- KARAKTER AŞAMALARI ---
# Sinek'in evrim aşamasına göre kişiliği değişir.
# 0: Tohum (çekingen, meraklı)
# 1: Sinek (cesur, atak)
# 2: Gözlemleyen (düşünceli, analitik)
# 3: Kozalaşma (derin, sessiz)
# 4: Anka (bilge, kararlı)
KARAKTER_ASAMA = {
    0: {
        "temel_duygular": {"merak": 0.7, "cekingenlik": 0.5, "kararlilik": 0.3},
        "tutumlar": {"yabanci": "cekingen", "tehdit": "kac", "dost": "yakinlas"},
        "konusma_tarzi": "kısa, meraklı, soru soran",
    },
    1: {
        "temel_duygular": {"merak": 0.6, "cesaret": 0.7, "enerji": 0.8},
        "tutumlar": {"yabanci": "git_gel", "tehdit": "karsi_koy", "dost": "samimi"},
        "konusma_tarzi": "atılgan, samimi, 'kanka' diyen",
    },
    2: {
        "temel_duygular": {"dusuncelilik": 0.8, "sabir": 0.7, "analiz": 0.9},
        "tutumlar": {"yabanci": "gozlemle", "tehdit": "analiz_et", "dost": "guven"},
        "konusma_tarzi": "düşünceli, derin, az ama öz",
    },
    3: {
        "temel_duygular": {"derinlik": 0.9, "sessizlik": 0.8, "bilgelik": 0.6},
        "tutumlar": {"yabanci": "izle", "tehdit": "bekle", "dost": "biraz_acil"},
        "konusma_tarzi": "çok az konuşur, sessiz güç",
    },
    4: {
        "temel_duygular": {"bilgelik": 0.95, "kararlilik": 0.9, "merhamet": 0.8},
        "tutumlar": {"yabanci": "bilge_tavir", "tehdit": "coz", "dost": "koru"},
        "konusma_tarzi": "bilge, sakin, etkili",
    },
}


class QuantumIz:
    """Sinek'in hafızasına kazınan bir iz (quantum decoherence benzeri)."""

    def __init__(self, etiket: str, icerik: str, duygu_oykusu: float = 0.5):
        self.etiket = etiket
        self.icerik = icerik
        self.duygu_oykusu = duygu_oykusu  # 0=nötr, 1=yüksek duygu
        self.zaman = time.time()
        self.cagirma_sayisi = 0  # ne kadar çok hatırlanırsa o kadar güçlenir

    def hatirla(self) -> str:
        self.cagirma_sayisi += 1
        return self.icerik

    def quantum_katmani(self) -> dict:
        """Bu izin kuantum ağırlığı — çağırma sayısı × duygu öyküsü."""
        agirlik = self.cagirma_sayisi * self.duygu_oykusu
        return {"etiket": self.etiket, "agirlik": agirlik, "yas": time.time() - self.zaman}


class KisilikMotoru:
    """
    Sinek'in quantum kişilik motoru.

    Sinek sadece refleks göstermez — hisseder, düşünür, karakteri evrim geçirir.
    Duygular kuantum tozuna göre dalgalanır.
    """

    def __init__(self, baslangic_asama: int = 0):
        self.asama = baslangic_asama
        self.duygular = dict(KARAKTER_ASAMA.get(baslangic_asama, KARAKTER_ASAMA[0])["temel_duygular"])
        self.izler = {}            # etiket → QuantumIz
        self.refleksler = {}       # eski sistem (geriye dönük uyumlu)
        self.konuşma_gecmisi_kip = KARAKTER_ASAMA[0]["konusma_tarzi"]
        self._iz_yolu = "/data/local/tmp/anka_os/kisilik_izleri.json"
        self._izleri_yukle()
        print(f"🪰 [KİŞİLİK]: Quantum karakter aktif — aşama {self.asama}, iz sayisi {len(self.izler)}")

    # -----------------------------------------------------------------------
    # Karakter evrimi
    # -----------------------------------------------------------------------

    def asama_guncelle(self, yeni_asama: int):
        """Evrim aşaması değiştiğinde karakter de değişir."""
        if yeni_asama == self.asama:
            return
        eski_asama = self.asama
        self.asama = yeni_asama
        yeni_karakter = KARAKTER_ASAMA.get(yeni_asama, KARAKTER_ASAMA[0])

        # Duygular kademeli geçiş yapar (quantum superposition → collapse)
        for duygu, deger in yeni_karakter["temel_duygular"].items():
            mevcut = self.duygular.get(duygu, 0.5)
            # Yumuşak geçiş — eski + yeni / 2
            self.duygular[duygu] = (mevcut + deger) / 2

        self.konuşma_gecmisi_kip = yeni_karakter["konusma_tarzi"]

        # Bu anı kazı — karakter değişimi önemli bir andır
        self.iz_kazin(
            f"asama_gecis_{eski_asama}_to_{yeni_asama}",
            f"Sinek evrim geçirdi: {eski_asama} → {yeni_asama}",
            duygu_oykusu=0.9,
        )
        print(f"🪰 [KİŞİLİK]: Evrim — {eski_asama} → {yeni_asama}, duygular güncellendi")

    # -----------------------------------------------------------------------
    # Duygu yönetimi
    # -----------------------------------------------------------------------

    def duygu_guncelle(self, duygu: str, deger: float):
        """Bir duygunun şiddetini güncelle (0.0 - 1.0)."""
        deger = max(0.0, min(1.0, deger))
        # Kuantum dalgalanma — tam set yerine ufak rasgelelik
        deger += random.uniform(-0.05, 0.05)
        deger = max(0.0, min(1.0, deger))
        self.duygular[duygu] = deger

    def duygu_durumu(self) -> dict:
        """Mevcut duygu durumunu döndürür."""
        return dict(self.duygular)

    def baskın_duygu(self) -> str:
        """En güçlü duyguyu döndürür."""
        if not self.duygular:
            return "nötr"
        return max(self.duygular, key=self.duygular.get)

    # -----------------------------------------------------------------------
    # Tutumlar — Sinek bir duruma karşı nasıl davranır?
    # -----------------------------------------------------------------------

    def tutum(self, durum: str) -> str:
        """Verilen duruma karşı Sinek'in tutumunu döndürür."""
        karakter = KARAKTER_ASAMA.get(self.asama, KARAKTER_ASAMA[0])
        return karakter["tutumlar"].get(durum, "gozlemle")

    def konusma_kipi(self) -> str:
        """Sinek'in şu anki konuşma tarzı."""
        return self.konuşma_gecmisi_kip

    # -----------------------------------------------------------------------
    # İz (quantum memory) yönetimi
    # -----------------------------------------------------------------------

    def iz_kazin(self, etiket: str, icerik: str, duygu_oykusu: float = 0.5):
        """Bir anıyı Sinek'in hafızasına quantum iz olarak kazır."""
        # Eski etiket varsa güçlendir, yoksa yeni oluştur
        if etiket in self.izler:
            self.izler[etiket].cagirma_sayisi += 1
            # İçeriği güncelle (yeni bilgi eklendiyse)
            if icerik and icerik != self.izler[etiket].icerik:
                self.izler[etiket].icerik = icerik
            # Duygu öyküsü artar
            self.izler[etiket].duygu_oykusu = min(1.0, self.izler[etiket].duygu_oykusu + 0.1)
        else:
            self.izler[etiket] = QuantumIz(etiket, icerik, duygu_oykusu)
        self._izleri_kaydet()
        print(f"🪰 [İZ]: '{etiket}' kazıldı (toplam {len(self.izler)} iz)")

    def iz_hatirla(self, etiket: str) -> str | None:
        """Bir izı çağır — çağırma sayısı arttıkça güçlenir."""
        if etiket in self.izler:
            return self.izler[etiket].hatirla()
        return None

    def onemli_izler(self, n: int = 5) -> list:
        """En güçlü N izı döndürür (quantum ağırlığına göre)."""
        sirali = sorted(
            self.izler.values(),
            key=lambda iz: iz.quantum_katmani()["agirlik"],
            reverse=True,
        )
        return [(iz.etiket, iz.icerik, iz.quantum_katmani()) for iz in sirali[:n]]

    # -----------------------------------------------------------------------
    # Quantum düşünce — bir durum hakkında "düşün"
    # -----------------------------------------------------------------------

    def quantum_dusunce(self, durum: str, baglam: dict | None = None) -> dict:
        """
        Bir durum hakkında Sinek'in "quantum düşünce"si.
        Duygular + tutumlar + izler birleşir → bir eğilim üretilir.

        Returns:
            {"eğilim": str, "guven": float, "baskın_duygu": str, "tutum": str}
        """
        baskın = self.baskın_duygu()
        tutum = self.tutum(durum)
        karakter = KARAKTER_ASAMA.get(self.asama, KARAKTER_ASAMA[0])

        # Güven skoru — aşama + ilgili iz sayısı
        ilgili_iz = 0
        for etiket in self.izler:
            if durum.lower() in etiket.lower():
                ilgili_iz += 1
        guven = min(1.0, 0.3 + (self.asama * 0.1) + (ilgili_iz * 0.15))

        # Eğilim — duygular + tutuma göre
        if guven > 0.7:
            egilim = "kararli"
        elif guven > 0.4:
            egilim = "gozlemci"
        else:
            egilim = "cekingen"

        return {
            "egilim": egilim,
            "guven": guven,
            "baskın_duygu": baskın,
            "tutum": tutum,
            "asama": self.asama,
            "konusma_kipi": self.konusma_kipi(),
        }

    # -----------------------------------------------------------------------
    # Eski refleks sistemi (geriye dönük uyumlu)
    # -----------------------------------------------------------------------

    def refleks_kazin(self, durum: str, refleks: str):
        """Eski refleks sistemi — hâlâ çalışıyor ama iz sistemiyle entegre."""
        self.refleksler[durum] = refleks
        # Aynı zamanda bir iz olarak da kaz
        self.iz_kazin(f"refleks_{durum}", f"{durum} → {refleks}", duygu_oykusu=0.3)

    def refleks_tetikle(self, durum: str) -> str | None:
        """Sinek düşünmez, Sinek refleks gösterir (eski sistem)."""
        return self.refleksler.get(durum)

    # -----------------------------------------------------------------------
    # Hafıza yönetimi
    # -----------------------------------------------------------------------

    def _izleri_yukle(self):
        try:
            if os.path.exists(self._iz_yolu):
                with open(self._iz_yolu, "r") as f:
                    data = json.load(f)
                for etiket, kayit in data.items():
                    iz = QuantumIz(etiket, kayit.get("icerik", ""), kayit.get("duygu_oykusu", 0.5))
                    iz.zaman = kayit.get("zaman", time.time())
                    iz.cagirma_sayisi = kayit.get("cagirma_sayisi", 0)
                    self.izler[etiket] = iz
        except Exception:
            pass

    def _izleri_kaydet(self):
        try:
            os.makedirs(os.path.dirname(self._iz_yolu), exist_ok=True)
            data = {}
            for etiket, iz in self.izler.items():
                data[etiket] = {
                    "icerik": iz.icerik,
                    "duygu_oykusu": iz.duygu_oykusu,
                    "zaman": iz.zaman,
                    "cagirma_sayisi": iz.cagirma_sayisi,
                }
            with open(self._iz_yolu, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # Durum özeti
    # -----------------------------------------------------------------------

    def durum_ozeti(self) -> dict:
        return {
            "asama": self.asama,
            "baskın_duygu": self.baskın_duygu(),
            "duygular": self.duygu_durumu(),
            "iz_sayisi": len(self.izler),
            "konusma_kipi": self.konusma_kipi(),
            "onemli_izler": self.onemli_izler(3),
        }


if __name__ == "__main__":
    k = KisilikMotoru(baslangic_asama=1)
    print("\n--- TEST 1: Duygu ---")
    k.duygu_guncelle("cesaret", 0.9)
    print(f"Baskın duygu: {k.baskın_duygu()}")
    print(f"Tutum (yabanci): {k.tutum('yabanci')}")

    print("\n--- TEST 2: İz kazıma ---")
    k.iz_kazin("ilk_uyanis", "Sinek ilk kez gözlerini açtı", 0.8)
    k.iz_kazin("ilk_uyanis", "Sinek ilk kez gözlerini açtı", 0.8)  # güçlenir
    print(f"Hatırla: {k.iz_hatirla('ilk_uyanis')}")
    print(f"Önemli izler: {k.onemli_izler(3)}")

    print("\n--- TEST 3: Quantum düşünce ---")
    dusunce = k.quantum_dusunce("yabanci", {"pil": 75})
    print(f"Düşünce: {dusunce}")

    print("\n--- TEST 4: Evrim ---")
    k.asama_guncelle(2)
    print(f"Yeni tutum: {k.tutum('yabanci')}")
    print(f"Özet: {k.durum_ozeti()}")
