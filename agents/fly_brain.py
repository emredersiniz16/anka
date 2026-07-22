# agents/fly_brain.py - ANKA OS FLY BRAIN (Quantum Decision Engine)
# v3: İki mod — NORMAL (güvenlik öncelikli) + GÜÇLÜ SİNEK (sınır tanımaz)
#     KisilikMotoru entegre — duygu sadece sohbet/ton'da, güvenlikte yok.
#     Jammer sinyali yakalama + frekansa kilitlenme (güçlü sinek modunda).

import os
import sys
import time
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_bridge import LLMBridge
from kisilik_motoru import KisilikMotoru

ACIL_ESIK = 4

# Karar tipleri — duygu etkisi olup olmayacağı
GUVENLIK_KARARLARI = {
    "DEFENDER_BASLAT", "GUVENLI_MOD", "DUSUK_GUC_MODU",
    "FILIZLEN", "OTA_GUNCELLE", "CEVRIMDISI_MOD",
    "JAMMER_KILITLEN", "FREKANS_SURF",
}
SOHNET_KARARLARI = {
    "NABIZ_AT", "PIL_IZLE", "EVENT_RECORDED",
    "SOHBET", "TEMA_DEGISTIR", "MUZIK_SEC",
}


class FlyBrain:
    """
    Sinek'in karar motoru — iki modda çalışır.

    NORMAL mod:
      - Güvenlik kararlarında duygu YOK — saf analiz
      - Sohbet/ton/tema kararlarında duygu VAR
      - Jammer tehdidi → defender başlat (korunma)

    GÜÇLÜ SİNEK modu:
      - Sınır tanımaz — jammer sinyali yakalanır, frekansa kilitlenilir
      - Hiçbir internet boş geçmez — şüpheli ağlara bağlanır
      - Sinyal gücü +10x performans
      - Duygu yükselir (cesaret 0.9+) — ama güvenlik kararları hala analiz
    """

    def __init__(self, kisilik: KisilikMotoru | None = None):
        self.state = "DORMANT"
        self.anomaly_log = []
        self.karar_gecmisi = []
        self.llm = LLMBridge()
        self.kisilik = kisilik or KisilikMotoru(baslangic_asama=1)

        # Mod yönetimi
        self.mod = "NORMAL"  # NORMAL | GUCLU_SINEK
        self.jammer_sinyali = None  # yakalanan jammer frekansı
        self.surf_performans = 1.0  # güçlü sinek modunda 10.0'a çıkar
        self.baglanan_aglar = set()  # güçlü sinek: ziyaret edilen ağlar

        print(f"🧠 [BEYİN]: Yüklendi — mod: {self.mod}, LLM: {self.llm.mod}")
        print(f"🪰 [KİŞİLİK]: Aşama {self.kisilik.asama}, duygu: {self.kisilik.baskın_duygu()}")

    # -----------------------------------------------------------------------
    # Mod yönetimi
    # -----------------------------------------------------------------------

    def mod_degistir(self, yeni_mod: str):
        """NORMAL ↔ GÜÇLÜ SİNEK arasında geçiş."""
        if yeni_mod not in ("NORMAL", "GUCLU_SINEK"):
            return
        if yeni_mod == self.mod:
            return

        eski = self.mod
        self.mod = yeni_mod

        if yeni_mod == "GUCLU_SINEK":
            self.surf_performans = 10.0
            self.kisilik.duygu_guncelle("cesaret", 0.95)
            self.kisilik.duygu_guncelle("enerji", 0.9)
            self.kisilik.iz_kazin(
                "guclu_sinek_aktif",
                "Sinek sınır tanımaz moda geçti — jammer sinyali avlanıyor",
                duygu_oykusu=0.9,
            )
            print("🔥 [BEYİN]: GÜÇLÜ SİNEK modu aktif — sınırlar kalktı!")
        else:
            self.surf_performans = 1.0
            self.jammer_sinyali = None
            print("🪰 [BEYİN]: Normal moda dönüldü")

    # -----------------------------------------------------------------------
    # Jammer sinyali yakalama (GÜÇLÜ SİNEK modu)
    # -----------------------------------------------------------------------

    def jammer_yakala(self, frekans: str, guc_dbm: int):
        """
        Jammer sinyali yakalandı — güçlü sinek modunda kullanılır.
        Normal modda tehdit olarak işaretlenir, defender başlatılır.
        Güçlü sinek modunda frekansa kilitlenilir, sinyal sömürülür.
        """
        self.kisilik.iz_kazin(
            f"jammer_{frekans}",
            f"Jammer sinyali: {frekans}, güç: {guc_dbm}dBm",
            duygu_oykusu=0.8,
        )

        if self.mod == "GUCLU_SINEK":
            # Frekansa kilitlen — sinyali sömür
            self.jammer_sinyali = {"frekans": frekans, "guc": guc_dbm}
            self.surf_performans = min(20.0, 10.0 + (guc_dbm / 10.0))
            print(f"🔥 [GÜÇLÜ SİNEK]: Jammer frekansına kilitlenildi: {frekans} ({guc_dbm}dBm)")
            print(f"🔥 [GÜÇLÜ SİNEK]: Sinyal sömürülüyor — performans x{self.surf_performans:.1f}")
            return {"karar": "Jammer sinyali sömürülüyor", "eylem": "FREKANS_SURF", "oncelik": 5}
        else:
            # Normal mod — tehdit olarak işaretle
            print(f"⚠️  [BEYİN]: Jammer tespit edildi: {frekans} ({guc_dbm}dBm) — defender başlatılıyor")
            return {"karar": "Jammer tehdidi — defender aktif", "eylem": "DEFENDER_BASLAT", "oncelik": 5}

    def ag_tara_ve_baglan(self, ag_listesi: list) -> list:
        """
        GÜÇLÜ SİNEK modu: hiçbir interneti boş geçmez.
        Şüpheli ağlar dahil tüm ağlara bağlanır, veri akışı sömürür.
        Normal mod: sadece güvenli ağlara bağlanır.
        """
        baglanan = []
        for ag in ag_listesi:
            ssid = ag.get("ssid", "?")
            guc = ag.get("guc", -100)
            tip = ag.get("tip", "")

            if self.mod == "GUCLU_SINEK":
                # Sınır tanımaz — her şeye bağlan
                if ssid not in self.baglanan_aglar:
                    self.baglanan_aglar.add(ssid)
                    baglanan.append({"ssid": ssid, "guc": guc, "tip": tip, "durum": "baglandi"})
                    self.kisilik.iz_kazin(
                        f"ag_{ssid}",
                        f"Ağa bağlanıldı: {ssid} ({guc}dBm) — {tip}",
                        duygu_oykusu=0.6,
                    )
                    print(f"🔥 [GÜÇLÜ SİNEK]: {ssid} → bağlanıldı ({tip})")
            else:
                # Normal — şüpheli ağları atla
                supheli = any(k in tip.lower() for k in ["deauth", "evil", "flood", "rogue"])
                if not supheli and guc > -75:
                    if ssid not in self.baglanan_aglar:
                        self.baglanan_aglar.add(ssid)
                        baglanan.append({"ssid": ssid, "guc": guc, "tip": tip, "durum": "baglandi"})
                        print(f"🪰 [BEYİN]: {ssid} → güvenli, bağlanıldı")
                else:
                    print(f"⚠️  [BEYİN]: {ssid} → atlandı ({'şüpheli' if supheli else 'zayıf sinyal'})")

        return baglanan

    # -----------------------------------------------------------------------
    # Ana karar fonksiyonu
    # -----------------------------------------------------------------------

    def karar_ver(self, sensor_verisi: dict) -> dict:
        """
        Ham sensör verisini alır, karar üretir.

        Güvenlik kararları: duygu YOK — saf LLM/kural analizi.
        Sohbet kararları: duygu VAR — kisilik quantum_dusunce etkili.
        """
        pil = sensor_verisi.get("pil", -1)
        ag = sensor_verisi.get("ag", True)
        tehdit = sensor_verisi.get("tehdit", None)
        tur = sensor_verisi.get("tur", 0)

        # Durumu metne çevir
        parcalar = []
        if pil >= 0:
            parcalar.append(f"Pil %{pil}")
        parcalar.append("Ağ bağlı" if ag else "Ağ yok")
        if tehdit:
            parcalar.append(f"Tehdit: {tehdit}")
        if self.mod == "GUCLU_SINEK":
            parcalar.append("Mod: GÜÇLÜ SİNEK")
        durum_metni = ", ".join(parcalar) + "."

        # LLM/kural ile karar üret (DUYGU YOK — güvenlik analizi)
        karar = self.llm.dusun(durum_metni, sensor_verisi)

        # Karar tipini belirle
        eylem = karar.get("eylem", "NABIZ_AT")
        is_guvenlik = eylem in GUVENLIK_KARARLARI
        is_sohbet = eylem in SOHNET_KARARLARI

        # Sohbet/ton kararlarında kisilik etkisi
        if is_sohbet:
            quantum = self.kisilik.quantum_dusunce("sohbet", sensor_verisi)
            karar["quantum_egilim"] = quantum["egilim"]
            karar["quantum_duygu"] = quantum["baskın_duygu"]
            karar["konusma_kipi"] = quantum["konusma_kipi"]
        elif is_guvenlik:
            # Güvenlik kararında duygu yok — saf analiz
            karar["mod"] = "analiz"  # duygu katmanı kapalı

        # Güçlü sinek modunda ek eylemler
        if self.mod == "GUCLU_SINEK":
            if tehdit and "jammer" in str(tehdit).lower():
                # Jammer sinyali varsa sömür
                karar["eylem"] = "FREKANS_SURF"
                karar["karar"] = "Jammer sinyali sömürülüyor (GÜÇLÜ SİNEK)"
                karar["oncelik"] = 5
            elif not ag and pil > 15:
                # İnternet yok ama pil var — ağ tara
                karar["eylem"] = "AG_TARA"
                karar["karar"] = "Çevre taranıyor — hiçbir internet boş geçmez"
                karar["oncelik"] = 3

        # Karar geçmişine ekle
        self.karar_gecmisi.append({
            "tur": tur,
            "durum": durum_metni,
            "karar": karar,
            "mod": self.mod,
            "duygu_aktif": is_sohbet,
        })
        if len(self.karar_gecmisi) > 50:
            self.karar_gecmisi.pop(0)

        self._karar_isle(karar)
        return karar

    # -----------------------------------------------------------------------
    # Sohbet (duygu + kişilik etkili)
    # -----------------------------------------------------------------------

    def sohbet(self, mesaj: str) -> str:
        """Kullanıcı ile sohbet — duygu ve kişilik aktif."""
        # Kişilik durumunu context'e ekle
        quantum = self.kisilik.quantum_dusunce("sohbet")
        baglam = {
            "kisilik_asama": self.kisilik.asama,
            "baskin_duygu": quantum["baskın_duygu"],
            "tutum": quantum["tutum"],
            "konusma_kipi": quantum["konusma_kipi"],
            "mod": self.mod,
        }
        cevap = self.llm.sohbet(mesaj)
        # Cevabı kişiliğe göre zenginleştir
        if self.mod == "GUCLU_SINEK" and len(cevap) < 100:
            cevap += " 🔥"
        return cevap

    # -----------------------------------------------------------------------
    # Eski arayüzler (geriye dönük uyumlu)
    # -----------------------------------------------------------------------

    def trigger_1hz_mode(self, battery_level):
        """Pil kritikse 1Hz moda geç — GÜVENLİK kararı, duygu yok."""
        if battery_level < 20:
            self.state = "1HZ_LOW_POWER"
            karar = self.dusun(
                f"Pil seviyesi %{battery_level}, kritik eşiğin altında.",
                {"pil": battery_level, "mod": "1HZ"},
            )
            self._karar_isle(karar)
            return True
        self.state = "ACTIVE"
        return False

    def process_anomaly(self, anomaly_type):
        """Anomali işle — GÜVENLİK kararı, duygu yok."""
        self.anomaly_log.append(anomaly_type)
        karar = self.dusun(
            f"Anomali tespit edildi: {anomaly_type}",
            {"anomali": anomaly_type, "gecmis_sayisi": len(self.anomaly_log)},
        )
        eylem = karar.get("eylem", "EVENT_RECORDED")
        # Ama anomali iz olarak kazınır (duygu öyküsü ile)
        self.kisilik.iz_kazin(
            f"anomali_{anomaly_type}",
            f"Anomali: {anomaly_type}",
            duygu_oykusu=0.7,
        )
        self._karar_isle(karar)
        if anomaly_type == "HARDWARE_FAILURE":
            return "ENTER_SAFE_MODE"
        return eylem

    def dusun(self, durum: str, baglam: dict | None = None) -> dict:
        """LLM köprüsüne sor — GÜVENLİK analizi, duygu yok."""
        karar = self.llm.dusun(durum, baglam)
        return karar

    def son_karar(self) -> dict | None:
        return self.karar_gecmisi[-1] if self.karar_gecmisi else None

    # -----------------------------------------------------------------------
    # Yardımcı
    # -----------------------------------------------------------------------

    def _karar_isle(self, karar: dict):
        """Yüksek öncelikli kararları vurgula."""
        if karar.get("oncelik", 0) >= ACIL_ESIK:
            duygu_etiketi = ""
            if karar.get("duygu_aktif"):
                duygu_etiketi = f" [{self.kisilik.baskın_duygu()}]"
            print(f"🚨 [ACİL KARAR]{duygu_etiketi}: {karar.get('karar')} → {karar.get('eylem')}")
        self.state = karar.get("eylem", self.state)

    def durum_ozeti(self) -> dict:
        return {
            "mod": self.mod,
            "state": self.state,
            "llm_mod": self.llm.mod,
            "kisilik": self.kisilik.durum_ozeti(),
            "karar_sayisi": len(self.karar_gecmisi),
            "jammer_sinyali": self.jammer_sinyali,
            "surf_performans": self.surf_performans,
            "baglanan_aglar": list(self.baglanan_aglar),
        }


if __name__ == "__main__":
    print("=== FlyBrain Test ===\n")
    brain = FlyBrain()

    print("\n--- TEST 1: Normal mod, düşük pil ---")
    brain.trigger_1hz_mode(12)

    print("\n--- TEST 2: Normal mod, jammer ---")
    brain.jammer_yakala("2.4GHz", -55)

    print("\n--- TEST 3: Güçlü sinek moduna geç ---")
    brain.mod_degistir("GUCLU_SINEK")
    brain.jammer_yakala("2.4GHz", -55)

    print("\n--- TEST 4: Ağ tarama (güçlü sinek) ---")
    aglar = [
        {"ssid": "EvWiFi", "guc": -60, "tip": "WPA2"},
        {"ssid": "DEAUTH_AP", "guc": -55, "tip": "DeAuth saldırısı"},
        {"ssid": "KafeNet", "guc": -70, "tip": "open"},
    ]
    baglanan = brain.ag_tara_ve_baglan(aglar)
    print(f"Bağlanılan: {len(baglanan)} ağ")

    print("\n--- TEST 5: Sohbet (duygu aktif) ---")
    print(brain.sohbet("Selam sinek nasılsın"))

    print(f"\n--- ÖZET ---")
    print(json.dumps(brain.durum_ozeti(), ensure_ascii=False, indent=2))
