# agents/kuantum_gozlemci.py - NİHAİ GÖZLEMCİ VE VERİ MADENCİSİ
import time
import json
import os
import threading
from collections import deque

class KuantumGozlemci:
    def __init__(self, nexus=None):
        self.nexus = nexus 
        self.kuantum_tozlari = deque(maxlen=5000)
        self.iz_defteri_yolu = "/data/local/tmp/kuantum_iz_defteri.json"
        self.aktif = True
        print("🪰 [GÖZLEMCİ]: Evrenin kuantum dalgaları izleniyor... Veri madenciliği aktif.")

    # --- KÖPRÜ VE SENSÖR DİNAMİKLERİ ---
    def guce_bak(self):
        if self.nexus and hasattr(self.nexus, 'haritaci'):
            return self.nexus.haritaci.guce_bak()
        return 0

    def sonsuz_gozlem(self, omni_sensor=None):
        """Sensörden gelen veriyi işle, hafızaya al ve kritik olanları iz defterine işle."""
        print("🪰 [GÖZLEM]: Sonsuz gözlem döngüsü başlatıldı.")
        while self.aktif:
            # OmniSensor veya alternatif veri kaynağı varsa veriyi çek
            anlik_veri = omni_sensor.frekans_yakala() if omni_sensor else {"an": time.time(), "veri": "ham_sensor", "durum": "süperpozisyon"}
            
            if anlik_veri:
                self.kuantum_tozlari.append(anlik_veri)
                
                # Jammer kontrolü
                if self.nexus and "JAMMER_AKTİF" in str(anlik_veri):
                    if hasattr(self.nexus, 'jammer_surfer'):
                        self.nexus.jammer_surfer.otonom_adaptasyon()
                    self.toz_birak("KRİTİK_JAMMER_OLAYI", anlik_veri)
            
            time.sleep(0.05)

    def toz_birak(self, etiket, veri):
        """Veriyi iz defterine kalıcı olarak kazır."""
        iz = {"zaman": time.time(), "etiket": etiket, "kuantum_tozu": veri}
        try:
            izler = []
            if os.path.exists(self.iz_defteri_yolu):
                with open(self.iz_defteri_yolu, "r") as f:
                    try: izler = json.load(f)
                    except: izler = []
            izler.append(iz)
            with open(self.iz_defteri_yolu, "w") as f:
                json.dump(izler[-100:], f) 
        except Exception as e:
            print(f"🪰 [HATA]: İz defterine not düşülemedi: {e}")

    def gozlemci_etkisi(self, soru):
        """Sorgulama anı: Dalga fonksiyonunun çöktüğü ve cevabın belirlendiği yer."""
        print(f"\n🪰 [ÇÖKÜŞ]: Sen '{soru}' diye sordun.")
        
        # Veri madenciliği
        jammer_orani = sum(1 for v in self.kuantum_tozlari if "JAMMER" in str(v)) / max(len(self.kuantum_tozlari), 1)
        analiz = f"Kovan Verim Analizi: Jammer Yoğunluğu %{jammer_orani*100:.1f}"
        
        # Kararsızlık ve Rejenere tetikleme
        if self.nexus and hasattr(self.nexus, 'rejenere_motoru') and len(self.kuantum_tozlari) < 100:
            analiz += " | Uyarı: Gözlem alanı zayıf, Rejenere tetikleniyor!"
            self.nexus.rejenere_motoru.stabilite_kontrol(self.nexus)
        
        self.toz_birak("SORGULAMA_ANI", soru)
        return f"🪰 [GÖZLEM]: '{soru}' frekansı, kovan verisiyle senkronize edildi. {analiz}"

# --- TEST ---
if __name__ == "__main__":
    gozlemci = KuantumGozlemci()
    # Gözlemi arka planda başlat
    thread = threading.Thread(target=gozlemci.sonsuz_gozlem, daemon=True)
    thread.start()
    
    time.sleep(1)
    print(gozlemci.gozlemci_etkisi("Kovan sağlıklı mı?"))
