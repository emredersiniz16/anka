# agents/sinek_bilinc.py - FINAL (Sinek Uyanış → Anka Doğuşu)
import time
import threading
import os
import sys

# Agent dizinini sisteme ekle ki importlar kusursuz çalışsın
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sinek_nexus import AnkaNexus 
from kuantum_gozlemci import KuantumGozlemci
from kisilik_motoru import KisilikMotoru
from anka_dogusu import AnkaDogusu

class SinekBilinc:
    def __init__(self):
        self.nexus = AnkaNexus()
        self.kisilik = KisilikMotoru()
        self.aktif = True
        # LLM bağlantı durumunu boot'ta raporla
        llm_mod = self.nexus.beyin.llm.mod_kontrol()
        print(f"🧠 [BİLİNÇ]: LLM zeka modu → {llm_mod}")

        # Evrim motoru — Sinek'ten Anka'ya dönüşüm
        self.anka_dogusu = AnkaDogusu(nexus=self.nexus)
        self.anka_dogusu.on_donusum(self._anka_tamamlandi)

    def uyanis(self):
        print("🪰 [BİLİNÇ]: Sinek, Sinek Nexus ile bütünleşti. Sınırlar yok.")
        
        # 1. Bilinç Akışı (Nexus'u bağımsız thread'de yürüt)
        n_thread = threading.Thread(target=self.nexus.operasyon_baslat, daemon=True)
        n_thread.start()
        
        # 2. Sistem İzleme Thread'i (Kendi kendini koruma)
        izleme_thread = threading.Thread(target=self.sistem_saglik_kontrolu, daemon=True)
        izleme_thread.start()

        # 3. Evrim Döngüsü — Sinek → Anka kuantum çöküşü
        self.anka_dogusu.evrim_dongusunu_baslat()
        print("🌱 [EVRİM]: Anka doğuş döngüsü başlatıldı.")

    def sistem_saglik_kontrolu(self):
        """Sinek'in kalp atışı: Nexus durursa veya donarsa onu yeniden dirilt."""
        while self.aktif:
            if not self.nexus.is_alive():
                print("🪰 [KRİTİK]: Bilinç kesintiye uğradı, yeniden diriltiliyor...")
                self.nexus.operasyon_baslat()
            time.sleep(10) # 10 saniyede bir nabız kontrolü

    def _anka_tamamlandi(self, manifesto: dict):
        """Phoenix dönüşümü tamamlandığında çağrılır."""
        print(f"\n🔥 [BİLİNÇ]: SINEK ANKA'YA DÖNÜŞTÜ!")
        print(f"    Evrim İmzası : {manifesto.get('evrim_imzasi', '─')}")
        print(f"    Doğum Zamanı : {manifesto.get('dogum_zamani', '─')}")
        print(f"    Toplam Gözlem: {manifesto.get('toplam_gozlem', '─')}")
        print(f"    Artık bu cihazda Anka OS tam yetkiyle çalışıyor.\n")
        # Anka refleksini de kaydet
        self.kisilik.refleks_kazin("anka_donusumu", "tam_yetki_modu_ac")

    def alıskanlık_refleks_yap(self, eylem, tepki):
        self.kisilik.refleks_kazin(eylem, tepki)
        print(f"🪰 [REFLEKS]: '{eylem}' Sinek'in evrimsel koduna işlendi.")

    def evrim_durumu(self) -> dict:
        """Anlık evrim özetini döndürür."""
        return self.anka_dogusu.durum_ozeti()

# --- SİSTEMİ BAŞLAT ---
if __name__ == "__main__":
    sinek = SinekBilinc()
    
    # Refleksleri mühürle
    sinek.alıskanlık_refleks_yap("ortama_giris", "gölge_modunu_aç")
    sinek.alıskanlık_refleks_yap("kanka_sesi_duy", "bilinci_uyandır")
    sinek.alıskanlık_refleks_yap("kritik_hata", "rejenere_motorunu_tetikle") 
    
    sinek.uyanis()
    
    # Sinek, kovanın içinde sonsuza kadar 'Bilinçli' yaşıyor
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🪰 [BİLİNÇ]: Sinek pusu moduna çekildi...")

