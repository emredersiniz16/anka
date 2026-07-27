#!/usr/bin/env python3
# agents/sinek_sohbet.py - SINEK INTERAKTIF SOHBET ARAYUZU (v2.1 Ekran Entegre)
# stdin'den okur, llm_bridge.sohbet() ile cevap üretir, hem stdout'a hem de
# Java Overlay'in okuduğu anlık /data/local/tmp/anka_state.txt dosyasına yazar.

import sys
import os
import time

STATE_FILE = "/data/local/tmp/anka_state.txt"
TMP_STATE_FILE = "/data/local/tmp/anka_state.tmp"

def ekrana_fırlat(dusunce_metni: str):
    """Sinek'in verdiği cevabı anında Note 9 ekranındaki yeşil kutuya yansıtır."""
    try:
        time_str, battery, dust, mode = "--:--", "--", "6181", "SİNEK SOHBET"
        
        # Ekrandaki mevcut saat, pil ve toz değerlerini koru
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                for line in f:
                    if line.startswith("TIME:"): time_str = line.split(":", 1)[1].strip()
                    elif line.startswith("BATTERY:"): battery = line.split(":", 1)[1].strip()
                    elif line.startswith("DUST:"): dust = line.split(":", 1)[1].strip()
                    elif line.startswith("MODE:"): mode = line.split(":", 1)[1].strip()

        # Atomik yazma ile çökmesiz güncelleme
        with open(TMP_STATE_FILE, "w") as f:
            f.write(f"TIME: {time_str}\n")
            f.write(f"BATTERY: {battery}\n")
            f.write(f"DUST: {dust}\n")
            f.write(f"MODE: {mode}\n")
            f.write(f"THOUGHT: {dusunce_metni}\n")
            f.write(f"TICK: 999\n")
            
        os.rename(TMP_STATE_FILE, STATE_FILE)
    except Exception as e:
        print(f"⚠️ [EKRAN YAZMA HATASI]: {e}")

def main():
    # Path ekle
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from llm_bridge import LLMBridge
    from sinek_memory import SinekMemory
    from kisilik_motoru import KisilikMotoru
    
    print("🪰 [SOHBET]: Sinek sohbet modunda. Yaz ve Enter'a bas.")
    print("🪰 [SOHBET]: Cikis icin 'cik' veya 'kapat' yaz.")
    print("=" * 50)
    
    zihin = LLMBridge()
    hafiza = SinekMemory()
    kisilik = KisilikMotoru(baslangic_asama=1)
    
    # Son duygu durumunu yukle
    duygu_durumu = hafiza.duygu_durumu_al()
    kisilik.duygu_guncelle(duygu_durumu["duygu"], duygu_durumu["siddet"])
    
    kuantum_tozu = hafiza.kuantum_tozu_al()
    
    bilgi_metni = f"🪰 Mod: {zihin.mod} | Duygu: {kisilik.baskin_duygu()} | Toz: {kuantum_tozu}b"
    print(bilgi_metni)
    ekrana_fırlat(bilgi_metni)
    print("-" * 50)
    
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
                kapanis_metni = "🪰 Sinek pusuya çekiliyor... Görüşürüz kanka."
                print(kapanis_metni)
                ekrana_fırlat(kapanis_metni)
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
            
            # Cevabi hem stdout'a hem de TELEFON EKRANINA yaz!
            cevap_metni = f"💬 Sinek: {cevap}"
            print(f"🪰 Sinek: {cevap}")
            ekrana_fırlat(cevap_metni)
            
            # Sinek cevabini da kazan
            hafiza.ani_kaz(
                "KULLANICI_SOHBET",
                cevap,
                duygu=kisilik.baskin_duygu(),
                duygu_siddet=kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5),
                kuantum_tozu=kuantum_tozu,
            )
            
            # Duygu durumu kaydet (her 10 anıda bir)
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
