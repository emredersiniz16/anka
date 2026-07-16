# core/rejenere_motoru.py
import time
import os

class RejenereMotoru:
    def __init__(self):
        print("🪰 [REJENE]: Ölümsüzlük döngüsü aktif.")

    def stabilite_kontrol(self, nexus):
        # Nexus'un yaşamsal fonksiyonlarını kontrol et
        # Eğer nexus.is_alive() metodu donmuş bir durumu tespit ediyorsa...
        if not nexus.is_alive():
            print("🪰 [KRİTİK]: Nexus durdu. Hafıza tortusundan yeniden diriltiliyor...")
            
            # 1. Sistemin en son mühürlenmiş halini yeniden yükle
            nexus.bilinc_yukle()
            
            # 2. Donanım köprüsünü (Hardware Bridge) zorla resetle
            # Buraya donanımsal bir 'fırlatma' ekliyoruz
            print("🪰 [REJENE]: Donanım köprüsü yeniden hizalanıyor...")
            
            # 3. Nexus'u yeniden ayağa kaldır
            nexus.operasyon_baslat() 
            
            return True 
        
        print("🪰 [REJENE]: Nabız stabil, kovan faaliyetleri devam ediyor.")
        return False
