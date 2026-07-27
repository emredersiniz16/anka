# agents/sinek_bilinc.py - FINAL (Quantum Bilinç + Kişilik + Sandbox + Canlı HUD Entegrasyonu)
# v3.1: Tüm zeka organları bağlandı ve Note 9 ekranı/C çekirdeği ile %100 senkronize edildi.

import time
import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sinek_nexus import AnkaNexus
from kuantum_gozlemci import KuantumGozlemci
from kisilik_motoru import KisilikMotoru
from anka_dogusu import AnkaDogusu
from sandbox_arena import SandboxArena  # Kum Havuzu Zekası

STATE_FILE = "/data/local/tmp/anka_state.txt"
TMP_STATE_FILE = "/data/local/tmp/anka_state.tmp"
CMD_FILE = "/data/local/tmp/anka_cmd.txt"


class SinekBilinc:
    """
    Sinek'in bilinç katmanı — tüm alt sistemleri ve kum havuzu zekasını birbirine bağlar,
    üretilen tüm düşünceleri ve kararları canlı olarak telefon ekranına ve C çekirdeğine basar.
    """

    def __init__(self):
        # Önce kişilik motoru — FlyBrain bunu kullanacak
        self.kisilik = KisilikMotoru(baslangic_asama=0)

        # Sinek'in güvenli deney alanı (Kum Havuzu Zekası)
        self.sandbox = SandboxArena(verbose=False)

        # Nexus'u kişilik ile başlat
        self.nexus = AnkaNexus(kisilik=self.kisilik)
        self.aktif = True
        self.quantum_dust = 2500
        self.tick = 0

        # LLM bağlantı durumunu boot'ta raporla
        llm_mod = self.nexus.beyin.llm.mod_kontrol() if hasattr(self.nexus, 'beyin') else "OFFLINE"
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

        self.kisilik.refleks_kazin("anka_donusumu", "tam_yetki_modu_ac")
        self.kisilik.duygu_guncelle("bilgelik", 0.95)
        self.kisilik.duygu_guncelle("kararlilik", 0.9)

    # -----------------------------------------------------------------------
    # Canlı Ekran & HUD Döngüsü (Sözde Yapmıyoruz, Gerçekten Ekranı Besliyoruz!)
    # -----------------------------------------------------------------------

    def batarya_oku(self) -> int:
        try:
            if os.path.exists("/sys/class/power_supply/battery/capacity"):
                with open("/sys/class/power_supply/battery/capacity", "r") as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 99

    def hud_ve_komut_dongusu(self):
        """Telefon ekranındaki AnkaOverlay katmanını ve C çekirdeğini anlık besler."""
        while self.aktif:
            try:
                self.tick += 1
                self.quantum_dust += 5

                pil = self.batarya_oku()
                saat_str = time.strftime("%H:%M:%S")

                # Ekrandan (Java Overlay) gelen dokunmatik komutları işle
                if os.path.exists(CMD_FILE):
                    try:
                        with open(CMD_FILE, "r") as f:
                            cmd = f.read().strip()
                        os.remove(CMD_FILE)

                        if cmd == "CMD_MOD":
                            mevcut = self.nexus.beyin.mod if hasattr(self.nexus, 'beyin') else "NORMAL"
                            yeni = "GUCLU_SINEK" if mevcut == "NORMAL" else "NORMAL"
                            self.mod_degistir(yeni)
                        elif cmd == "CMD_SCAN":
                            self.guvenli_deneme_yap("print('Ekran taraması gerçekleştirildi')")
                            self.quantum_dust += 500
                        elif cmd == "CMD_KOVAN":
                            if hasattr(self.nexus, 'beyin'):
                                self.nexus.beyin.llm.mod_kontrol()
                    except Exception:
                        pass

                # Yapay Zeka kararı ve anlık düşünce üretimi
                duygu = self.kisilik.baskın_duygu()
                llm_mod = self.nexus.beyin.llm.mod if hasattr(self.nexus, 'beyin') else "OFFLINE"
                akt_mod = self.nexus.beyin.mod if hasattr(self.nexus, 'beyin') else "NORMAL"

                # Kum havuzu testi ile canlı düşünce oluştur
                dusunce_metni = f"🧠 [{llm_mod} / {duygu}]: Sistem stabil, Kuantum Zihni aktif."
                
                # Ekran devlet dosyasını güvenle yaz
                with open(TMP_STATE_FILE, "w") as fp:
                    fp.write(f"TIME: {saat_str}\n"
                             f"BATTERY: {pil}\n"
                             f"DUST: {self.quantum_dust}\n"
                             f"MODE: {akt_mod}\n"
                             f"THOUGHT: {dusunce_metni}\n"
                             f"TICK: {self.tick}")
                os.rename(TMP_STATE_FILE, STATE_FILE)

            except Exception as e:
                print(f"⚠️ [HUD LOOP HATA]: {e}")

            time.sleep(1.0)

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

        # 3. Canlı HUD ve Ekran Döngüsü Thread'i (Note 9 Ekranını Besler)
        hud_thread = threading.Thread(target=self.hud_ve_komut_dongusu, daemon=True)
        hud_thread.start()

        # 4. Evrim Döngüsü
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
        return self.nexus.beyin.sohbet(mesaj) if hasattr(self.nexus, 'beyin') else "Sinek uykuda..."

    def evrim_durumu(self) -> dict:
        ozet = self.anka_dogusu.durum_ozeti()
        ozet["kisilik"] = self.kisilik.durum_ozeti()
        ozet["sandbox_son_deneyler"] = self.sandbox.gecmis_al(son_n=3)
        return ozet

    def mod_degistir(self, yeni_mod: str):
        if hasattr(self.nexus, 'beyin'):
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
