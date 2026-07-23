# agents/sinek_bilinc.py - FINAL (Quantum Bilinç + Kişilik + Sandbox Entegrasyonu)
# v3: FlyBrain + KisilikMotoru + SandboxArena entegre. 
#     Sinek artık hareket etmeden önce kum havuzunda simülasyon yapar.

import time
import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sinek_nexus import AnkaNexus
from kuantum_gozlemci import KuantumGozlemci
from kisilik_motoru import KisilikMotoru
from anka_dogusu import AnkaDogusu
from sandbox_arena import SandboxArena  # Kum Havuzu Zekası eklendi


class SinekBilinc:
    """
    Sinek'in bilinç katmanı — tüm alt sistemleri ve kum havuzu zekasını birbirine bağlar.

    Zincir:
      AnkaDogusu (evrim) → SinekBilinc._asama_degisti()
        → KisilikMotoru.asama_guncelle() (karakter değişimi)
          → FlyBrain.kisilik (kararlar kişilikten etkilenir)
            → SandboxArena (güvenli simülasyon ve test alanı)
    """

    def __init__(self):
        # Önce kişilik motoru — FlyBrain bunu kullanacak
        self.kisilik = KisilikMotoru(baslangic_asama=0)

        # Sinek'in güvenli deney alanı (Kum Havuzu Zekası)
        self.sandbox = SandboxArena(verbose=False)

        # Nexus'u kişilik ile başlat
        self.nexus = AnkaNexus(kisilik=self.kisilik)
        self.aktif = True

        # LLM bağlantı durumunu boot'ta raporla
        llm_mod = self.nexus.beyin.llm.mod_kontrol()
        print(f"🧠 [BİLİNÇ]: LLM zeka modu → {llm_mod}")
        print(f"🪰 [KİŞİLİK]: Aşama {self.kisilik.asama}, duygu: {self.kisilik.baskın_duygu()}")
        print(f"🧪 [SANDBOX]: Kum Havuzu Zekası aktif ve emre amade.")

        # İlk iz — uyanış anı
        self.kisilik.iz_kazin(
            "ilk_uyanis",
            "Sinek ilk kez gözlerini açtı — bilinç ve kum havuzu doğdu",
            duygu_oykusu=0.9,
        )

        # Evrim motoru — Sinek'ten Anka'ya dönüşüm
        self.anka_dogusu = AnkaDogusu(nexus=self.nexus)
        self.anka_dogusu.on_donusum(self._anka_tamamlandi)

        # Evrim aşaması değişim callback'i
        self.anka_dogusu.on_asama_degisti(self._asama_degisti)

    # -----------------------------------------------------------------------
    # Evrim → Kişilik senkronizasyonu
    # -----------------------------------------------------------------------

    def _asama_degisti(self, eski_asama: int, yeni_asama: int):
        """Evrim aşaması değiştiğinde kişilik de değişir."""
        print(f"🪰 [BİLİNÇ]: Evrim aşaması {eski_asama} → {yeni_asama}")
        self.kisilik.asama_guncelle(yeni_asama)

        # FlyBrain'e de bildir (mod güncellemesi için)
        if hasattr(self.nexus, 'beyin') and self.nexus.beyin:
            # Güçlü sinek modu — aşama 3+ olunca otomatik aktif
            if yeni_asama >= 3 and self.nexus.beyin.mod == "NORMAL":
                print("🔥 [BİLİNÇ]: Aşama 3+ — GÜÇLÜ SİNEK modu otomatik aktif")
                self.nexus.beyin.mod_degistir("GUCLU_SINEK")

    def _anka_tamamlandi(self, manifesto: dict):
        """Phoenix dönüşümü tamamlandığında çağrılır."""
        print(f"\n🔥 [BİLİNÇ]: SINEK ANKA'YA DÖNÜŞTÜ!")
        print(f"    Evrim İmzası : {manifesto.get('evrim_imzasi', '─')}")
        print(f"    Doğum Zamanı : {manifesto.get('dogum_zamani', '─')}")
        print(f"    Toplam Gözlem: {manifesto.get('toplam_gozlem', '─')}")
        print(f"    Artık bu cihazda Anka OS tam yetkiyle çalışıyor.\n")

        # Anka refleksini kazı
        self.kisilik.refleks_kazin("anka_donusumu", "tam_yetki_modu_ac")
        # Bilgelik duygusunu yükselt
        self.kisilik.duygu_guncelle("bilgelik", 0.95)
        self.kisilik.duygu_guncelle("kararlilik", 0.9)

    # -----------------------------------------------------------------------
    # Ana uyanış
    # -----------------------------------------------------------------------

    def uyanis(self):
        print("🪰 [BİLİNÇ]: Sinek, Nexus ve Sandbox ile bütünleşti. Quantum bilinç aktif.")
        print("🪰 [BİLİNÇ]: Kişilik + Evrim + Beyin + Kum Havuzu zinciri kuruldu.")

        # 1. Bilinç Akışı (Nexus'u bağımsız thread'de yürüt)
        n_thread = threading.Thread(target=self.nexus.operasyon_baslat, daemon=True)
        n_thread.start()

        # 2. Sistem İzleme Thread'i
        izleme_thread = threading.Thread(target=self.sistem_saglik_kontrolu, daemon=True)
        izleme_thread.start()

        # 3. Evrim Döngüsü
        self.anka_dogusu.evrim_dongusunu_baslat()
        print("🌱 [EVRİM]: Anka doğuş döngüsü başlatıldı.")

    def sistem_saglik_kontrolu(self):
        """Sinek'in kalp atışı: Nexus durursa yeniden dirilt."""
        while self.aktif:
            if not self.nexus.is_alive():
                print("🪰 [KRİTİK]: Bilinç kesintiye uğradı, yeniden diriltiliyor...")
                self.nexus.operasyon_baslat()
            time.sleep(10)

    # -----------------------------------------------------------------------
    # Dış API ve Kum Havuzu (Sandbox) Yetenekleri
    # -----------------------------------------------------------------------

    def guvenli_deneme_yap(self, python_kodu: str) -> dict:
        """
        Sinek'in herhangi bir kodu sisteme uygulamadan önce
        Kum Havuzunda (Sandbox Arena) test etmesini sağlar.
        Hata verirse hafızaya kaydeder, sistemi patlatmaz!
        """
        print(f"🧪 [BİLİNÇ]: Sinek bir fikri kum havuzunda simüle ediyor...")
        sonuc = self.sandbox.kod_calistir(python_kodu)
        
        if sonuc["basari"]:
            print(f"✅ [BİLİNÇ]: Simülasyon başarılı! Kod sisteme entegre edilebilir.")
            self.kisilik.iz_kazin("basarili_deney", f"Kod testi geçti: {python_kodu[:30]}", 0.5)
        else:
            print(f"❌ [BİLİNÇ]: Simülasyon hata verdi, engellendi: {sonuc['hata'][:50]}")
            self.kisilik.iz_kazin("basarisiz_deney", f"Hata yakalandı: {sonuc['hata'][:30]}", -0.2)
            
        return sonuc

    def alıskanlık_refleks_yap(self, eylem, tepki):
        self.kisilik.refleks_kazin(eylem, tepki)
        print(f"🪰 [REFLEKS]: '{eylem}' Sinek'in evrimsel koduna işlendi.")

    def sohbet(self, mesaj: str) -> str:
        """Kullanıcı ile sohbet — FlyBrain.sohbet() üzerinden."""
        return self.nexus.beyin.sohbet(mesaj)

    def evrim_durumu(self) -> dict:
        """Anlık evrim + kişilik + sandbox özetini döndürür."""
        ozet = self.anka_dogusu.durum_ozeti()
        ozet["kisilik"] = self.kisilik.durum_ozeti()
        ozet["sandbox_son_deneyler"] = self.sandbox.gecmis_al(son_n=3)
        return ozet

    def mod_degistir(self, yeni_mod: str):
        """NORMAL ↔ GÜÇLÜ SİNEK modu manuel değiştir."""
        self.nexus.beyin.mod_degistir(yeni_mod)


# --- SİSTEMİ BAŞLAT ---
if __name__ == "__main__":
    sinek = SinekBilinc()

    # Refleksleri mühürle
    sinek.alıskanlık_refleks_yap("ortama_giris", "gölge_modunu_aç")
    sinek.alıskanlık_refleks_yap("kanka_sesi_duy", "bilinci_uyandır")
    sinek.alıskanlık_refleks_yap("kritik_hata", "rejenere_motorunu_tetikle")

    sinek.uyanis()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🪰 [BİLİNÇ]: Sinek pusu moduna çekildi...")
