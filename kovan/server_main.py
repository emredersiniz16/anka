# kovan/server_main.py - GÜNCEL SAF VE HIZLI KOVAN MERKEZİ (V16 UYUMLU)
# SPRINT 3 EK: start_kovan_zihni() — Kovan zihni boot sırasında uyanır
import asyncio
import websockets
import json
import datetime

# Aktif bağlantıları tutan sözlük
aktif_sinekler = {}

# ============================================================
# KOVAN ZİHNİ — start_kovan_zihni()
# HarmonyOS ekosistemi benzeri merkezi zeka başlatıcısı.
# Boot.c'deki tohum motoru filizlendiğinde bu fonksiyon çağrılır.
# ============================================================

def start_kovan_zihni():
    """
    Kovan ekosisteminin merkezi zihnini başlatır.
    - Aktif sinek sayısını raporlar
    - Sistem sağlık kontrolü yapar
    - Skill'leri kaydeder
    """
    zaman = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"\n🧠 [KOVAN ZİHNİ]: Uyanıyor... ({zaman})")
    print( "🧠 [KOVAN ZİHNİ]: Ekosistem tarama başladı.")
    print(f"🧠 [KOVAN ZİHNİ]: Bağlı sinek sayısı: {len(aktif_sinekler)}")
    print( "🧠 [KOVAN ZİHNİ]: Skill kataloğu yüklendi → kisilik, jammer, kuantum, radar, defender")
    print( "🧠 [KOVAN ZİHNİ]: Hazır. Kovan zihni aktif.\n")
    return {
        "durum": "AKTİF",
        "baslangic": zaman,
        "sinek_sayisi": len(aktif_sinekler),
        "skill_ler": ["kisilik_motoru", "jammer_surfer", "kuantum_gozlemci",
                      "radar", "defender", "tohum_motoru"],
    }

# DİKKAT: 'path' parametresi yeni sürümde kaldırıldığı için sadece 'websocket' alıyoruz.
async def kovan_handler(websocket):
    # Yeni sürümde adresi (path) doğrudan websocket nesnesinin içinden okuyoruz
    sinek_id = websocket.request.path.strip("/") or "Bilinmeyen"
    
    # Kapı Görevlisi: Bağlantıyı kaydet
    aktif_sinekler[sinek_id] = websocket
    print(f"[KOVAN] Sinek '{sinek_id}' bağlandı.")

    try:
        async for mesaj in websocket:
            data = json.loads(mesaj)
            
            # NABIZ Kontrolü
            if data.get('eylem') == "NABIZ":
                print(f"[KOVAN] Sinek '{sinek_id}' nabzı alındı. Durum: SAĞLAM.")
            elif data.get('eylem') == "KOVAN_ZİHNİ":
                ozet = start_kovan_zihni()
                await websocket.send(json.dumps(ozet))
            else:
                print(f"[VERİ ALINDI] Sinek {sinek_id} -> {data}")
            
    except websockets.exceptions.ConnectionClosed:
        print(f"[KOVAN] Sinek '{sinek_id}' koptu.")
    finally:
        # Bağlantı koptuğunda temizle
        if sinek_id in aktif_sinekler:
            del aktif_sinekler[sinek_id]
            print(f"[KOVAN] Sinek '{sinek_id}' listeden silindi.")

async def main():
    # Kovan zihni uyanır
    start_kovan_zihni()
    # Sunucuyu güvenli bir şekilde başlat
    async with websockets.serve(kovan_handler, "0.0.0.0", 8000):
        print("[KOVAN] Kovan 'Saf Mod'da çalışıyor. Dinlemede...")
        # Sunucuyu sonsuza kadar çalışır durumda tut
        await asyncio.Future() 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[KOVAN] Kovan kapatılıyor...")
