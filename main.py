# main.py - SİNEK (OTONOM KUANTUM AJAN) - DÜZELTİLMİŞ
import time
import threading
import sqlite3
import os
import asyncio
import websockets
import json
import ctypes
from core.hardware_bridge import HardwareBridge
from agents.fly_brain import FlyBrain

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        self.websocket = None
        
        print(f"[SİNEK] Kuantum uyanış başlıyor... Token: {self.token}")
        
        self.brain = FlyBrain()
        self.quantum_init()
        self.kara_kutu_kur()
        self.donanim_koprusu_kur()
        
        if self.bridge.aktif:
            self.bridge.konus("Kuantum Sinek uyandı")
            self.bridge.titresim_ver(200)

    def quantum_init(self):
        try:
            self.dust = ctypes.CDLL("./core/quantum/libanka_quantum.so")
            # qd_init, collapse_init vs. C fonksiyonlarını buraya ekleyebilirsin
            print("[SİNEK] Kuantum Toz deposu (libanka_quantum) hazır.")
        except Exception as e:
            print(f"[HATA] Kuantum motoru yüklenemedi: {e}")

    def kara_kutu_kur(self):
        self.db_baglanti = sqlite3.connect("sinek_hafiza.db", check_same_thread=False)
        cursor = self.db_baglanti.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS bekleyen_veriler (id INTEGER PRIMARY KEY AUTOINCREMENT, islem_tipi TEXT, veri_yolu TEXT, zaman DATETIME DEFAULT CURRENT_TIMESTAMP)")
        self.db_baglanti.commit()
        print("[SİNEK] Kara Kutu (SQLite) devrede.")

    def donanim_koprusu_kur(self):
        self.bridge = HardwareBridge()
        self.bridge.aktif = True
        print(f"[SİNEK] Donanım köprüsü: AKTİF")

    async def canli_baglanti_kur(self):
        uri = f"ws://127.0.0.1:8000/{self.token}"
        while self.hayatta_mi:
            try:
                async with websockets.connect(uri) as ws:
                    self.websocket = ws
                    print(f"[AĞ] Kovan'a bağlandım.")
                    while self.hayatta_mi:
                        mesaj = await ws.recv()
                        komut = json.loads(mesaj)
                        
                        # Kuantum Dönüşümü
                        self.dust.qd_seal(None, 2, json.dumps(komut).encode(), len(json.dumps(komut)), None)
                        
                        eylem = komut.get('eylem')
                        self.dust.sinek_fsm_handle_event(None, 3, None, 0)
                        
                        if self.brain.process_anomaly(eylem) != "ENTER_SAFE_MODE":
                            if eylem == 'FOTOGRAF_CEK': pass # eylem mantığın buraya
            except Exception as e:
                print(f"[AĞ HATASI] ({e})")
                await asyncio.sleep(5)

    def canli_baglanti_dinle(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.canli_baglanti_kur())

    def kovan_icin_yasa(self):
        # 1. Ağ dinleyicisi thread'i
        t1 = threading.Thread(target=self.canli_baglanti_dinle, daemon=True)
        t1.start()
        
        # 2. Ana nabız döngüsü (Kuantum Nabız)
        while self.hayatta_mi:
            try:
                # C tabanlı nabız tetikleyicisi
                self.dust.collapse_fire(4, None, 0)
                time.sleep(1)
            except Exception as e:
                print(f"[SİNEK NABIZ] Hata: {e}")
                time.sleep(5)

if __name__ == "__main__":
    sinek = HarcanabilirSinek(os.getenv("SINEK_TOKEN", "KAYITSIZ_SINEK"))
    sinek.kovan_icin_yasa()
