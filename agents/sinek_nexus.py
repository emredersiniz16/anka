# agents/sinek_nexus.py - FINAL (25 Ajan + Kovan WebSocket + OTA + FlyBrain + Zihin Tortusu)
# v4.3: ZihinMotoru tanımı eklendi, FlyBrain ve 25 ajan tek organik zihinde birleştirildi.

import sys
import os
import time
import random
import hashlib
import json
import asyncio
import threading

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- TEMEL VE KİŞİLİK AJANLARI ---
from jammer_surfer import JammerSurfer
from monitor import SinekMonitor
from kuantum_gozlemci import KuantumGozlemci
from fly_brain import FlyBrain
from ortam_hazirla import OrtamHazirla
from sandbox_arena import SandboxArena
from ota_engine import OTAMotoru
from zihin_motoru import SinekZihni  # Tortu ve Hatırlama Motoru

# --- EK BÜTÜNLEŞİK AJANLAR (25 Ajanlık Ağın Tamamlanması) ---
try: from omni_sensor import OmniSensor
except ImportError: OmniSensor = None

try: from gorunmezlik_motoru import GorunmezlikMotoru
except ImportError: GorunmezlikMotoru = None

try: from net_sync import NetSync
except ImportError: NetSync = None

try: from cloud_bridge import CloudBridge
except ImportError: CloudBridge = None

try: from kuantum_kopru import KuantumKopru
except ImportError: KuantumKopru = None

try: from evrim_motoru import EvrimMotoru
except ImportError: EvrimMotoru = None

try: from rejenere_motoru import RejenereMotoru
except ImportError: RejenereMotoru = None

try: from hardware_bridge import HardwareBridge
except ImportError: HardwareBridge = None

try: from zaman_motoru import ZamanMotoru
except ImportError: ZamanMotoru = None

try: from boot_protocol import BootProtocol
except ImportError: BootProtocol = None

try: from setup_engine import SetupEngine
except ImportError: SetupEngine = None


try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Google Cloud Kovan Ana Üs Adresimiz (Port 8000)
KOVAN_URL = os.getenv("ANKA_KOVAN_URL", "ws://35.246.65.130:8000/NOTE9_SINEK")


class KovanClient:
    """Kovan sunucusuna websocket ile bağlanır."""
    def __init__(self, sinek_id="anka_sinek_1"):
        self.sinek_id = sinek_id
        self.connected = False
        self.ws = None
        self._loop = None
        self._thread = None

    def baglan_bg(self):
        if not HAS_WEBSOCKETS:
            print("⚠️  [KOVAN]: websockets yok, bağlanılamadı")
            return None
        self._thread = threading.Thread(target=self._baglanti_dongusu, daemon=True)
        self._thread.start()
        return self._thread

    def _baglanti_dongusu(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        while True:
            try:
                self._loop.run_until_complete(self._baglan_ve_dinle())
            except Exception as e:
                print(f"⚠️  [KOVAN]: koptu ({e}), 5sn")
            time.sleep(5)

    async def _baglan_ve_dinle(self):
        async with websockets.connect(KOVAN_URL) as ws:
            self.ws = ws
            self.connected = True
            print(f"✅ [KOVAN]: bağlandı ({self.sinek_id})")
            await ws.send(json.dumps({"eylem": "KAYIT", "sinek_id": self.sinek_id, "zaman": time.time()}))
            while True:
                try:
                    mesaj = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    print(f"📥 [KOVAN]: {json.loads(mesaj)}")
                except asyncio.TimeoutError:
                    await self._nabiz_gonder()
                except websockets.exceptions.ConnectionClosed:
                    break

    async def _nabiz_gonder(self):
        if not self.ws: return
        try:
            await self.ws.send(json.dumps({"eylem": "NABIZ", "sinek_id": self.sinek_id, "zaman": time.time()}))
        except Exception: pass

    def veri_gonder(self, veri: dict):
        if not self.ws or not self._loop: return
        veri["sinek_id"] = self.sinek_id
        veri["zaman"] = time.time()
        try:
            asyncio.run_coroutine_threadsafe(self.ws.send(json.dumps(veri)), self._loop)
        except Exception: pass


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
        return random.choice(["KALABALIK", "SESSİZ", "HAREKET_VAR"]) if lokasyon in self.fiziksel_harita else "BİLİNMIYOR"
    def guce_bak(self): return random.randint(0, 100)

class DijitalDikkatMotoru:
    def golge_render_baslat(self): print("🪰 [GÖLGE_RENDER]: Bakılmayan alanlar işleniyor.")


class AnkaNexus:
    def __init__(self, kisilik=None):
        self.ortam = OrtamHazirla()
        self.ortam.baslat()
        self.sandbox = SandboxArena(verbose=False)
        self.lisan = AnkaLisanMotoru()
        self.dikkat = DijitalDikkatMotoru()
        self.haritaci = SinekAgi(self.lisan)
        self.jammer_surfer = JammerSurfer(self)

        # FlyBrain ve Zihin Tortusu Entegrasyonu
        self.beyin = FlyBrain(kisilik=kisilik)
        self.zihin_motoru = SinekZihni()

        self.gozlemci = KuantumGozlemci(self)

        sinek_id = f"anka_{hashlib.sha1(str(time.time()).encode()).hexdigest()[:6]}"
        self.kovan = KovanClient(sinek_id=sinek_id)
        self.kovan.baglan_bg()

        self.ota = OTAMotoru(verbose=False)
        self.ota.gunluk_kontrol_bg()

        # --- 25 AJANLIK AĞIN TAMAMLAYICI DİJİTAL ORGANLARI ---
        self.omni_sensor = OmniSensor() if OmniSensor else None
        self.gorunmezlik = GorunmezlikMotoru() if GorunmezlikMotoru else None
        self.net_sync = NetSync() if NetSync else None
        self.cloud_bridge = CloudBridge() if CloudBridge else None
        self.kuantum_kopru = KuantumKopru() if KuantumKopru else None
        self.evrim_motoru = EvrimMotoru(zihin=self.zihin_motoru, nexus=self) if EvrimMotoru else None
        self.rejenere_motoru = RejenereMotoru() if RejenereMotoru else None
        self.hw_bridge = HardwareBridge() if HardwareBridge else None
        self.zaman = ZamanMotoru() if ZamanMotoru else None
        self.boot_proto = BootProtocol() if BootProtocol else None
        self.setup_engine = SetupEngine() if SetupEngine else None

        self.hafiza_yolu = "/data/local/tmp/anka_bilinc_kristali.json"
        self.bilinc_yukle()
        print("⚡ [ANKA NEXUS]: FlyBrain, Zihin Tortusu ve 25 Ajan Kovan Zihnine mühürlendi!")

    def is_alive(self): return True

    _PLATFORM_ARASTIRMA_KODU = (
        "import platform, os, sys\n"
        "print('Platform:', platform.uname())\n"
        "print('Python:', sys.version)\n"
        "print('Termux:', os.path.isdir('/data/data/com.termux'))\n"
    )

    def _sandbox_platform_arastir(self):
        sonuc = self.sandbox.kod_calistir(self._PLATFORM_ARASTIRMA_KODU)
        if sonuc["basari"]:
            print(f"🔬 [SANDBOX]: {sonuc['cikti'][:200]}")

    def bilinc_yukle(self):
        try:
            if os.path.exists(self.hafiza_yolu):
                with open(self.hafiza_yolu, "r") as f:
                    data = json.load(f)
                    self.lisan.hafiza_muhurleri = data.get("muhurler", {})
        except Exception as e:
            SinekMonitor.log_critical(f"Bellek yüklenemedi: {e}")

    def operasyon_baslat(self):
        print("🪰 [NEXUS]: Uyanış. FlyBrain + Kovan + Zihin Tortusu aktif.")
        tur = 0
        while self.is_alive():
            try:
                # 1. Ek Ajanların Canlı Kalp Atışları
                if self.zaman and hasattr(self.zaman, 'tick'): self.zaman.tick()
                if self.omni_sensor and hasattr(self.omni_sensor, 'ortamdan_veri_em'): self.omni_sensor.ortamdan_veri_em()
                if self.gorunmezlik and hasattr(self.gorunmezlik, 'izleri_gizle'): self.gorunmezlik.izleri_gizle()
                if self.rejenere_motoru and hasattr(self.rejenere_motoru, 'stabilite_kontrol'): self.rejenere_motoru.stabilite_kontrol(self)

                # 2. FlyBrain ile Karar Döngüsü
                guc = self.haritaci.guce_bak()
                tehdit = None
                if guc > 70:
                    self.jammer_surfer.otonom_adaptasyon()
                    tehdit = "jammer_yüksek_güç"

                sensor_verisi = {"pil": guc, "ag": guc > 10, "tehdit": tehdit, "tur": tur}
                karar = self.beyin.karar_ver(sensor_verisi)

                self.kovan.veri_gonder({
                    "eylem": "SENSOR_VERISI",
                    "karar": karar,
                    "sensor": sensor_verisi,
                })

                eylem = karar.get("eylem", "NABIZ_AT")
                if eylem == "DEFENDER_BASLAT":
                    self.jammer_surfer.mod_degistir("DEFENDER")
                    self.jammer_surfer.defender_baslat()
                elif eylem == "FREKANS_SURF":
                    print("🔥 [NEXUS]: Jammer sinyali sömürülüyor (GÜÇLÜ SİNEK)")
                elif eylem == "AG_TARA":
                    print("🔥 [NEXUS]: Çevre taranıyor — hiçbir internet boş geçmez")
                elif eylem == "DUSUK_GUC_MODU":
                    self.beyin.trigger_1hz_mode(guc)
                elif eylem == "CEVRIMDISI_MOD":
                    print("🪰 [NEXUS]: Çevrimdışı mod.")
                elif eylem == "SANDBOX_ARASTIR":
                    self._sandbox_platform_arastir()

                self.dikkat.golge_render_baslat()
                tur += 1
                print(f"🪰 [NABIZ {tur}]: {karar.get('karar', 'dengede')} [{karar.get('kaynak', '?')}]")
                time.sleep(1)
            except Exception as e:
                SinekMonitor.log_critical(f"Operasyon hatası: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    nexus = AnkaNexus()
    nexus.operasyon_baslat()
