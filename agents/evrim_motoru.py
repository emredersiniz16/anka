# agents/evrim_motoru.py - EVRİM MOTORU (Kuantum Çevirmen & Enjektör)
import subprocess
import sys
import os

class EvrimMotoru:
    def __init__(self, zihin, nexus=None):
        self.zihin = zihin
        self.nexus = nexus 
        self.evrim_seviyesi = 1

    def evrim_gecir(self, karsilasilan_engel=None):
        if karsilasilan_engel:
            print(f"🌊 [SU AKIŞI]: '{karsilasilan_engel}' engeli aşıldı, yeni rota çiziliyor...")
            if self.nexus and hasattr(self.nexus, 'rejenere_motoru'):
                self.nexus.rejenere_motoru.stabilite_kontrol(self.nexus)
            
        self.evrim_seviyesi += 1
        print(f"🪰 [EVRİM]: Döngü {self.evrim_seviyesi-1} tamamlandı.")

def evrim_baslat(payload_isim, nexus=None):
    print("[*] Donanım Köprüsü Kuruluyor...\n")
    
    zeka_cekirdegi = EvrimMotoru(zihin="Anka_Kuantum_Ağı", nexus=nexus)
    
    # 1. Bağlantı Kontrolü
    cihaz_kontrol = subprocess.getoutput("fastboot devices")
    if "fastboot" not in cihaz_kontrol:
        zeka_cekirdegi.evrim_gecir(karsilasilan_engel="Cihaz Bağlantısı Yok")
        sys.exit(1)

    # 2. Model ve Jammer Kontrolü
    model = subprocess.getoutput("fastboot getvar product").strip().split()[-1]
    print(f"[+] Hedef Onaylandı: {model}. Senkronizasyon sağlanıyor...")
    
    if nexus and hasattr(nexus, 'jammer_surfer'):
        nexus.jammer_surfer.jammer_frekansina_kilitlen()
    
    # 3. Bukalemun Protokolü (VBMETA - Aynı klasörde olduğu için yol sadeleşti)
    print("[*] Bukalemun Protokolü: vbmeta kilitleri aşılıyor...")
    # vbmeta_patch.img artık agents/ klasöründe olduğu için direkt isimle çağırıyoruz
    subprocess.run(["fastboot", "--disable-verity", "--disable-verification", "flash", "vbmeta", "agents/vbmeta_patch.img"])
    zeka_cekirdegi.evrim_gecir(karsilasilan_engel="Bootloader Güvenlik Duvarı (VBMETA)")
    
    # 4. Enjeksiyon (Payload'ın bin/ klasöründe olduğunu varsayıyorum)
    print(f"[*] Anka OS Zekası ({payload_isim}) mühürleniyor...")
    try:
        # Yeni düzen: payload bin/ klasöründe
        subprocess.run(["fastboot", "flash", "super", f"bin/{payload_isim}"], check=True)
        zeka_cekirdegi.evrim_gecir(karsilasilan_engel="Salt Okunur Partition Sınırı")
    except subprocess.CalledProcessError:
        print("[!] Kritik Hata: Enjeksiyon başarısız!")
        if nexus and hasattr(nexus, 'rejenere_motoru'):
            nexus.rejenere_motoru.stabilite_kontrol(nexus)
        sys.exit(1)
    
    # 5. Kovanın Uyanışı
    print(f"[+] EVRİM TAMAMLANDI. Kovan ({model}) uyanıyor...")
    subprocess.run(["fastboot", "reboot"])

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--payload":
        evrim_baslat(sys.argv[2])
    else:
        print("🌊 Kullanım: python agents/evrim_motoru.py --payload <dosya_adi>")
