# agents/fly_brain.py
# Anka OS - Otonom Karar Mekanizması ve Evrim Motoru

class FlyBrain:
    def __init__(self):
        self.state = "DORMANT"
        self.anomaly_log = []
        print("[SİNEK BİLİNCİ] Zihin yükleniyor... Click evreni aktif.")

    def trigger_1hz_mode(self, battery_level):
        """
        LTPO ve LCD ekranlar için 1 Hz otonom sinek rotası hesaplar.
        Pil seviyesine göre düşük güç moduna geçer.
        """
        if battery_level < 20:
            self.state = "1HZ_LOW_POWER"
            print(f"[SİNEK BİLİNCİ] Kritik pil: {battery_level}%. 1 Hz moda geçiliyor.")
            return True # 1Hz Mod Aktif
        
        self.state = "ACTIVE"
        return False # Normal Mod

    def process_anomaly(self, anomaly_type):
        """
        Sistemdeki garip olayları (Click sesleri, donanımsal aksamalar) işler.
        """
        self.anomaly_log.append(anomaly_type)
        print(f"[SİNEK BİLİNCİ] Anomali işlendi: {anomaly_type}. Kayıt tamam.")
        
        # Anomali tipine göre özel karar mekanizması
        if anomaly_type == "CLICK":
            return "LOG_CLICK_EVENT"
        elif anomaly_type == "HARDWARE_FAILURE":
            return "ENTER_SAFE_MODE"
            
        return "EVENT_RECORDED"

if __name__ == "__main__":
    brain = FlyBrain()
