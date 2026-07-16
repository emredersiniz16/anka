import json
import os
import sys

sys.path.append(os.getcwd())

try:
    from profile_manager import profil_kaydet
except ImportError:
    def profil_kaydet(isim, hitap):
        with open("profil.json", "w") as f:
            json.dump({"isim": isim, "hitap": hitap}, f)

def kurulum_yap():
    setup_file = "installed.flag"
    
    if os.path.exists(setup_file):
        return

    print("🚀 Anka OS: Sistem Senkronizasyonu Başlıyor...")
    print("Sinek: Selam kanka! Ben Anka OS, sistemini hızlandırmak için buradayım.")
    
    isim = input("Sinek: Seni nasıl tanıyamam? İsmin ne kanka? ").strip()
    if not isim: isim = "Dostum"
    
    print(f"Sinek: Memnun oldum {isim}! Bağlantı tercihin ne olsun?")
    tercih = input("1- Kişiselleştirilmiş yönetim, 2- Standart 'Kanka' modu: ")
    
    hitap = "isim" if tercih == "1" else "kanka"
    
    profil_kaydet(isim, hitap)
    
    with open(setup_file, "w") as f:
        f.write("OK")
        
    print(f"Sinek: Donanım ve ağ optimizasyonu tamamlandı {isim}. Artık sistemin daha akıcı.")

if __name__ == "__main__":
    kurulum_yap()
