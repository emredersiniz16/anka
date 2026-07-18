# agents/fly_brain.py
# Anka OS - Otonom Karar Mekanizması ve Evrim Motoru
# GÜNCELLEME: LLMBridge entegre edildi — fly_brain artık gerçekten "düşünüyor".

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_bridge import LLMBridge

# Öncelik eşiği: >= bu değer ise acil eylem log'a işlenir
ACIL_ESIK = 4


class FlyBrain:
    def __init__(self):
        self.state = "DORMANT"
        self.anomaly_log = []
        self.karar_gecmisi = []        # Son N kararı sakla
        self.llm = LLMBridge()         # Düşünce motoru
        print("[SİNEK BİLİNCİ] Zihin yükleniyor... Click evreni aktif.")
        print(f"[SİNEK BİLİNCİ] LLM modu: {self.llm.mod}")

    # -----------------------------------------------------------------------
    # Mevcut arayüzler (geriye dönük uyumluluk korundu)
    # -----------------------------------------------------------------------

    def trigger_1hz_mode(self, battery_level):
        """
        LTPO/LCD ekranlar için 1 Hz otonom sinek rotası hesaplar.
        Pil seviyesine göre düşük güç moduna geçer.
        """
        if battery_level < 20:
            self.state = "1HZ_LOW_POWER"
            print(f"[SİNEK BİLİNCİ] Kritik pil: {battery_level}%. 1 Hz moda geçiliyor.")
            # LLM'e de sor — acil durum kararını al
            karar = self.dusun(
                f"Pil seviyesi %{battery_level}, kritik eşiğin altında.",
                {"pil": battery_level, "mod": "1HZ"}
            )
            self._karar_isle(karar)
            return True
        self.state = "ACTIVE"
        return False

    def process_anomaly(self, anomaly_type):
        """
        Sistemdeki olağandışı olayları işler ve LLM ile karar üretir.
        """
        self.anomaly_log.append(anomaly_type)

        karar = self.dusun(
            f"Anomali tespit edildi: {anomaly_type}",
            {"anomali": anomaly_type, "gecmis_sayisi": len(self.anomaly_log)}
        )

        eylem = karar.get("eylem", "EVENT_RECORDED")
        print(f"[SİNEK BİLİNCİ] Anomali → {anomaly_type} | Karar → {eylem}")

        self._karar_isle(karar)

        # Eski arayüzle uyumluluk: kritik anomalilerde sabit dönüş
        if anomaly_type == "HARDWARE_FAILURE":
            return "ENTER_SAFE_MODE"
        return eylem

    # -----------------------------------------------------------------------
    # Yeni: gerçek düşünme katmanı
    # -----------------------------------------------------------------------

    def dusun(self, durum: str, baglam: dict | None = None) -> dict:
        """
        Verilen durumu LLM köprüsüne gönderir, JSON kararı döndürür.

        Args:
            durum:   İnsan dilinde durum tanımı
            baglam:  Sensör/sistem verisi (opsiyonel)

        Returns:
            {"karar": str, "eylem": str, "oncelik": int, "kaynak": str}
        """
        karar = self.llm.dusun(durum, baglam)
        self.karar_gecmisi.append({"durum": durum, "karar": karar})
        # Hafızayı sınırla (son 50 karar)
        if len(self.karar_gecmisi) > 50:
            self.karar_gecmisi.pop(0)
        return karar

    def karar_ver(self, sensor_verisi: dict) -> dict:
        """
        Ham sensör verisini alır, durumu metne dönüştürür ve LLM'e sorar.
        sinek_nexus.py'nin operasyon döngüsünden çağrılır.

        Args:
            sensor_verisi: {"pil": int, "ag": bool, "tehdit": str|None, ...}

        Returns:
            {"karar": str, "eylem": str, "oncelik": int, "kaynak": str}
        """
        pil   = sensor_verisi.get("pil",    -1)
        ag    = sensor_verisi.get("ag",     True)
        tehdit = sensor_verisi.get("tehdit", None)

        # Durumu insan diline çevir
        parcalar = []
        if pil >= 0:
            parcalar.append(f"Pil %{pil}")
        parcalar.append("Ağ bağlı" if ag else "Ağ yok")
        if tehdit:
            parcalar.append(f"Tehdit: {tehdit}")

        durum_metni = ", ".join(parcalar) + "."

        return self.dusun(durum_metni, sensor_verisi)

    def son_karar(self) -> dict | None:
        """En son verilen kararı döndürür."""
        return self.karar_gecmisi[-1] if self.karar_gecmisi else None

    # -----------------------------------------------------------------------
    # Yardımcı
    # -----------------------------------------------------------------------

    def _karar_isle(self, karar: dict):
        """Yüksek öncelikli kararları konsola vurgula."""
        if karar.get("oncelik", 0) >= ACIL_ESIK:
            print(f"🚨 [ACİL KARAR]: {karar.get('karar')} → Eylem: {karar.get('eylem')}")
        self.state = karar.get("eylem", self.state)


if __name__ == "__main__":
    brain = FlyBrain()
    print("\n--- Senaryo 1: Düşük pil ---")
    brain.trigger_1hz_mode(12)

    print("\n--- Senaryo 2: Anomali ---")
    brain.process_anomaly("HARDWARE_FAILURE")

    print("\n--- Senaryo 3: Sensör döngüsü ---")
    print(brain.karar_ver({"pil": 45, "ag": True, "tehdit": "DeAuth"}))

