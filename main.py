import time
import threading
import sqlite3
import os
import asyncio
import websockets
import json
from core.hardware_bridge import HardwareBridge
from agents.fly_brain import FlyBrain # Beyin eklendi

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        self.rotation_aktif = False 
        
        print(f"[SİNEK] Uyanıyor... Token: {self.token}")
        
        self.brain = FlyBrain() # Beyin başlatıldı
        self.kara_kutu_kur()
        self.donanim_koprusu_kur()
        self.rol = self.donanim_tara()

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
        print("[SİNEK] Donanım köprüsü (HAL) aranıyor...")
        self.bridge = HardwareBridge()
        if self.bridge.aktif:
            print("[SİNEK] Donanım köprüsü başarıyla zihne bağlandı.")
        else:
            print("[SİNEK UYARI] Donanım köprüsü aktif değil! Bağımsız mod devrede.")

    def veriyi_guvenceye_al(self, islem_tipi, veri_yolu):
        cursor = self.db_baglanti.cursor()
        cursor.execute("INSERT INTO bekleyen_veriler (islem_tipi, veri_yolu) VALUES (?, ?)", (islem_tipi, veri_yolu))
        self.db_baglanti.commit()
        print(f"[HAFIZA] Veri kara kutuya yazıldı: {islem_tipi}")

    def donanim_tara(self):
        print("[SİNEK] Donanım kapasitesi taranıyor...")
        return "GOREN_SINEK"

    def eylem_kamera_cek(self, dosya_adi):
        if self.bridge and self.bridge.aktif:
            dosya_yolu = self.bridge.kamera_cek(dosya_adi)
            if dosya_yolu:
                self.veriyi_guvenceye_al("KAMERA_CEKIMI", dosya_yolu)
        else:
            print("[EYLEM HATA] Donanım köprüsü aktif değil, kamera kullanılamıyor!")

    def eylem_konus(self, metin):
        if self.bridge and self.bridge.aktif:
            self.bridge.konus(metin)
            self.veriyi_guvenceye_al("SES_CIKISI", metin)
        else:
            print("[EYLEM HATA] Donanım köprüsü aktif değil, ses çıkışı yok!")

    async def canli_baglanti_kur(self):
        uri = "ws://127.0.0.1:8000/ws/"
        print(f"[AĞ] Kovan aranıyor...")
        
        while self.hayatta_mi:
            try:
                async with websockets.connect(f"{uri}{self.token}") as websocket:
                    print("[AĞ] Kovan'a bağlandım, emir bekliyorum...")
                    while self.hayatta_mi:
                        mesaj = await websocket.recv()
                        komut = json.loads(mesaj)
                        
                        # EMİR İŞLEME MERKEZİ (Beyin Süzgeci)
                        eylem = komut.get('eylem')
                        if self.brain.process_anomaly(eylem) != "ENTER_SAFE_MODE":
                            if eylem == 'FOTOGRAF_CEK':
                                self.eylem_kamera_cek(komut.get('dosya_adi', 'default_cekim'))
                            elif eylem == 'KONUS':
                                self.eylem_konus(komut.get('metin', ''))
                            elif eylem == 'TITRESIM':
                                if self.bridge and self.bridge.aktif:
                                    self.bridge.titresim_ver(komut.get('ms', 500))
                        else:
                            print(f"[SİNEK] Beyin {eylem} komutunu reddetti.")
                            
            except Exception:
                await asyncio.sleep(10)

    def canli_baglanti_dinle(self):
        asyncio.run(self.canli_baglanti_kur())

    def kovan_icin_yasa(self):
        t1 = threading.Thread(target=self.canli_baglanti_dinle)
        t1.start()
        try:
            while self.hayatta_mi:
                time.sleep(1)
        except KeyboardInterrupt:
            self.hayatta_mi = False
            t1.join()
            self.db_baglanti.close()

if __name__ == "__main__":
    SINEK_GIZLI_TOKEN = os.getenv("SINEK_TOKEN", "KAYITSIZ_SINEK")
    sinek = HarcanabilirSinek(SINEK_GIZLI_TOKEN)
    sinek.kovan_icin_yasa()
