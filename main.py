# main.py - SİNEK (OTONOM KUANTUM AJAN) - GÜNCEL
import time
import threading
import sqlite3
import os
import asyncio
import websockets
import json
import ctypes # KUANTUM KATMANI İÇİN
from core.hardware_bridge import HardwareBridge
from agents.fly_brain import FlyBrain

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        self.websocket = None
        
        print(f"[SİNEK] Kuantum uyanış başlıyor... Token: {self.token}")
        
        # --- 1. SİSTEM BİRİMLERİ ---
        self.brain = FlyBrain()
        self.quantum_init() # Yeni: Kuantum motoru devreye girdi
        self.kara_kutu_kur()
        self.donanim_koprusu_kur()
        
        if self.bridge.aktif:
            self.bridge.konus("Kuantum Sinek uyandı")
            self.bridge.titresim_ver(200)

    def quantum_init(self):
        """Kuantum motorunu (.so) yükle ve FSM'i tetikle."""
        try:
            self.dust = ctypes.CDLL("./core/quantum/libanka_quantum.so")
            # FSM ve Collapse motorunu C seviyesinde bağla
            self.dust.qd_init(None, b"Note9_Merlin_FP", b"KovanSecret_v1")
            print("[SİNEK] Kuantum Toz deposu (libanka_quantum) hazır.")
        except Exception as e:
            print(f"[HATA] Kuantum motoru yüklenemedi: {e}")

    def kara_kutu_kur(self):
        self.db_baglanti = sqlite3.connect("sinek_hafiza.db", check_same_thread=False)
        # ... (Kara Kutu mantığın aynı kalıyor) ...
        print("[SİNEK] Kara Kutu (SQLite) devrede.")

    def donanim_koprusu_kur(self):
        self.bridge = HardwareBridge()
        print(f"[SİNEK] Donanım köprüsü: {'AKTİF'}")

    # ... (eylem_kamera_cek, eylem_konus aynı kalıyor) ...

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
                        
                        # --- KUANTUM DÖNÜŞÜMÜ ---
                        # Kovan'dan gelen veriyi toz olarak mühürle
                        self.dust.qd_seal(None, 2, json.dumps(komut).encode(), len(json.dumps(komut)), None)
                        
                        eylem = komut.get('eylem')
                        # FSM Tetiklemesi: Kovan'dan emir gelince durum değişir
                        self.dust.sinek_fsm_handle_event(None, 3, None, 0) # KOVAN_MSG eventi
                        
                        if self.brain.process_anomaly(eylem) != "ENTER_SAFE_MODE":
                            # ... (eylem mantığı aynı) ...
            except Exception as e:
                print(f"[AĞ HATASI] ({e})")
                await asyncio.sleep(5)

    def kovan_icin_yasa(self):
        t1 = threading.Thread(target=self.canli_baglanti_dinle, daemon=True)
        t1.start()
        # Yeni: Kuantum Nabız döngüsü (C'deki collapse_loop'u buradan tetikle)
        while self.hayatta_mi:
            self.dust.collapse_fire(4, None, 0) # TIMER eventi (1Hz nabız)
            time.sleep(1)

    # ... (diğer metodlar aynı kalıyor) ...

if __name__ == "__main__":
    sinek = HarcanabilirSinek(os.getenv("SINEK_TOKEN", "KAYITSIZ_SINEK"))
    sinek.kovan_icin_yasa()
