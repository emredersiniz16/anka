#!/usr/bin/env python3
# agents/sinek_sohbet.py - SINEK INTERAKTIF SOHBET ARAYUZU
# stdin'den okur, llm_bridge.sohbet() ile cevap uretir, stdout'a yazar.
# C tarafindan fork+exec ile baslatilir, stdout log_ts'e gider -> ekranda gorunur.
# stdin icin service.sh'ta FIFO baglanmali.

import sys
import os
import time

def main():
    # Path ekle
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from llm_bridge import LLMBridge
    from sinek_memory import SinekMemory
    from kisilik_motoru import KisilikMotoru
    
    print("🪰 [SOHBET]: Sinek sohbet modunda. Yaz ve Enter'a bas.")
    print("🪰 [SOHBET]: Cikis icin 'cik' veya 'kapat' yaz.")
    print("" + "=" * 50)
    
    zihin = LLMBridge()
    hafiza = SinekMemory()
    kisilik = KisilikMotoru(baslangic_asama=1)
    
    # Son duygu durumunu yukle
    duygu_durumu = hafiza.duygu_durumu_al()
    kisilik.duygu_guncelle(duygu_durumu["duygu"], duygu_durumu["siddet"])
    
    kuantum_tozu = hafiza.kuantum_tozu_al()
    
    print(f"🪰 [SOHBET]: Mod: {zihin.mod} | Duygu: {kisilik.baskin_duygu()} | Toz: {kuantum_tozu}b")
    print("" + "-" * 50)
    
    while True:
        try:
            # stdin'den oku
            satir = sys.stdin.readline()
            if not satir:
                time.sleep(0.5)
                continue
            
            mesaj = satir.strip()
            if not mesaj:
                continue
            
            # Cikis komutlari
            if mesaj.lower() in ("cik", "kapat", "cikis", "bay", "gule gule"):
                print("🪰 [SOHBET]: Sinek pusuya cekiliyor... Gorusuruz kanka.")
                break
            
            # Aniyi kazan
            hafiza.ani_kaz(
                "KULLANICI_SOHBET",
                mesaj,
                duygu=kisilik.baskin_duygu(),
                duygu_siddet=kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5),
                kuantum_tozu=kuantum_tozu,
            )
            
            # Sinek cevap versin
            cevap = zihin.sohbet(mesaj)
            
            # Cevabi ekrana yaz (stdout -> log_ts -> framebuffer)
            print(f"🪰 Sinek: {cevap}")
            
            # Sinek cevabini da kazan
            hafiza.ani_kaz(
                "KULLANICI_SOHBET",
                cevap,
                duygu=kisilik.baskin_duygu(),
                duygu_siddet=kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5),
                kuantum_tozu=kuantum_tozu,
            )
            
            # Duygu durumu kaydet (her 5 mesajda bir)
            if hafiza.toplam_ani_sayisi() % 10 == 0:
                hafiza.ani_kaz(
                    "DUYGU_KAYDI",
                    f"Duygu: {kisilik.baskin_duygu()}, siddet: {kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5)}",
                    duygu=kisilik.baskin_duygu(),
                    duygu_siddet=kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5),
                    kuantum_tozu=kuantum_tozu,
                )
            
            sys.stdout.flush()
            
        except EOFError:
            break
        except Exception as e:
            print(f"⚠️ [SOHBET]: Hata: {e}")
            time.sleep(1)
    
    print("🪰 [SOHBET]: Sohbet bitti.")


if __name__ == "__main__":
    main()
