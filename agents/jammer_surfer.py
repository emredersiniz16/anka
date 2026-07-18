# agents/jammer_surfer.py - GÜÇLENDİRİLMİŞ SURF MODÜLÜ
# SPRINT 4: Radar (pasif tarama) + Defender (aktif savunma) modları eklendi.
# Mimarı:
#   • SURF/SALDIRI  — jammer sinyalini kullanarak ağa sızmak (eski)
#   • RADAR         — çevredeki ağları ve tehditleri pasif olarak taramak (yeni)
#   • DEFENDER      — tespit edilen saldırılara karşı aktif savunma (yeni)

import time

# Çalışma modları
MOD_SURF     = "SURF"
MOD_RADAR    = "RADAR"
MOD_DEFENDER = "DEFENDER"


class JammerSurfer:
    def __init__(self, nexus, esik_deger=70):
        self.nexus = nexus
        self.esik_deger = esik_deger
        self.sinyal_maskele = False
        self.performans_carpan = 5.0
        self.kovan_liste = []
        self.mod = MOD_SURF           # Varsayılan mod
        self.tehdit_listesi = []      # Radar/Defender için
        print("🪰 [SURF]: Jammer sinyali tespit edildi. Kovan aktifleşiyor.")

    # -----------------------------------------------------------------------
    # Mevcut SURF/SALDIRI işlevleri (değişmedi)
    # -----------------------------------------------------------------------

    def jammer_frekansina_kilitlen(self):
        if hasattr(self.nexus, 'gozlemci') and self.nexus.gozlemci.kuantum_tozlari:
            son_frekans = self.nexus.gozlemci.kuantum_tozlari[-1]
            print(f"🪰 [KİLİT]: {son_frekans} frekansına senkronize olundu.")
        else:
            print("🪰 [UYARI]: Gözlem alanında kilitlenecek frekans yok.")

    def konum_tespit(self):
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
        guncel_guc = self.nexus.haritaci.guce_bak()
        if guncel_guc > self.esik_deger:
            lokasyon = self.konum_tespit()
            self.jammer_frekansina_kilitlen()
            print(f"🪰 [SÜPÜRGE]: {lokasyon} bölgesindeki tüm kararsız cihazlar kovana katılıyor.")
            self.performans_carpan = 10.0
            self.veri_akisi_sur()

    # -----------------------------------------------------------------------
    # SPRINT 4 — RADAR MODU: Pasif çevre taraması
    # -----------------------------------------------------------------------

    def radar_baslat(self, tarama_suresi=5):
        """
        Çevredeki ağ trafiğini ve olası tehditleri pasif olarak dinler.
        Gerçek cihazda /proc/net veya iw tarama sonuçları kullanılır.
        Simülasyon modunda örnek tehdit verileri üretilir.
        """
        self.mod = MOD_RADAR
        print(f"\n📡 [RADAR]: Pasif tarama başlıyor ({tarama_suresi}s)...")
        self.tehdit_listesi.clear()

        # Simüle edilmiş tehdit tespiti
        sahte_tehditler = [
            {"ssid": "DEAUTH_AP_01",  "guc": -55, "tip": "DeAuth saldırısı"},
            {"ssid": "EVIL_TWIN_5G",  "guc": -72, "tip": "Kötü ikiz AP"},
            {"ssid": "PROBE_FLOOD",   "guc": -80, "tip": "Probe flood"},
        ]
        for tehdit in sahte_tehditler:
            self.tehdit_listesi.append(tehdit)
            print(f"  📡 [TESPİT]: {tehdit['ssid']} | Güç: {tehdit['guc']} dBm | Tip: {tehdit['tip']}")
            time.sleep(tarama_suresi / len(sahte_tehditler))

        print(f"📡 [RADAR]: Tarama tamamlandı. {len(self.tehdit_listesi)} tehdit bulundu.\n")
        return self.tehdit_listesi

    def radar_ozet(self):
        """Mevcut tehdit listesini özetler."""
        if not self.tehdit_listesi:
            print("📡 [RADAR]: Tehdit listesi boş. Önce radar_baslat() çalıştır.")
            return
        print(f"\n📡 [RADAR ÖZET]: {len(self.tehdit_listesi)} tehdit kayıtlı:")
        for i, t in enumerate(self.tehdit_listesi, 1):
            print(f"  [{i}] {t['ssid']} — {t['tip']}")
        print()

    # -----------------------------------------------------------------------
    # SPRINT 4 — DEFENDER MODU: Aktif savunma
    # -----------------------------------------------------------------------

    def defender_baslat(self):
        """
        Radar'ın tespit ettiği tehditlere karşı aktif savunma başlatır.
        Her tehdit türüne özel karşı-tedbir uygulanır.
        """
        self.mod = MOD_DEFENDER
        if not self.tehdit_listesi:
            print("🛡️  [DEFENDER]: Savunma için önce radar_baslat() çalıştır.")
            return

        print(f"\n🛡️  [DEFENDER]: {len(self.tehdit_listesi)} tehdide karşı savunma başlatıldı...")
        for tehdit in self.tehdit_listesi:
            self._tehdit_bertaraf_et(tehdit)
        print("🛡️  [DEFENDER]: Tüm tehditler bertaraf edildi.\n")

    def _tehdit_bertaraf_et(self, tehdit):
        """Tehdit tipine göre uygun karşı-tedbiri uygular."""
        tip = tehdit.get("tip", "")
        ssid = tehdit.get("ssid", "?")

        if "DeAuth" in tip:
            print(f"  🛡️  [ÖNLEM]: {ssid} → DeAuth paketleri engellendi (Management Frame Filter).")
        elif "Kötü ikiz" in tip:
            print(f"  🛡️  [ÖNLEM]: {ssid} → Evil-twin AP izole edildi, kullanıcılar uyarıldı.")
        elif "flood" in tip.lower():
            print(f"  🛡️  [ÖNLEM]: {ssid} → Probe flood rate-limit uygulandı.")
        else:
            print(f"  🛡️  [ÖNLEM]: {ssid} → Genel savunma tetiklendi.")
        time.sleep(0.1)

    def defender_durum(self):
        """Defender'ın aktif durumunu raporlar."""
        print(f"\n🛡️  [DEFENDER DURUM]: Mod={self.mod} | "
              f"Korunan cihaz={len(self.kovan_liste)} | "
              f"Aktif tehdit={len(self.tehdit_listesi)}\n")

    # -----------------------------------------------------------------------
    # Mod yönetimi
    # -----------------------------------------------------------------------

    def mod_degistir(self, yeni_mod):
        """SURF / RADAR / DEFENDER arasında geçiş yapar."""
        if yeni_mod not in (MOD_SURF, MOD_RADAR, MOD_DEFENDER):
            print(f"⚠️  [MOD]: Geçersiz mod: {yeni_mod}")
            return
        self.mod = yeni_mod
        print(f"🪰 [MOD]: {yeni_mod} moduna geçildi.")

