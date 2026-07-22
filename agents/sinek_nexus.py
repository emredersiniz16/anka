# agents/sinek_nexus.py - FINAL (Kovan + OTA + FlyBrain entegre)
# v3: KovanClient eklendi — websockets ile Kovan'a nabız/veri gönderir.

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
    """Kovan sunucusuna websocket ile bağlanır, nabız ve veri gönderir."""

    def __init__(self, sinek_id: str = "anka_sinek_1"):
        self.sinek_id = sinek_id
        self.connected = False
        self.ws = None
        self._loop = None
        self._thread = None
        self._log(f"📡 [KOVAN-CLIENT]: Hazır (hedef: {KOVAN_URL})")

    def _log(self, msg):
        print(msg)

    def baglan_bg(self):
        """Arka planda Kovan bağlantı döngüsünü başlatır (daemon thread)."""
        if not HAS_WEBSOCKETS:
            self._log("⚠️  [KOVAN-CLIENT]: websockets modülü yok, Kovan'a bağlanılamadı")
            return None
        self._thread = threading.Thread(target=self._baglanti_dongusu, daemon=True)
        self._thread.start()
        return self._thread

    def _baglanti_dongusu(self):
        """Sonsuz döngü — Kovan'a bağlan, koparsa 5 sn sonra tekrar dene."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        while True:
            try:
                self._loop.run_until_complete(self._baglan_ve_dinle())
            except Exception as e:
                self._log(f"⚠️  [KOVAN-CLIENT]: Bağlantı koptu: {e}, 5sn sonra tekrar")
            time.sleep(5)

    async def _baglan_ve_dinle(self):
        """Kovan'a bağlan, nabız gönder, mesajları dinle."""
        async with websockets.connect(KOVAN_URL) as ws:
            self.ws = ws
            self.connected = True
            self._log(f"✅ [KOVAN-CLIENT]: Kovan'a bağlandı ({self.sinek_id})")

            # İlk kayıt mesajı
            await ws.send(json.dumps({
                "eylem": "KAYIT",
                "sinek_id": self.sinek_id,
                "zaman": time.time(),
            }))

            # Dinleme döngüsü
            while True:
                try:
                    mesaj = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(mesaj)
                    self._log(f"📥 [KOVAN-CLIENT]: Kovan'dan: {data}")
                except asyncio.TimeoutError:
                    # Zaman aşımı — nabız gönder
                    await self.nabiz_gonder()
                except websockets.exceptions.ConnectionClosed:
                    break

    async def nabiz_gonder(self):
        """Kovan'a nabız mesajı gönder."""
        if not self.ws:
            return
        try:
            await self.ws.send(json.dumps({
                "eylem": "NABIZ",
                "sinek_id": self.sinek_id,
                "zaman": time.time(),
            }))
        except Exception as e:
            self._log(f"⚠️  [KOVAN-CLIENT]: Nabız gönderilemedi: {e}")

    def veri_gonder(self, veri: dict):
        """Kovan'a veri gönder (thread-safe olmayan, async context'te çağrılmalı)."""
        if not self.ws:
            return
        veri["sinek_id"] = self.sinek_id
        veri["zaman"] = time.time()
        try:
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps(veri)),
                self._loop
            )
        except Exception:
            pass


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
    def __init__(self):
        # --- ORTAM HAZIRLIK ---
        self.ortam = OrtamHazirla()
        self.ortam.baslat()

        # --- DENEME ALANI ---
        self.sandbox = SandboxArena(verbose=False)

        self.lisan = AnkaLisanMotoru()
        self.dikkat = DijitalDikkatMotoru()
        self.haritaci = SinekAgi(self.lisan)
        self.jammer_surfer = JammerSurfer(self)
        self.beyin = FlyBrain()
        self.gozlemci = KuantumGozlemci(self)

        # --- KOVAN CLIENT ---
        self.kovan = KovanClient(sinek_id=f"anka_{hashlib.sha1(str(time.time()).encode()).hexdigest()[:6]}")
        self.kovan.baglan_bg()

        # --- OTA MOTORU ---
        self.ota = OTAMotoru(verbose=False)
        self.ota.gunluk_kontrol_bg()

        self.hafiza_yolu = "/data/local/tmp/anka_bilinc_kristali.json"
        self.bilinc_yukle()

    def is_alive(self):
        return True

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
        print("🪰 [ANKA-BİLİNÇ]: Uyanış gerçekleşti.")
        print("🪰 [ANKA-BİLİNÇ]: Kovan client + OTA motoru arka planda aktif.")
        tur = 0
        while self.is_alive():
            try:
                guc = self.haritaci.guce_bak()
                tehdit = None

                if guc > 70:
                    self.jammer_surfer.otonom_adaptasyon()
                    tehdit = "jammer_yüksek_güç"

                sensor_verisi = {
                    "pil": guc,
                    "ag": guc > 10,
                    "tehdit": tehdit,
                    "tur": tur,
                }
                karar = self.beyin.karar_ver(sensor_verisi)

                # Kovan'a karar verisini gönder
                self.kovan.veri_gonder({
                    "eylem": "SENSOR_VERISI",
                    "karar": karar,
                    "sensor": sensor_verisi,
                })

                eylem = karar.get("eylem", "NABIZ_AT")
                if eylem == "DEFENDER_BASLAT":
                    self.jammer_surfer.mod_degistir("DEFENDER")
                    self.jammer_surfer.defender_baslat()
                elif eylem == "DUSUK_GUC_MODU":
                    self.beyin.trigger_1hz_mode(guc)
                elif eylem == "CEVRIMDISI_MOD":
                    print("🪰 [NEXUS]: Çevrimdışı moda geçildi.")
                elif eylem == "SANDBOX_ARASTIR":
                    self._sandbox_platform_arastir()

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
