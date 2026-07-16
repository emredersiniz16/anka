# kovan/server_main.py - GÜNCEL SAF VE HIZLI KOVAN MERKEZİ (V16 UYUMLU)
import asyncio
import websockets
import json

# Aktif bağlantıları tutan sözlük
aktif_sinekler = {}

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
