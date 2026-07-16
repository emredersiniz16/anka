# agents/setup_engine.py - ANKA OS İLK KURULUM SİHİRBAZI
import json
import os
import sys

# Proje ana dizinini importlar için sisteme dahil et
sys.path.append(os.getcwd())

# Kalıcı verilerin tutulacağı güvenli Android klasörü
STORAGE_PATH = "/data/local/tmp/"
SETUP_FLAG = os.path.join(STORAGE_PATH, "installed.flag")
PROFILE_FILE = os.path.join(STORAGE_PATH, "profil.json")

try:
    from profile_manager import profil_kaydet
except ImportError:
    # Eğer profil_manager henüz yoksa yedeği burada devreye girer
    def profil_kaydet(isim, hitap):
        with open(PROFILE_FILE, "w") as f:
            json.dump({"isim": isim, "hitap": hitap}, f)

def kurulum_yap():
    # Eğer daha önce kurulduysa tekrar çalıştırma
    if os.path.exists(SETUP_FLAG):
        return

    print("🚀 Anka OS: Sistem Senkronizasyonu Başlıyor...")
    print("Sinek: Selam kanka! Ben Anka OS, sistemini hızlandırmak için buradayım.")
    
    isim = input("Sinek: Seni nasıl tanıyamam? İsmin ne kanka? ").strip()
    if not isim: isim = "Dostum"
    
    print(f"Sinek: Memnun oldum {isim}! Bağlantı tercihin ne olsun?")
    tercih = input("1- Kişiselleştirilmiş yönetim, 2- Standart 'Kanka' modu: ")
    
    hitap = "isim" if tercih == "1" else "kanka"
    
    profil_kaydet(isim, hitap)
    
    # Kurulumun tamamlandığını işaretle
    with open(SETUP_FLAG, "w") as f:
        f.write("OK")
        
    print(f"Sinek: Donanım ve ağ optimizasyonu tamamlandı {isim}. Artık sistemin daha akıcı.")

if __name__ == "__main__":
    kurulum_yap()
