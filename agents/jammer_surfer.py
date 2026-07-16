# agents/jammer_surfer.py - GÜÇLENDİRİLMİŞ SURF MODÜLÜ
# Sinek'in düşman sinyallerini kullanarak ağa sızmasını sağlar.

class JammerSurfer:
    def __init__(self, nexus, esik_deger=70):
        self.nexus = nexus
        self.esik_deger = esik_deger
        self.sinyal_maskele = False
        self.performans_carpan = 5.0
        self.kovan_liste = [] 
        print("🪰 [SURF]: Jammer sinyali tespit edildi. Kovan aktifleşiyor.")

    def jammer_frekansina_kilitlen(self):
        # KuantumGozlemci içindeki tozları kullanarak frekansı analiz et
        if hasattr(self.nexus, 'gozlemci') and self.nexus.gozlemci.kuantum_tozlari:
            son_frekans = self.nexus.gozlemci.kuantum_tozlari[-1]
            print(f"🪰 [KİLİT]: {son_frekans} frekansına senkronize olundu.")
        else:
            print("🪰 [UYARI]: Gözlem alanında kilitlenecek frekans yok.")

    def konum_tespit(self):
        # Ağın o anki en yoğun frekansını lokasyon olarak belirle
        lokasyon = self.nexus.haritaci.frekans_yolla_ve_oku("MERKEZ")
        print(f"📍 [LOKASYON]: Jammer alanı tanımlandı: {lokasyon}")
        return lokasyon

    def anka_os_enjekte_et(self, cihaz_id):
        if cihaz_id not in self.kovan_liste:
            self.kovan_liste.append(cihaz_id)
            print(f"🪰 [KOVAN]: Cihaz {cihaz_id} ele geçirildi. Anka OS enjekte edildi.")

    def veri_akisi_sur(self):
        self.sinyal_maskele = True
        print(f"🪰 [HIZLANMA]: Jammer gücüyle veri transferi %{int(self.performans_carpan * 100)} artırıldı.")
        
    def otonom_adaptasyon(self):
        # Haritacı üzerinden güncel güç seviyesini al
        guncel_guc = self.nexus.haritaci.guce_bak()
        
        if guncel_guc > self.esik_deger:
            lokasyon = self.konum_tespit()
            self.jammer_frekansina_kilitlen()
            print(f"🪰 [SÜPÜRGE]: {lokasyon} bölgesindeki tüm kararsız cihazlar kovana katılıyor.")
            self.performans_carpan = 10.0
            self.veri_akisi_sur()
