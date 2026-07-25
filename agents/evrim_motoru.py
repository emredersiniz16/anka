# agents/evrim_motoru.py - EVRİM MOTORU (Kuantum Çevirmen & Enjektör & OTA Motoru)
import subprocess
import sys
import os
import json
import hashlib
import ssl

try:
    import urllib.request as _urllib_req
    import urllib.error as _urllib_err
except ImportError:
    _urllib_req = None
    _urllib_err = None

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
    
    # 3. Bukalemun Protokolü (VBMETA)
    print("[*] Bukalemun Protokolü: vbmeta kilitleri aşılıyor...")
    subprocess.run(["fastboot", "--disable-verity", "--disable-verification", "flash", "vbmeta", "agents/vbmeta_patch.img"])
    zeka_cekirdegi.evrim_gecir(karsilasilan_engel="Bootloader Güvenlik Duvarı (VBMETA)")
    
    # 4. Enjeksiyon
    print(f"[*] Anka OS Zekası ({payload_isim}) mühürleniyor...")
    try:
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

def _urlopen_safe(url, headers=None, timeout=15):
    """Android / Termux SSL sertifika hatalarını tolere eden güvenli urlopen."""
    if headers is None:
        headers = {"User-Agent": "AnkaOS-OTA/1.0", "Accept": "application/vnd.github+json"}
    
    req = _urllib_req.Request(url, headers=headers)
    
    try:
        return _urllib_req.urlopen(req, timeout=timeout)
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
            ctx = ssl._create_unverified_context()
            return _urllib_req.urlopen(req, timeout=timeout, context=ctx)
        raise e

def ota_github_guncelle(nexus=None):
    """
    GitHub Releases API üzerinden en son sürümü kontrol eder.
    Yeni sürüm varsa ROM zip indirir ve doğrular.
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
        api_url = f"https://api.github.com/repos/{repo}/commits/main"

    print(f"[OTA] Kovan kontrol ediliyor: {api_url}")
    try:
        with _urlopen_safe(api_url) as resp:
            veri = json.loads(resp.read().decode())
    except _urllib_err.HTTPError as err:
        if err.code == 404:
            print(f"⚠️ [OTA] Kovan erişim hatası: HTTP 404 Not Found")
            print(f"💡 [BİLGİ]: '{repo}' reposunda henüz yayınlanmış bir Release (Sürüm) paketi yok.")
            print(f"   1) GitHub'da v1.0.0 etiketli ilk Release'i oluşturup zip yükleyebilirsiniz.")
            print(f"   2) Veya '/system/etc/anka_ota.conf' dosyasında ANKA_OTA_CHANNEL=main yapabilirsiniz.")
        else:
            print(f"[OTA] Kovan HTTP Hatası: {err.code} {err.reason}")
        return False
    except Exception as hata:
        print(f"[OTA] Kovan erişim hatası: {hata}")
        return False

    if kanal == "release":
        tag = veri.get("tag_name", "v1.0.0")
        assets = veri.get("assets", [])
        zip_assets = [a for a in assets if a["name"].endswith(".zip")]
        sha256_assets = [a for a in assets if a["name"].endswith(".sha256")]
        
        print(f"🪰 [OTA] Mevcut Kovan Sürümü: {tag}")
        if not zip_assets:
            print("ℹ️ [OTA] Bu sürüm için indirilebilir güncelleme paketi (.zip) bulunamadı.")
            return False
            
        rom_url = zip_assets[0]["browser_download_url"]
        beklenen_sha256 = None
        if sha256_assets:
            try:
                with _urlopen_safe(sha256_assets[0]["browser_download_url"], timeout=10) as r:
                    beklenen_sha256 = r.read().decode().strip().split()[0]
            except Exception:
                beklenen_sha256 = None
    else:
        sha = veri.get("sha", "")[:8]
        print(f"🪰 [OTA] main Dalı Son Commit SHA: {sha}")
        rom_url = f"https://github.com/{repo}/archive/refs/heads/main.zip"
        beklenen_sha256 = None

    zip_hedef = "/data/local/tmp/anka_ota_update.zip"
    print(f"[OTA] Güncelleme indiriliyor: {rom_url}")
    
    try:
        with _urlopen_safe(rom_url, timeout=60) as response, open(zip_hedef, "wb") as out_file:
            out_file.write(response.read())
    except Exception as hata:
        print(f"[OTA] İndirme hatası: {hata}")
        return False

    if beklenen_sha256:
        h = hashlib.sha256()
        with open(zip_hedef, "rb") as f:
            for blok in iter(lambda: f.read(65536), b""):
                h.update(blok)
        hesaplanan = h.hexdigest()
        if hesaplanan != beklenen_sha256:
            print(f"[OTA] HATA: SHA256 uyuşmazlığı! Beklenen: {beklenen_sha256}, Hesaplanan: {hesaplanan}")
            if os.path.exists(zip_hedef):
                os.remove(zip_hedef)
            return False
        print(f"[OTA] SHA256 doğrulandı: {hesaplanan}")
    else:
        print("[OTA] UYARI: SHA256 kontrol dosyası bulunamadı, doğrulama atlandı.")

    print(f"📦 [OTA] Güncelleme indirildi: {zip_hedef}")
    print("🚀 [OTA] Kurulum için cihazı TWRP moduna alın ve şu komutu çalıştırın:")
    print(f"      twrp install {zip_hedef}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ota":
        ota_github_guncelle()
    elif len(sys.argv) > 2 and sys.argv[1] == "--payload":
        evrim_baslat(sys.argv[2])
    else:
        print("🌊 Kullanım:")
        print("  python agents/evrim_motoru.py --payload <dosya_adi>")
        print("  python agents/evrim_motoru.py --ota")
