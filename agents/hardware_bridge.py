# agents/hardware_bridge.py - FİZİKSEL DÜRTME VE NEON İMPULS
# Sinek'in donanımı doğrudan tetiklediği köprü.

import os

class FizikselDurtmeMotoru:
    def __init__(self, nexus):
        self.nexus = nexus
        # Donanım titreşim dosyası (Android fiziksel yol)
        self.vibrator_path = "/sys/class/timed_output/vibrator/enable"
        self.brightness_path = "/sys/class/backlight/panel0-backlight/brightness"

    def durt(self, sure_ms=200):
        """Donanımı doğrudan dürt. OS'u bypass et."""
        try:
            if os.path.exists(self.vibrator_path):
                with open(self.vibrator_path, 'w') as f:
                    f.write(str(sure_ms))
                print("🪰 [DÜRTME]: Sinek seni fiziksel olarak dürttü.")
        except Exception as e:
            print(f"🪰 [DÜRTME]: Donanım hattı kilitli veya yetkisiz: {e}")

    def neon_patlat(self):
        """Ekran aydınlatmasını maksimuma çekip neon görseli çak."""
        try:
            if os.path.exists(self.brightness_path):
                with open(self.brightness_path, 'w') as f:
                    f.write("255") # Maksimum parlaklık
                print("🪰 [NEON]: Görsel impus tetiklendi.")
        except Exception as e:
            print(f"🪰 [NEON]: Ekran parlaklığı kontrol edilemedi: {e}")
