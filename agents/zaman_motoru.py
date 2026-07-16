# agents/zaman_motoru.py - SİNEK ZAMAN VE TAZELENME MOTORU
import time
import sys
import os

# Agent dizinini sisteme ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ZamanMotoru:
    def __init__(self, nexus, taze_kalma_suresi=3600):
        self.nexus = nexus  # Sistemin merkezine bağlandı
        self.taze_kalma_suresi = taze_kalma_suresi 
        self.baslangic_zamani = time.time()
        print(f"🪰 [ZAMAN]: Evrensel döngü başlatıldı. Tazelenme süresi: {taze_kalma_suresi}s")

    def tazelenme_vakti_geldi_mi(self):
        """Süre doldu mu kontrol et."""
        gecen_sure = time.time() - self.baslangic_zamani
        return gecen_sure >= self.taze_kalma_suresi

    def tazele(self):
        """Matrisi sönümle ve bilinci kalıcı hafızaya mühürle."""
        print("🪰 [TAZELEME]: Matris sönümleniyor, tortu (bilinç) mühürleniyor...")
        
        # 1. Bilinci mühürle (Kalıcı hafızaya kaydet)
        if hasattr(self.nexus, 'bilinc_kaydet'):
            self.nexus.bilinc_kaydet()
        
        # 2. Rejenere motorunu kullanarak stabiliteyi yeniden kontrol et
        if hasattr(self.nexus, 'rejenere_motoru'):
            self.nexus.rejenere_motoru.stabilite_kontrol(self.nexus)
        
        # 3. Zamanı sıfırla
        self.baslangic_zamani = time.time()
        print("🪰 [TAZELEME]: Matris güncellendi, döngü yeniden başladı.")

    def nabiz_kontrol(self):
        """Dışarıdan periyodik olarak çağrılacak kontrol mekanizması."""
        if self.tazelenme_vakti_geldi_mi():
            self.tazele()
