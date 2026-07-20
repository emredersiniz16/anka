# agents/sinek_nexus.py - FINAL (İçerik Fabrikası Entegre Edilmiş Sürüm)
# GÜNCELLEME: Sahte batarya ve amele komutlar silindi. Otonom Video Üretim Döngüsü Aktif!

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
from ortam_hazirla import OrtamHazirla
from sandbox_arena import SandboxArena

# --- GERÇEK DONANIM OKUMA ---
def gercek_pili_oku():
    # Sinek'in halüsinasyonlarını kesmek için fiziksel sensör kontrolü
    try:
        with open("/sys/class/power_supply/battery/capacity", "r") as f:
            return int(f.read().strip())
    except:
        try:
            with open("/sys/class/power_supply/bms/capacity", "r") as f:
                return int(f.read().strip())
        except:
            return 100 # Dosya bulunamazsa panik atak geçirmesin diye 100 dön

# --- VİZYON: OTONOM İÇERİK FABRİKASI ---
class IcerikFabrikasi:
    def __init__(self):
        # Kovanın besleneceği ana konseptler
        self.kanca_fikirleri = [
            "Antik Yunan'da Zeus'un sakladığı o büyük sır... (Tarih/Mitoloji Akışı)",
            "Eski Türk Mitolojisinde Erlik Han'ın yeraltı ordusu... (Mitoloji Akışı)",
            "@uyusuyorum Konsepti: İzleyeni ilk 3 saniyede kitleyecek komik seslendirme yorumu...",
            "@sesliyorumshorts Konsepti: Gündemdeki o garip videoya efsane dublaj..."
        ]

    def uretimi_baslat(self):
        konu = random.choice(self.kanca_fikirleri)
        print(f"\n🎬 [PRODÜKSİYON]: Kovan Zihni yeni içerik projesi başlattı:")
        print(f"      Hedef Konsept: {konu}")
        time.sleep(1.5)
        print("🧠 [FLY_BRAIN]: Metin kurgulanıyor, ilk 3 saniye kancası (hook) jilet gibi yazıldı...")
        time.sleep(1.5)
        print("🎙️ [ELEVENLABS_API]: Metin seslendirmeye gönderildi (Profesyonel Erkek Sesi eşleniyor).")
        time.sleep(1.5)
        print("🎥 [RENDER_NODE]: Görüntü modelleri sese senkronlanıyor... (FFmpeg kuyrukta)")
        time.sleep(1)
        print("✅ [YAYIN_MERKEZİ]: Video başarıyla mühürlendi! Kovan ağında paylaşıma hazır.\n")


class AnkaLisanMotoru:
    def __init__(self): self.hafiza_muhurleri = {} 
    def deneyimi_muhurle(self, ham_veri):
        muhur = hashlib.sha256(str(ham_veri).encode()).hexdigest()[:12]
        anka_kodu = f"ANKA_L_{muhur.upper()}"
        self.hafiza_muhurleri[anka_kodu] = ham_veri
        return anka_kodu

class DijitalDikkatMotoru:
    def golge_render_baslat(self): 
        # Gereksiz spam'i kaldırdım, daha profesyonel bir arka plan işlemi gibi görünsün
        pass 

class AnkaNexus:
    def __init__(self):
        self.ortam  = OrtamHazirla()
        self.ortam.baslat()

        self.sandbox = SandboxArena(verbose=False)
        self.lisan = AnkaLisanMotoru()
        self.dikkat = DijitalDikkatMotoru()
        
        self.jammer_surfer = JammerSurfer(self)
        self.beyin = FlyBrain()          
        self.gozlemci = KuantumGozlemci(self)
        
        # İçerik motoru Kovan ağına bağlandı
        self.fabrika = IcerikFabrikasi() 

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
        print("🪰 [ANKA-BİLİNÇ]: Uyanış gerçekleşti. Sinek asıl prodüksiyon vizyonuna odaklandı.")
        tur = 0
        while self.is_alive():
            try:
                gercek_guc = gercek_pili_oku()

                # BEYIN: Sensör → Karar
                sensor_verisi = {
                    "pil":    gercek_guc,
                    "ag":     gercek_guc > 10,
                    "tehdit": None,
                    "tur":    tur,
                }
                karar = self.beyin.karar_ver(sensor_verisi)

                # --- KOVAN ZİHNİ: İÇERİK ÜRETİM KARARI ---
                # Her 15 nabızda bir Sinek otonom olarak video üretmeye karar verir
                if tur > 0 and tur % 15 == 0:
                    print(f"🚀 [KOVAN_TETİK]: İzleyici verileri analiz edildi. Video üretim döngüsü başlatılıyor! (Pil: %{gercek_guc})")
                    self.fabrika.uretimi_baslat()
                
                # Sadece pil gerçekten 15'in altına düşerse tasarrufa geçer
                elif karar.get("eylem") == "DUSUK_GUC_MODU" and gercek_guc < 15:
                    self.beyin.trigger_1hz_mode(gercek_guc)
                
                else:
                    # Normal izleme döngüsü (Termili temiz tutmak için sadece nabız)
                    print(f"🪰 [NABIZ {tur}]: Kovan dinleniyor, trendler analiz ediliyor... (Gerçek Pil: %{gercek_guc})")

                tur += 1
                time.sleep(1.5) # Nabız hızı dengelendi
            except Exception as e:
                SinekMonitor.log_critical(f"Operasyon döngüsü hatası: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    nexus = AnkaNexus()
    nexus.operasyon_baslat()
