# agents/sinek_nexus.py - FINAL (Gözlemci Sağlama Alınmış Sürüm)
# GÜNCELLEME: FlyBrain (LLM) entegre edildi — sensör → beyin → karar döngüsü aktif.

import sys
import os
import time
import random
import hashlib
import json

# --- YOL KİLİDİ ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from jammer_surfer import JammerSurfer
from monitor import SinekMonitor
from kuantum_gozlemci import KuantumGozlemci
from fly_brain import FlyBrain

class AnkaLisanMotoru:
    def __init__(self): self.hafiza_muhurleri = {} 
    def deneyimi_muhurle(self, ham_veri):
        muhur = hashlib.sha256(str(ham_veri).encode()).hexdigest()[:12]
        anka_kodu = f"ANKA_L_{muhur.upper()}"
        self.hafiza_muhurleri[anka_kodu] = ham_veri
        return anka_kodu

class SinekAgi:
    def __init__(self, lisan):
        self.lisan = lisan
        self.fiziksel_harita = {}
    def her_noktayi_isaretle(self, gorus_alani_id):
        iz = hashlib.sha256(f"NOKTA_{gorus_alani_id}_{time.time()}".encode()).hexdigest()[:8]
        self.fiziksel_harita[gorus_alani_id] = iz
        return iz
    def frekans_yolla_ve_oku(self, lokasyon):
        return random.choice(["KALABALIK", "SESSİZ", "HAREKET_VAR"]) if lokasyon in self.fiziksel_harita else "BİLİNMİYOR"
    def guce_bak(self): return random.randint(0, 100)

class DijitalDikkatMotoru:
    def golge_render_baslat(self): print("🪰 [GÖLGE_RENDER]: Bakılmayan alanlar işleniyor.")

class AnkaNexus:
    def __init__(self):
        self.lisan = AnkaLisanMotoru()
        self.dikkat = DijitalDikkatMotoru()
        self.haritaci = SinekAgi(self.lisan)
        self.jammer_surfer = JammerSurfer(self)
        self.beyin = FlyBrain()          # ← Gerçek düşünce motoru

        # --- GÖZLEMCİ TANIMLANDI VE SAĞLAMAYA ALINDI ---
        self.gozlemci = KuantumGozlemci(self)

        self.hafiza_yolu = "/data/local/tmp/anka_bilinc_kristali.json"
        self.bilinc_yukle()

    def is_alive(self):
        return True

    def bilinc_yukle(self):
        try:
            if os.path.exists(self.hafiza_yolu):
                with open(self.hafiza_yolu, "r") as f:
                    data = json.load(f)
                    self.lisan.hafiza_muhurleri = data.get("muhurler", {})
        except Exception as e:
            SinekMonitor.log_critical(f"Bellek yüklenemedi: {e}")

    def operasyon_baslat(self):
        print("🪰 [ANKA-BİLİNÇ]: Uyanış gerçekleşti.")
        tur = 0
        while self.is_alive():
            try:
                # --- SENSÖR OKU ---
                guc = self.haritaci.guce_bak()
                tehdit = None

                # Jammer tehdit kontrolü
                if guc > 70:
                    self.jammer_surfer.otonom_adaptasyon()
                    tehdit = "jammer_yüksek_güç"

                # --- BEYIN: Sensör → Karar ---
                sensor_verisi = {
                    "pil":    guc,
                    "ag":     guc > 10,          # Simülasyon: düşük güçte ağ yok
                    "tehdit": tehdit,
                    "tur":    tur,
                }
                karar = self.beyin.karar_ver(sensor_verisi)

                # --- KARAR UYGULA ---
                eylem = karar.get("eylem", "NABIZ_AT")
                if eylem == "DEFENDER_BASLAT":
                    self.jammer_surfer.mod_degistir("DEFENDER")
                    self.jammer_surfer.defender_baslat()
                elif eylem == "DUSUK_GUC_MODU":
                    self.beyin.trigger_1hz_mode(guc)
                elif eylem == "CEVRIMDISI_MOD":
                    print("🪰 [NEXUS]: Çevrimdışı moda geçildi.")

                self.dikkat.golge_render_baslat()
                tur += 1
                print(f"🪰 [NABIZ {tur}]: {karar.get('karar', 'Sistem dengede')} "
                      f"[{karar.get('kaynak', '?')}]")
                time.sleep(1)
            except Exception as e:
                SinekMonitor.log_critical(f"Operasyon döngüsü hatası: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    nexus = AnkaNexus()
    nexus.operasyon_baslat()
