# agents/kisilik_motoru.py - SİNEK KİŞİLİK MOTORU
# 🪰 Sinek'in alışkanlık reflekslerini kazıdığı derin katman.
# sinek_bilinc.py bu modülü import eder — agents/ dizininde olmalı.
#
# Vizyon: Sinek "düşünmez, refleks gösterir."
# Kullanıcının alışkanlıkları kısa kodlara mühürlenir,
# bir sonraki seferde otomatik tepki verilir.

class KisilikMotoru:
    def __init__(self):
        self.refleksler = {}
        print("🪰 [KİŞİLİK]: Refleks motoru hazır. Alışkanlıklar kazınıyor...")

    def refleks_kazin(self, durum, refleks):
        """
        Kanka, senin alışkanlıklarını Sinek'in derinlerine (Kısa Kodlara) 
        birer refleks olarak mühürlüyoruz.
        """
        self.refleksler[durum] = refleks
        print(f"🪰 [MÜHÜR]: '{durum}' durumunda Sinek artık otomatik olarak '{refleks}' tepkisi verecek.")

    def refleks_tetikle(self, durum):
        """Sinek düşünmez, Sinek refleks gösterir."""
        if durum in self.refleksler:
            return self.refleksler[durum]
        return None

