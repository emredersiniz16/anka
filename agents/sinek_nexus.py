# agents/sinek_nexus.py - FINAL (Kovan + OTA + FlyBrain + Kisilik entegre)
# v4: AnkaNexus artık kisilik parametresi alır → FlyBrain'e geçer.
#     Kararlar kişilikten, sohbet duygudan etkilenir.

import sys
import os
import time
import random
import hashlib
import json
import asyncio
import threading

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from jammer_surfer import JammerSurfer
from monitor import SinekMonitor
from kuantum_gozlemci import KuantumGozlemci
from fly_brain import FlyBrain
from ortam_hazirla import OrtamHazirla
from sandbox_arena import SandboxArena
from ota_engine import OTAMotoru

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

KOVAN_URL = os.getenv("ANKA_KOVAN_URL", "ws://localhost:8000")


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

        # FlyBrain'e kisilik geç — kararlar kişilikten etkilenir
        self.beyin = FlyBrain(kisilik=kisilik)

        self.gozlemci = KuantumGozlemci(self)

        sinek_id = f"anka_{hashlib.sha1(str(time.time()).encode()).hexdigest()[:6]}"
        self.kovan = KovanClient(sinek_id=sinek_id)
        self.kovan.baglan_bg()

        self.ota = OTAMotoru(verbose=False)
        self.ota.gunluk_kontrol_bg()

        self.hafiza_yolu = "/data/local/tmp/anka_bilinc_kristali.json"
        self.bilinc_yukle()

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
        print("🪰 [NEXUS]: Uyanış. Kovan + OTA + Kişilik aktif.")
        tur = 0
        while self.is_alive():
            try:
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
