# kovan/server_main.py - SAF VE HIZLI KOVAN MERKEZİ
import asyncio
import websockets
import json

# ConnectionManager yerine saf sözlük kullanımı
aktif_sinekler = {}

async def kovan_handler(websocket, path):
    # URL'den sinek_id'yi al (ws://ip:8000/sinek_id)
    sinek_id = path.strip("/")
    
    # Kapı Görevlisi
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
        if sinek_id in aktif_sinekler:
            del aktif_sinekler[sinek_id]

# Sunucuyu başlat
start_server = websockets.serve(kovan_handler, "0.0.0.0", 8000)

print("[KOVAN] Kovan 'Saf Mod'da çalışıyor. Dinlemede...")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
