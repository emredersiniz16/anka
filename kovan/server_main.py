# kovan/server_main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, sinek_id: str):
        await websocket.accept()
        self.active_connections[sinek_id] = websocket
        print(f"[KOVAN] Sinek {sinek_id} sisteme giriş yaptı.")

    def disconnect(self, sinek_id: str):
        if sinek_id in self.active_connections:
            del self.active_connections[sinek_id]

manager = ConnectionManager()

@app.websocket("/ws/{sinek_id}")
async def websocket_endpoint(websocket: WebSocket, sinek_id: str, token: str):
    # Token doğrulama buraya (database.py ile bağlanacak)
    await manager.connect(websocket, sinek_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"[DATA] {sinek_id} dedi ki: {data}")
    except WebSocketDisconnect:
        manager.disconnect(sinek_id)
        print(f"[KOVAN] {sinek_id} bağlantısı kesildi.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
