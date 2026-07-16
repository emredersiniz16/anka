import time
import threading
import sqlite3
import os
import asyncio
import websockets
import json
from core.hardware_bridge import HardwareBridge # SİHRİN GELDİĞİ YER

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        self.rotation_aktif = False 
        
        print(f"[SİNEK] Uyanıyor... Token: {self.token}")
        
        # 1. Kara Kutuyu Kur (İnternet yoksa veriler buraya yazılacak)
        self.kara_kutu_kur()
        
        # 2. Donanım Köprüsünü (HAL) Zihne Bağla
        self.donanim_koprusu_kur()
        
        # 3. Donanımı Tara ve Rolü Al
        self.rol = self.donanim_tara()

    def kara_kutu_kur(self):
        """Sinek'in çevrimdışı hafızası."""
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
        """Yeni HAL Mimarisi ile donanıma sızma işlemi."""
        print("[SİNEK] Donanım köprüsü (HAL) aranıyor...")
        self.bridge = HardwareBridge()
        if self.bridge.aktif:
            print("[SİNEK] Donanım köprüsü başarıyla zihne bağlandı.")
        else:
            print("[SİNEK UYARI] Donanım köprüsü aktif değil! Bağımsız mod devrede.")

    def token_guncelle(self, yeni_token):
        if self.rotation_aktif:
            self.token = yeni_token
            print(f"[GÜVENLİK] Token güncellendi.")
        else:
            print("[GÜVENLİK] Rotation kapalı, güncelleme yoksayıldı.")

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
        """Kovan'a WebSocket üzerinden bağlanır ve emirleri dinler."""
        uri = "ws://127.0.0.1:8000/ws/" # Telefon (Termux) için lokal IP ayarlandı
        print(f"[AĞ] Kovan aranıyor...")
        
        while self.hayatta_mi:
            try:
                # Token ile Kovan'a bağlan
                async with websockets.connect(f"{uri}{self.token}") as websocket:
                    print("[AĞ] Kovan'a bağlandım, emir bekliyorum...")
                    while self.hayatta_mi:
                        mesaj = await websocket.recv()
                        komut = json.loads(mesaj)
                        
                        # EMİR İŞLEME MERKEZİ
                        eylem = komut.get('eylem')
                        if eylem == 'FOTOGRAF_CEK':
                            self.eylem_kamera_cek(komut.get('dosya_adi', 'default_cekim'))
                        elif eylem == 'KONUS':
                            self.eylem_konus(komut.get('metin', ''))
                        elif eylem == 'TITRESIM':
                            if self.bridge and self.bridge.aktif:
                                self.bridge.titresim_ver(komut.get('ms', 500))
                            
            except Exception as e:
                print(f"[AĞ HATA] Kovan ile bağ koptu, 10 saniye sonra tekrar deniyorum...")
                await asyncio.sleep(10)

    def canli_baglanti_dinle(self):
        """Thread içinde asenkron döngüyü başlatır."""
        asyncio.run(self.canli_baglanti_kur())

    def nabiz_gonder(self):
        while self.hayatta_mi:
            if self.token != "KAYITSIZ_SINEK":
                print(f"[AĞ] Nabız atışı gönderildi (Token: {self.token[:5]}...)")
            time.sleep(300) 

    def kovan_icin_yasa(self):
        t1 = threading.Thread(target=self.canli_baglanti_dinle)
        t2 = threading.Thread(target=self.nabiz_gonder)
        t1.start()
        t2.start()

        try:
            while self.hayatta_mi:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SİNEK] Ölüm emri alındı! Kapatılıyor...")
            self.hayatta_mi = False
            t1.join()
            t2.join()
            self.db_baglanti.close()

if __name__ == "__main__":
    SINEK_GIZLI_TOKEN = os.getenv("SINEK_TOKEN") 
    
    if not SINEK_GIZLI_TOKEN:
        print("[BİLGİ] SINEK_TOKEN bulunamadı! 'Bağımsız Modda' başlatılıyor.")
        SINEK_GIZLI_TOKEN = "KAYITSIZ_SINEK"
        
    sinek = HarcanabilirSinek(SINEK_GIZLI_TOKEN)
    sinek.kovan_icin_yasa()
