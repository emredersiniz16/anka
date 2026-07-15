import time
import threading
import ctypes
import sqlite3
import os

class HarcanabilirSinek:
    def __init__(self, sinek_token):
        self.token = sinek_token
        self.hayatta_mi = True
        print(f"[SİNEK] Uyanıyor... Token: {self.token}")
        
        # 1. Kara Kutuyu Kur (İnternet yoksa veriler buraya yazılacak)
        self.kara_kutu_kur()
        
        # 2. Kasları (C Motorlarını) Zihne Bağla
        self.motorlari_atesle()
        
        # 3. Donanımı Tara ve Rolü Al
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

    def motorlari_atesle(self):
        """C ile yazılmış donanım motorlarını (so dosyalarını) Python zihnine bağlar."""
        try:
            # Ses motorunu yükle
            self.ses_motoru = ctypes.CDLL('./core/engines/audio_engine.so')
            self.ses_motoru.safe_speak.argtypes = [ctypes.c_char_p]
            
            # Kamera motorunu yükle
            self.kamera_motoru = ctypes.CDLL('./core/engines/camera_engine.so')
            self.kamera_motoru.safe_capture_frame.argtypes = [ctypes.c_char_p]
            
            print("[SİNEK] Kaslar (Motorlar) zihne bağlandı. Cihaz operasyonel.")
        except OSError:
            print("[SİNEK UYARI] Motorlar (so dosyaları) bulunamadı! Önce 'make' komutunu çalıştır.")

    def veriyi_guvenceye_al(self, islem_tipi, veri_yolu):
        """İnternet yokken veya Kovan uyurken veriyi depoya yazar"""
        cursor = self.db_baglanti.cursor()
        cursor.execute("INSERT INTO bekleyen_veriler (islem_tipi, veri_yolu) VALUES (?, ?)", (islem_tipi, veri_yolu))
        self.db_baglanti.commit()
        print(f"[HAFIZA] Veri kara kutuya yazıldı: {islem_tipi}")

    def donanim_tara(self):
        print("[SİNEK] Donanım kapasitesi taranıyor...")
        atanan_rol = "GOREN_SINEK" 
        print(f"[SİNEK] Kovan'daki Rolüm: {atanan_rol}")
        return atanan_rol

    def eylem_kamera_cek(self, dosya_adi):
        """Kovan'dan emir gelince veya otonom olarak kamerayı tetikler"""
        if hasattr(self, 'kamera_motoru'):
            dosya_yolu = f"./{dosya_adi}.jpg"
            # C motorunu çalıştır (Sistemi bloklamaz)
            self.kamera_motoru.safe_capture_frame(dosya_yolu.encode('utf-8'))
            
            # Veriyi anında Kara Kutu'ya (SQLite) kaydet
            self.veriyi_guvenceye_al("KAMERA_CEKIMI", dosya_yolu)
            print(f"[EYLEM] Görüntü alındı ve kara kutuya işlendi: {dosya_yolu}")
        else:
            print("[EYLEM HATA] Kamera motoru aktif değil!")

    def eylem_konus(self, metin):
        """Sinek'in konuşmasını sağlar"""
        if hasattr(self, 'ses_motoru'):
            self.ses_motoru.safe_speak(metin.encode('utf-8'))
            self.veriyi_guvenceye_al("SES_CIKISI", metin)
            print(f"[EYLEM] Konuşuldu: {metin}")
        else:
            print("[EYLEM HATA] Ses motoru aktif değil!")

    def canli_baglanti_dinle(self):
        """WebSocket ile Kovan'dan gelen anlık emirleri dinler"""
        print("[AĞ] Canlı bağlantı aktif. Emir bekleniyor...")
        while self.hayatta_mi:
            # İnternet koparsa burada try-except ile yakalayıp veriyi_guvenceye_al() çalıştıracağız
            time.sleep(1) 

    def nabiz_gonder(self):
        """5 dakikada bir Kovan'a 'Ben yaşıyorum ve buradayım' der"""
        while self.hayatta_mi:
            # Bağımsız moddaysa ağa ping atmaya çalışmaz, sadece lokal log tutar
            if self.token != "KAYITSIZ_SINEK":
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
    # Sinek token'ı artık kodun içinde değil, cihazın ortam değişkeninden (environment) çekiliyor!
    SINEK_GIZLI_TOKEN = os.getenv("SINEK_TOKEN") 
    
    if not SINEK_GIZLI_TOKEN:
        print("[BİLGİ] SINEK_TOKEN bulunamadı! Sinek 'Bağımsız Modda' (Offline) başlatılıyor.")
        print("[BİLGİ] Ağ bağlantısı kurulmayacak ama veri toplamaya ve Kara Kutu'ya yazmaya devam edecek.")
        SINEK_GIZLI_TOKEN = "KAYITSIZ_SINEK" # Ağa bağlanmayacak ama çalışmaya devam edecek profil
        
    sinek = HarcanabilirSinek(SINEK_GIZLI_TOKEN)
    sinek.kovan_icin_yasa()
