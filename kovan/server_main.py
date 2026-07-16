# kovan/server_main.py - KOVAN ANA MERKEZİ (BİRLEŞTİRİLMİŞ)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import json
from database import engine, Base
import models 

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[KOVAN BİLGİ] Veritabanı ve Kara Kutu tabloları hazır. Sistem aktif.")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, sinek_id: str):
        await websocket.accept()
        self.active_connections[sinek_id] = websocket
        print(f"[KOVAN GÜVENLİK] Sinek '{sinek_id}' bağlandı.")

    def disconnect(self, sinek_id: str):
        if sinek_id in self.active_connections:
            del self.active_connections[sinek_id]

manager = ConnectionManager()

@app.websocket("/ws/{sinek_id}")
async def websocket_endpoint(websocket: WebSocket, sinek_id: str, token: str):
    # Kapı Görevlisi
    if token == "KAYITSIZ_SINEK": # Token kontrolünü buraya oturttuk
        await manager.connect(websocket, sinek_id)
        try:
            while True:
                data = await websocket.receive_json()
                
                # [BİRLEŞTİRİLEN MANTIK] NABIZ Kontrolü
                if data.get('eylem') == "NABIZ":
                    print(f"[KOVAN] Sinek '{sinek_id}' nabzı alındı. Durum: SAĞLAM.")
                    # İleride veritabanı update'i buraya gelecek:
                    # await db.update_sinek_status(sinek_id, "AKTİF")
                else:
                    print(f"[VERİ ALINDI] Sinek {sinek_id} -> {data}")
            
        except WebSocketDisconnect:
            manager.disconnect(sinek_id)
            print(f"[KOVAN BAĞLANTI] Sinek '{sinek_id}' koptu.")
        except Exception as e:
            print(f"[KOVAN HATA] {sinek_id} veri akışı: {e}")
            manager.disconnect(sinek_id)
    else:
        print(f"[GÜVENLİK İHLALİ] Yetkisiz Sinek: {sinek_id}")
        await websocket.close(code=1008)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
