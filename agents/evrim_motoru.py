# agents/evrim_motoru.py - EVRİM MOTORU (Kuantum Çevirmen & Enjektör)
import subprocess
import sys
import os
import json
import hashlib
try:
    import urllib.request as _urllib_req
except ImportError:
    _urllib_req = None

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

def _ota_conf_oku(conf_yolu="/system/etc/anka_ota.conf"):
    """anka_ota.conf dosyasından yapılandırmayı okur."""
    ayarlar = {
        "ANKA_OTA_REPO": "emredersiniz16/anka",
        "ANKA_OTA_CHANNEL": "release",
        "ANKA_INSTALL_DIR": "/system/anka_core",
        "ANKA_PYTHON3": "/system/anka_core/python3/bin/python3",
    }
    if not os.path.isfile(conf_yolu):
        return ayarlar
    with open(conf_yolu, "r") as f:
        for satir in f:
            satir = satir.strip()
            if satir.startswith("#") or "=" not in satir:
                continue
            anahtar, deger = satir.split("=", 1)
            ayarlar[anahtar.strip()] = deger.strip()
    return ayarlar


def ota_github_guncelle(nexus=None):
    """
    GitHub Releases API üzerinden en son sürümü kontrol eder.
    Yeni sürüm varsa anka_core/agents/*.py dosyalarını günceller.
    """
    if _urllib_req is None:
        print("[OTA] urllib mevcut değil, güncelleme atlanıyor.")
        return False

    ayarlar = _ota_conf_oku()
    repo = ayarlar["ANKA_OTA_REPO"]
    kanal = ayarlar["ANKA_OTA_CHANNEL"]

    if kanal == "release":
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    else:
        # main branch: son commit bilgisini kontrol et
        api_url = f"https://api.github.com/repos/{repo}/commits/main"

    print(f"[OTA] Kovan kontrol ediliyor: {api_url}")
    try:
        req = _urllib_req.Request(api_url,
                                  headers={"User-Agent": "AnkaOS-OTA/1.0",
                                           "Accept": "application/vnd.github+json"})
        with _urllib_req.urlopen(req, timeout=15) as resp:
            veri = json.loads(resp.read().decode())
    except Exception as hata:
        print(f"[OTA] Kovan erişim hatası: {hata}")
        return False

    if kanal == "release":
        tag = veri.get("tag_name", "")
        assets = veri.get("assets", [])
        # ROM zip ve varsa SHA256 kontrol dosyasını bul
        zip_assets = [a for a in assets if a["name"].endswith(".zip")]
        sha256_assets = [a for a in assets if a["name"].endswith(".sha256")]
        print(f"[OTA] Mevcut sürüm etiket: {tag}")
        if not zip_assets:
            print("[OTA] Bu sürümde indirilebilecek ROM zip bulunamadı.")
            return False
        rom_url = zip_assets[0]["browser_download_url"]
        beklenen_sha256 = None
        if sha256_assets:
            try:
                req_sha = _urllib_req.Request(
                    sha256_assets[0]["browser_download_url"],
                    headers={"User-Agent": "AnkaOS-OTA/1.0"})
                with _urllib_req.urlopen(req_sha, timeout=10) as r:
                    beklenen_sha256 = r.read().decode().strip().split()[0]
            except Exception:
                beklenen_sha256 = None
    else:
        sha = veri.get("sha", "")[:8]
        print(f"[OTA] main SHA: {sha}")
        rom_url = f"https://github.com/{repo}/archive/refs/heads/main.zip"
        beklenen_sha256 = None

    # İndir
    zip_hedef = "/data/local/tmp/anka_ota_update.zip"
    print(f"[OTA] Güncelleme indiriliyor: {rom_url}")
    try:
        _urllib_req.urlretrieve(rom_url, zip_hedef)
    except Exception as hata:
        print(f"[OTA] İndirme hatası: {hata}")
        return False

    # SHA256 doğrulama
    if beklenen_sha256:
        h = hashlib.sha256()
        with open(zip_hedef, "rb") as f:
            for blok in iter(lambda: f.read(65536), b""):
                h.update(blok)
        hesaplanan = h.hexdigest()
        if hesaplanan != beklenen_sha256:
            print(f"[OTA] HATA: SHA256 uyuşmazlığı! Beklenen: {beklenen_sha256}, Hesaplanan: {hesaplanan}")
            os.remove(zip_hedef)
            return False
        print(f"[OTA] SHA256 doğrulandı: {hesaplanan}")
    else:
        print("[OTA] UYARI: SHA256 kontrol dosyası bulunamadı, doğrulama atlandı.")

    print(f"[OTA] Güncelleme indirildi: {zip_hedef}")
    print("[OTA] Kurulum için cihazı TWRP moduna alın ve şu komutu çalıştırın:")
    print(f"      twrp install {zip_hedef}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ota":
        # GitHub Releases OTA güncelleme modu
        ota_github_guncelle()
    elif len(sys.argv) > 2 and sys.argv[1] == "--payload":
        evrim_baslat(sys.argv[2])
    else:
        print("🌊 Kullanım:")
        print("  python agents/evrim_motoru.py --payload <dosya_adi>")
        print("  python agents/evrim_motoru.py --ota")
