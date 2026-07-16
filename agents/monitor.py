# agents/monitor.py - Sinek Sağlık Merkezi

import os
import datetime

class SinekMonitor:
    # Android/Termux'ta yazma izni olan güvenli alan
    LOG_FILE = "/data/local/tmp/sinek_nabiz.log"

    @staticmethod
    def log_critical(mesaj):
        """Kritik hataları logla ve konsola yazdır."""
        zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_satiri = f"[{zaman}] [KRİTİK]: {mesaj}\n"
        
        print(log_satiri) # Konsola da bas ki GitHub'da görebilelim
        
        try:
            # Telefon hafızasına yaz
            with open(SinekMonitor.LOG_FILE, "a") as f:
                f.write(log_satiri)
        except Exception:
            # Eğer log dosyasına yazılamıyorsa (izin vs.) en azından konsolda kalsın
            pass

    @staticmethod
    def sistem_durumu_bildir():
        """Sistemin genel sağlığını raporla."""
        return "🪰 Sinek Bilinci: Aktif ve Tetikte."
