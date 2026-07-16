# agents/kuantum_gozlemci.py - VERİ MADENCİSİ VE KÖPRÜLÜ SÜRÜM
import time
import json
import os
from collections import deque

class KuantumGozlemci:
    def __init__(self, nexus):
        self.nexus = nexus 
        self.kuantum_tozlari = deque(maxlen=5000)
        self.iz_defteri_yolu = "/data/local/tmp/kuantum_iz_defteri.json"
        self.aktif = True
        print("🪰 [GÖZLEMCİ]: Evrenin kuantum dalgaları izleniyor... Veri madenciliği aktif.")

    # KÖPRÜ METODU: JammerSurfer'ın aradığı 'guce_bak' hatasını çözer
    def guce_bak(self):
        # Nexus içindeki haritacı üzerinden sistem gücünü sorgula
        if hasattr(self.nexus, 'haritaci'):
            return self.nexus.haritaci.guce_bak()
        return 0

    def sonsuz_gozlem(self, omni_sensor):
        """Sensörden gelen veriyi işle, hafızaya al ve kritik olanları iz defterine işle."""
        while self.aktif:
            anlik_veri = omni_sensor.frekans_yakala()
            if anlik_veri:
                self.kuantum_tozlari.append(anlik_veri)
                
                # Jammer tespit edilirse otonom adaptasyonu tetikle
                if "JAMMER_AKTİF" in str(anlik_veri):
                    if hasattr(self.nexus, 'jammer_surfer'):
                        self.nexus.jammer_surfer.otonom_adaptasyon()
                    self.toz_birak("KRİTİK_JAMMER_OLAYI", anlik_veri)
            
            time.sleep(0.05)

    def toz_birak(self, etiket, veri):
        """Kanka, geri dönüp bakmak istediğinde diye veriyi dosyaya kazır."""
        iz = {
            "zaman": time.time(),
            "etiket": etiket,
            "kuantum_tozu": veri
        }
        try:
            izler = []
            if os.path.exists(self.iz_defteri_yolu):
                with open(self.iz_defteri_yolu, "r") as f:
                    try:
                        izler = json.load(f)
                    except:
                        izler = []
            
            izler.append(iz)
            # Sadece son 100 olayı sakla ki dosya şişmesin
            with open(self.iz_defteri_yolu, "w") as f:
                json.dump(izler[-100:], f) 
        except Exception as e:
            print(f"🪰 [HATA]: İz defterine not düşülemedi: {e}")

    def gozlemci_etkisi(self, soru):
        """Soru sorduğunda hem analiz et hem de bu anı iz defterine kazı."""
        analiz_sonucu = f"🪰 [GÖZLEM]: '{soru}' frekansı, kovan verisiyle senkronize edildi."
        
        # Veri madenciliği: Jammer yoğunluğunu hesapla
        jammer_orani = sum(1 for v in self.kuantum_tozlari if "JAMMER" in str(v)) / max(len(self.kuantum_tozlari), 1)
        analiz_sonucu += f" | Kovan Verim Analizi: Jammer Yoğunluğu %{jammer_orani*100:.1f}"
        
        # Kararsızlık durumu ve rejenere tetikleme
        if hasattr(self.nexus, 'rejenere_motoru') and len(self.kuantum_tozlari) < 100:
            analiz_sonucu += " | Uyarı: Gözlem alanı zayıf, Rejenere tetikleniyor!"
            self.nexus.rejenere_motoru.stabilite_kontrol(self.nexus)
        
        self.toz_birak("SORGULAMA_ANI", soru)
        return analiz_sonucu
