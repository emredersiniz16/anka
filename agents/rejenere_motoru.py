# agents/rejenere_motoru.py - ÖLÜMSÜZLÜK VE İYİLEŞTİRME MOTORU
import time
import os

class RejenereMotoru:
    def __init__(self):
        print("🪰 [REJENE]: Ölümsüzlük döngüsü aktif.")

    def stabilite_kontrol(self, nexus):
        """
        Nexus'un yaşamsal fonksiyonlarını kontrol et.
        Eğer bir duraksama tespit edilirse, sistemi güvenli modda yeniden başlat.
        """
        # Sinek'in nabzını kontrol et
        if not nexus.is_alive():
            print("🪰 [KRİTİK]: Nexus durdu. Hafıza tortusundan yeniden diriltiliyor...")
            
            # 1. Sistemin en son mühürlenmiş halini yeniden yükle
            # Hafızadaki kristalden (bilinç) verileri geri getir
            nexus.bilinc_yukle()
            
            # 2. Donanım köprüsünü (Hardware Bridge) yeniden hizala
            print("🪰 [REJENE]: Donanım köprüsü yeniden hizalanıyor...")
            
            # 3. Nexus'u yeniden ayağa kaldır
            # Not: Bu çağrı sistemin yeniden başlatılmasını sağlar
            nexus.operasyon_baslat() 
            
            return True 
        
        # Eğer nabız normalse, hiçbir şeye dokunma
        print("🪰 [REJENE]: Nabız stabil, kovan faaliyetleri devam ediyor.")
        return False
