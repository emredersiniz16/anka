import asyncio
import websockets
import json

async def sinek_gonder():
    uri = "ws://127.0.0.1:8000/Sinek_01"
    async with websockets.connect(uri) as websocket:
        print("[SİNEK] Kovan'a bağlandı.")
        # NABIZ gönder
        nabiz = {"eylem": "NABIZ"}
        await websocket.send(json.dumps(nabiz))
        print("[SİNEK] Nabız gönderildi!")

asyncio.run(sinek_gonder())
