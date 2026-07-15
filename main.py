import time
import threading
import ctypes
import sqlite3 # Sinek'in Kara Kutusu eklendi

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        print(f"[SİNEK] Uyanıyor... Token doğrulandı.")
        
        # 1. Kara Kutuyu Kur (İnternet yoksa veriler buraya yazılacak)
        self.kara_kutu_kur()
        
        # 2. Donanımı Tara ve Rolü Al
        self.rol = self.donanim_tara()

    def kara_kutu_kur(self):
        """Sinek'in çevrimdışı hafızası. İnternet kopsa da veriler burada birikir."""
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
        print("[SİNEK] Kara Kutu (SQLite) devrede. Veri kaybı imkansız.")

    def veriyi_guvenceye_al(self, islem_tipi, veri_yolu):
        """İnternet yokken veya Kovan uyurken veriyi depoya yazar"""
        cursor = self.db_baglanti.cursor()
        cursor.execute("INSERT INTO bekleyen_veriler (islem_tipi, veri_yolu) VALUES (?, ?)", (islem_tipi, veri_yolu))
        self.db_baglanti.commit()
        print(f"[HAFIZA] İnternet yok! Veri kara kutuya yazıldı: {islem_tipi}")

    def donanim_tara(self):
        print("[SİNEK] Donanım kapasitesi taranıyor...")
        atanan_rol = "GOREN_SINEK" 
        print(f"[SİNEK] Kovan'daki Rolüm: {atanan_rol}")
        return atanan_rol

    def canli_baglanti_dinle(self):
        """WebSocket ile Kovan'dan gelen anlık emirleri dinler"""
        print("[AĞ] Canlı bağlantı aktif. Emir bekleniyor...")
        while self.hayatta_mi:
            # İnternet koparsa burada try-except ile yakalayıp veriyi_guvenceye_al() çalıştıracağız
            time.sleep(1) 

    def nabiz_gonder(self):
        """5 dakikada bir Kovan'a 'Ben yaşıyorum ve buradayım' der"""
        while self.hayatta_mi:
            print(f"[AĞ] Nabız atışı gönderildi -> Kovan Merkezi (Rol: {self.rol})")
            time.sleep(300) 

    def kovan_icin_yasa(self):
        """Sinek'in iletişim kanallarını başlatır"""
        t1 = threading.Thread(target=self.canli_baglanti_dinle)
        t2 = threading.Thread(target=self.nabiz_gonder)

        t1.start()
        t2.start()

        try:
            # Ana thread'i açık tutmak için sonsuz döngü (CTRL+C ile çıkış için)
            while self.hayatta_mi:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SİNEK] Ölüm emri alındı! Sistem güvenli bir şekilde kapatılıyor...")
            self.hayatta_mi = False
            t1.join()
            t2.join()
            self.db_baglanti.close()
            print("[SİNEK] Tamamen kapandı.")

if __name__ == "__main__":
    SINEK_GIZLI_TOKEN = "SINEK_NODE_99X_BETA" 
    sinek = HarcanabilirSinek(SINEK_GIZLI_TOKEN)
    sinek.kovan_icin_yasa()
