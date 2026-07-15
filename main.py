import ctypes
import os

# C motorlarını yükle (Shared Object olarak derlediğimizi varsayıyoruz)
lib_audio = ctypes.CDLL('./core/engines/audio_engine.so') 

class SinekZihin:
    def __init__(self):
        print("[SİNEK] Kovan zihni uyandırılıyor...")
        # Burada HAL init fonksiyonunu çağırıp donanımı tanıyacağız
        
    def selamla(self):
        # Ses motorunu güvenli şekilde tetikle
        text = "Kovan aktif, ben Sinek."
        lib_audio.safe_speak(text.encode('utf-8'))
        print(f"[SİNEK] {text}")

if __name__ == "__main__":
    sinek = SinekZihin()
    sinek.selamla()
