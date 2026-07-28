#!/usr/bin/env python3
# agents/sinek_sohbet.py - SINEK INTERAKTIF SOHBET ARAYUZU (v3.0 Dev Ekran Geçmişi Entegre)
# stdin yerine /data/local/tmp/anka_chat_in.txt dosyasını dinler,
# cevapları /data/local/tmp/anka_chat_display.txt dosyasına alt alta (geçmişli) yazar.

import sys
import os
import time

CHAT_IN_FILE = "/data/local/tmp/anka_chat_in.txt"
CHAT_DISPLAY_FILE = "/data/local/tmp/anka_chat_display.txt"

def ekrana_gecmis_ekle(metin: str):
    """Sinek'in veya kullanıcının mesajını dev ekran geçmişine alt alta ekler."""
    try:
        with open(CHAT_DISPLAY_FILE, "a", encoding="utf-8") as f:
            f.write(metin + "\n\n")
        os.chmod(CHAT_DISPLAY_FILE, 0o666)
    except Exception as e:
        print(f"⚠️ [EKRAN YAZMA HATASI]: {e}")

def main():
    # Path ekle
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from llm_bridge import LLMBridge
        from sinek_memory import SinekMemory
        from kisilik_motoru import KisilikMotoru
    except ImportError as e:
        print(f"⚠️ [IMPORT HATASI]: {e}")
        return
    
    print("🪰 [SOHBET]: Sinek zihni devrede ve dosya tabanlı dinlemede...")
    
    zihin = LLMBridge()
    hafiza = SinekMemory()
    kisilik = KisilikMotoru(baslangic_asama=1)
    
    # Son duygu durumunu yukle
    duygu_durumu = hafiza.duygu_durumu_al()
    kisilik.duygu_guncelle(duygu_durumu["duygu"], duygu_durumu["siddet"])
    kuantum_tozu = hafiza.kuantum_tozu_al()
    
    # Başlangıç logu
    baslangic_mesaji = f"🪰 SİNEK ZİHNİ AKTİF — Mod: {zihin.mod} | Duygu: {kisilik.baskin_duygu()} | Toz: {kuantum_tozu}b"
    print(baslangic_mesaji)
    
    # İşlenen son mesajı takip etmek için (aynı mesajı tekrar okumasın)
    islenen_mesaj = ""
    
    while True:
        try:
            # Anlık input dosyasını kontrol et (Java overlay / Bash buraya yazacak)
            if os.path.exists(CHAT_IN_FILE):
                with open(CHAT_IN_FILE, "r", encoding="utf-8") as f:
                    mesaj = f.read().strip()
                
                # Dosyayı hemen temizle ki döngüde tekrar okumasın
                if os.path.exists(CHAT_IN_FILE):
                    os.remove(CHAT_IN_FILE)
                
                if mesaj and mesaj != islenen_mesaj:
                    islenen_mesaj = mesaj
                    print(f"💬 [GELEN MESAJ]: {mesaj}")
                    
                    # Cikis komutlari
                    if mesaj.lower() in ("cik", "kapat", "cikis", "bay", "gule gule"):
                        kapanis_metni = "🪰 Sinek pusuya çekiliyor... Görüşürüz kanka."
                        ekrana_gecmis_ekle(kapanis_metni)
                        break
                    
                    # Aniyi kazan
                    hafiza.ani_kaz(
                        "KULLANICI_SOHBET",
                        mesaj,
                        duygu=kisilik.baskin_duygu(),
                        duygu_siddet=kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5),
                        kuantum_tozu=kuantum_tozu,
                    )
                    
                    # Sinek gerçek LLM / zihin motoru ile cevap versin
                    cevap = zihin.sohbet(mesaj)
                    if not cevap:
                        cevap = f"'{mesaj}' dedin kanka, frekanslar karıştlı ama buradayım!"
                    
                    # Cevabı dev ekrana alt alta yaz!
                    cevap_metni = f"🪰 SİNEK: {cevap}"
                    print(cevap_metni)
                    ekrana_gecmis_ekle(cevap_metni)
                    
                    # Sinek cevabini da hafızaya kazan
                    hafiza.ani_kaz(
                        "KULLANICI_SOHBET",
                        cevap,
                        duygu=kisilik.baskin_duygu(),
                        duygu_siddet=kisilik.duygu_durumu().get(kisilik.baskin_duygu(), 0.5),
                        kuantum_tozu=kuantum_tozu,
                    )
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"⚠️ [SOHBET DÖNGÜ HATASI]: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
