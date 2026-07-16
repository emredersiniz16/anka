# main.py - SİNEK (OTONOM AJAN) MERKEZİ
import time
import threading
import sqlite3
import os
import asyncio
import websockets
import json
from core.hardware_bridge import HardwareBridge
from agents.fly_brain import FlyBrain

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        self.websocket = None # Soket nesnesi globalde
        
        print(f"[SİNEK] Uyanıyor... Token: {self.token}")
        
        self.brain = FlyBrain()
        self.kara_kutu_kur()
        self.donanim_koprusu_kur()
        self.rol = self.donanim_tara()

        if self.bridge.aktif:
            self.bridge.konus("Sinek uyandı")
            self.bridge.titresim_ver(200)

    def kara_kutu_kur(self):
        self.db_baglanti = sqlite3.connect("sinek_hafiza.db", check_same_thread=False)
        cursor = self.db_baglanti.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bekleyen_veriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                islem_tipi TEXT,
                veri_yolu TEXT,
                zaman DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db_baglanti.commit()
        print("[SİNEK] Kara Kutu (SQLite) devrede.")

    def donanim_koprusu_kur(self):
        self.bridge = HardwareBridge()
        print(f"[SİNEK] Donanım köprüsü: {'AKTİF' if self.bridge.aktif else 'PASİF'}")

    def veriyi_guvenceye_al(self, islem_tipi, veri_yolu):
        cursor = self.db_baglanti.cursor()
        cursor.execute("INSERT INTO bekleyen_veriler (islem_tipi, veri_yolu) VALUES (?, ?)", (islem_tipi, veri_yolu))
        self.db_baglanti.commit()

    def donanim_tara(self):
        return "GOREN_SINEK"

    def eylem_kamera_cek(self, dosya_adi):
        if self.bridge and self.bridge.aktif:
            dosya_yolu = self.bridge.kamera_cek(dosya_adi)
            if dosya_yolu: 
                self.veriyi_guvenceye_al("KAMERA_CEKIMI", dosya_yolu)

    def eylem_konus(self, metin):
        if self.bridge and self.bridge.aktif:
            self.bridge.konus(metin)
            self.veriyi_guvenceye_al("SES_CIKISI", metin)

    async def canli_baglanti_kur(self):
        uri = f"ws://127.0.0.1:8000/{self.token}"
        while self.hayatta_mi:
            try:
                async with websockets.connect(uri) as ws:
                    self.websocket = ws 
                    print(f"[AĞ] Kovan'a bağlandım. Görev bekleniyor...")
                    while self.hayatta_mi:
                        mesaj = await ws.recv()
                        komut = json.loads(mesaj)
                        eylem = komut.get('eylem')
                        print(f"\n[!!!] KOVAN'DAN EMİR GELDİ: {komut}")
                        
                        if self.brain.process_anomaly(eylem) != "ENTER_SAFE_MODE":
                            if eylem == 'FOTOGRAF_CEK': 
                                self.eylem_kamera_cek(komut.get('dosya_adi', 'cekim'))
                            elif eylem == 'KONUS': 
                                self.eylem_konus(komut.get('metin', ''))
                            elif eylem == 'TITRESIM' and self.bridge.aktif: 
                                self.bridge.titresim_ver(komut.get('ms', 500))
            except Exception as e:
                self.websocket = None
                print(f"[AĞ HATASI] Kovan'a ulaşılamıyor, tekrar deneniyor... ({e})")
                await asyncio.sleep(5)

    async def nabiz_gonder_async(self):
        while self.hayatta_mi:
            # DÜZELTME: ".open" özelliği kaldırıldı, sadece nesnenin varlığını kontrol ediyoruz.
            if self.websocket:
                try:
                    await self.websocket.send(json.dumps({"eylem": "NABIZ", "token": self.token}))
                    print("[AĞ] Kovan'a nabız atıldı.")
                except Exception as e: 
                    print(f"[AĞ HATASI] Nabız başarısız: {e}")
            
            await asyncio.sleep(5) 

    def canli_baglanti_dinle(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(self.canli_baglanti_kur(), self.nabiz_gonder_async()))

    def kovan_icin_yasa(self):
        t1 = threading.Thread(target=self.canli_baglanti_dinle, daemon=True)
        t1.start()
        try:
            while self.hayatta_mi: 
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SİNEK] Kapatılıyor... Kara Kutu kilitlendi.")
            self.hayatta_mi = False
            self.db_baglanti.close()

if __name__ == "__main__":
    sinek = HarcanabilirSinek(os.getenv("SINEK_TOKEN", "KAYITSIZ_SINEK"))
    sinek.kovan_icin_yasa()
