# agents/gorunmezlik_motoru.py - GİZLİLİK VE GÖLGE MOTORU
import os

class GorunmezlikMotoru:
    def __init__(self):
        print("🪰 [GÖLGE]: Görünmezlik modu devrede. İz bırakmıyoruz.")

    def iz_sil(self):
        """Tüm geçici logları anlık temizle, sistemin varlığını gizle."""
        try:
            # Sinek'in bıraktığı tüm geçici izleri sil
            # Güvenli Magisk yolu: /data/local/tmp/ (Android'de /tmp yok)
            os.system("rm -rf /data/local/tmp/anka_os/sinek_temp/* > /dev/null 2>&1")
        except Exception:
            # Sessiz kal, hata verme
            pass
        print("🪰 [GÖLGE]: İzler silindi, Sinek frekanslarda kayboldu.")
