# kovan/server_main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import json
from database import engine, Base # Veritabanı motorunu içeri aldık
import models # Tabloları tanıması için import ediyoruz

app = FastAPI()

# Kovan ilk çalıştığında veritabanı dosyalarını (SQLite) otomatik oluşturur
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Kanka bu satır sayesinde kovan_merkez.db otomatik oluşacak
        await conn.run_sync(Base.metadata.create_all)
    print("[KOVAN BİLGİ] Veritabanı ve Kara Kutu tabloları hazır. Sistem aktif.")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, sinek_id: str):
        await websocket.accept()
        self.active_connections[sinek_id] = websocket
        print(f"[KOVAN GÜVENLİK] Sinek '{sinek_id}' sisteme sızmaz bir şekilde bağlandı.")

    def disconnect(self, sinek_id: str):
        if sinek_id in self.active_connections:
            del self.active_connections[sinek_id]

manager = ConnectionManager()

@app.websocket("/ws/{sinek_id}")
async def websocket_endpoint(websocket: WebSocket, sinek_id: str, token: str):
    # Kapı Görevlisi: Token kontrolü 
    if token != "KAYITSIZ_SINEK" and token != "SENIN_GIZLI_TOKENIN":
        print(f"[GÜVENLİK İHLALİ] Yetkisiz Sinek giriş denemesi engellendi: {sinek_id}")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, sinek_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"[VERİ ALINDI] Sinek {sinek_id} -> {data}")
            # İleride burada SQLAlchemy session'ı açıp veriyi 'kara_kutu_log' tablosuna yazacağız
            
    except WebSocketDisconnect:
        manager.disconnect(sinek_id)
        print(f"[KOVAN BAĞLANTI] Sinek '{sinek_id}' koptu.")
    except Exception as e:
        print(f"[KOVAN HATA] {sinek_id} ile veri akışında sorun: {e}")
        manager.disconnect(sinek_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
