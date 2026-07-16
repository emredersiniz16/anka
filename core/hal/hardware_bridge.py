import ctypes
import os

# C tarafındaki AnkaHAL struct'ının birebir kopyası (ABI Garantisi)
class AnkaHALStruct(ctypes.Structure):
    _fields_ = [
        ("vibrate", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)),
        ("read_touch", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))),
        ("speak", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)),
        ("capture_camera", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)),
    ]

class HardwareBridge:
    def __init__(self):
        # Makefile ile derlediğimiz ana yükleyici çekirdek (Loader)
        loader_path = "./build/anka_hal.so"
        
        if not os.path.exists(loader_path):
            print(f"[KÖPRÜ PANİK] {loader_path} bulunamadı! Önce 'make' ile çekirdeği derle.")
            self.aktif = False
            return

        # Yükleyici kütüphanesini zihne al
        self.hal_lib = ctypes.CDLL(loader_path)
        
        # Donanımı tara ve doğru sürücüyü yükle (dlopen mantığı burada tetiklenir)
        self.hal_lib.hal_loader_init()
        
        # Yüklenen aktif donanım pointer'ını (current_hal) Python'a çekiyoruz
        try:
            hal_pointer = ctypes.POINTER(AnkaHALStruct).in_dll(self.hal_lib, "current_hal")
            if not hal_pointer:
                raise ValueError("current_hal NULL döndü.")
                
            self.current_hal = hal_pointer.contents
            self.aktif = True
            print("[KÖPRÜ BİLGİ] Anka Zihni donanıma başarıyla bağlandı! Uçuşa hazır.")
        except Exception as e:
            print(f"[KÖPRÜ HATA] Donanım zihne bağlanamadı: {e}")
            self.aktif = False

    # --- ZİHNİN KASLARI (HAL FONKSİYONLARI) ---

    def titresim_ver(self, ms=500):
        if self.aktif and self.current_hal.vibrate:
            self.current_hal.vibrate(ms)

    def dokunmatik_oku(self):
        if self.aktif and self.current_hal.read_touch:
            x = ctypes.c_int(0)
            y = ctypes.c_int(0)
            self.current_hal.read_touch(ctypes.byref(x), ctypes.byref(y))
            return (x.value, y.value)
        return (0, 0)

    def konus(self, metin):
        if self.aktif and self.current_hal.speak:
            self.current_hal.speak(metin.encode('utf-8'))

    def kamera_cek(self, dosya_adi="cekim"):
        if self.aktif and self.current_hal.capture_camera:
            yol = f"./{dosya_adi}.jpg"
            self.current_hal.capture_camera(yol.encode('utf-8'))
            return yol
        return None
