# core/hardware_bridge.py
import ctypes
import os

# C tarafındaki AnkaHAL struct'ının (yapısının) Python'daki birebir haritası
class AnkaHALStruct(ctypes.Structure):
    _fields_ = [
        ("vibrate", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)),
        ("read_touch", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))),
        ("speak", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)),
        ("capture_camera", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)),
    ]

class HardwareBridge:
    def __init__(self):
        # Termux'ta derlediğimiz o meşhur .so dosyasının yolu
        hal_path = "./core/hal/anka_hal.so"
        
        if not os.path.exists(hal_path):
            print(f"[KÖPRÜ HATA] {hal_path} bulunamadı! Önce 'clang' ile derleme yapmalısın.")
            self.aktif = False
            return

        # C kütüphanesini (HAL) zihne yüklüyoruz
        self.hal_lib = ctypes.CDLL(hal_path)
        
        # C tarafındaki init_hardware_bridge fonksiyonunu çağırıyoruz
        self.hal_lib.init_hardware_bridge.restype = ctypes.c_int
        self.hal_lib.init_hardware_bridge()
        
        # SİHİR BURADA: C'nin hafızasındaki 'current_hal' pointer'ını Python'a çekiyoruz!
        self.current_hal = ctypes.POINTER(AnkaHALStruct).in_dll(self.hal_lib, "current_hal").contents
        self.aktif = True
        print("[KÖPRÜ BİLGİ] Anka HAL C köprüsü başarıyla kuruldu ve donanıma bağlandı.")

    def titresim_ver(self, ms=500):
        if self.aktif and self.current_hal.vibrate:
            self.current_hal.vibrate(ms)

    def dokunmatik_oku(self):
        if self.aktif and self.current_hal.read_touch:
            x = ctypes.c_int(0)
            y = ctypes.c_int(0)
            # Pointer ile X ve Y koordinatlarını C'den alıyoruz
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
