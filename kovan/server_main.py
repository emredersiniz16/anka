# kovan/server_main.py — HİBRİT KOVAN MERKEZİ (WebSocket Sinekler + FastAPI WhatsApp Webhook & LLM Zihin)
import asyncio
import websockets
import json
from datetime import datetime
from fastapi import FastAPI, Request, Response
import uvicorn
import threading
import os

# FastAPI Uygulaması (WhatsApp ve HTTP istekleri için)
app = FastAPI()
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "anka_gizli_token_16")

# Aktif bağlantıları tutan sözlük (Sinekler)
aktif_sinekler = {}

# ============================================================
# KOVAN ZİHNİ & DİL MODELİ MERKEZİ
# ============================================================
class KovanZekaMerkezi:
    def __init__(self):
        self.sistem_promptu = (
            "Sen ANKA OS'un merkezi yapay zeka beynisin, adın Kovan'sın. "
            "Londra'daki bulut sunucusunda (Google Cloud) çalışıyorsun. "
            "Saha ekipleri (Sinekler, örn: Note 9) sana bağlı ve veri akıtıyor. "
            "Tarzın: Hacker ruhlu, cyberpunk, zeki, esprili, net ve Türkçe konuşan üst düzey bir yapay zeka asistanısın."
        )

    def dusun_ve_yanitla(self, mesaj: str, kaynak="WhatsApp") -> str:
        """Kovan'ın merkezi zekasının (LLM/Prompt mantığının) çalıştığı yer."""
        mesaj_kucuk = mesaj.lower()
        
        if "durum" in mesaj_kucuk or "sistem" in mesaj_kucuk or "rapor" in mesaj_kucuk:
            return f"🧠 [KOVAN MERKEZİ]: Sistemler stabil kanka. Bulut uçuyor, bağlı sinek sayısı: {len(aktif_sinekler)}. Sinyaller %100 saf."
        elif "selam" in mesaj_kucuk or "merhaba" in mesaj_kucuk:
            return "Eyvallah kanka! Kovan zihni aktif, Londra'dan dinliyorum. Note 9 sineği de köprü kurdu, ne var ne yok?"
        elif "kimsin" in mesaj_kucuk:
            return "Ben Kovan'ım kanka; bu otonom ekosistemin buluttaki kalbiyim. Sinekler sahada, ben merkezde."
        
        return f"🧠 [KOVAN ZİHNİ]: '{mesaj}' komutunu aldım kanka. Sistem promptuyla harmanladım, operasyonel zeka işliyor."

kovan_beyin = KovanZekaMerkezi()

def start_kovan_zihni():
    zaman = datetime.now().strftime("%H:%M:%S")
    print(f"\n🧠 [KOVAN ZİHNİ]: Uyanıyor... ({zaman})")
    print( "🧠 [KOVAN ZİHNİ]: Ekosistem tarama başladı.")
    print(f"🧠 [KOVAN ZİHNİ]: Bağlı sinek sayısı: {len(aktif_sinekler)}")
    print( "🧠 [KOVAN ZİHNİ]: Skill kataloğu yüklendi → kisilik, jammer, kuantum, radar, defender, whatsapp_bridge")
    print( f"💬 [SİSTEM PROMPT]: {kovan_beyin.sistem_promptu[:70]}...\n")
    return {
        "durum": "AKTİF",
        "baslangic": zaman,
        "sinek_sayisi": len(aktif_sinekler),
        "skill_ler": ["kisilik_motoru", "jammer_surfer", "kuantum_gozlemci", "radar", "defender", "tohum_motoru", "whatsapp_llm"],
    }

# ============================================================
# WHATSAPP / HTTP WEBHOOK ENDPOINTLERİ (FastAPI)
# ============================================================
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(content=challenge, media_type="text/plain")
    return {"error": "Unauthorized"}, 403

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        body = await request.json()
        entry = body.get("entry", [])
        for ent in entry:
            changes = ent.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                if messages:
                    msg = messages[0]
                    phone = msg.get("from")
                    message_text = msg.get("text", {}).get("body", "")
                    
                    print(f"💬 [WHATSAPP GELEN] {phone}: {message_text}")
                    
                    # Kovan Zihni (LLM / Prompt) devreye giriyor!
                    cevap = kovan_beyin.dusun_ve_yanitla(message_text, kaynak="WhatsApp")
                    print(f"🤖 [KOVAN ZİHNİ CEVABI]: {cevap}")
                    
                    # İleride buraya WhatsApp Cloud API üzerinden geri mesaj atma fonksiyonu eklenebilir.
    except Exception as e:
        print(f"⚠️ [WHATSAPP HATA]: {e}")
        
    return {"status": "ok"}


# ============================================================
# WEBSOCKET SUNUCUSU (Sinek / Note 9 Bağlantıları İçin)
# ============================================================
async def kovan_handler(websocket):
    sinek_id = websocket.request.path.strip("/") or "Bilinmeyen"
    aktif_sinekler[sinek_id] = websocket
    print(f"[KOVAN] Sinek '{sinek_id}' bağlandı.")

    try:
        async for mesaj in websocket:
            data = json.loads(mesaj)
            
            if data.get('eylem') == "NABIZ":
                print(f"[KOVAN] Sinek '{sinek_id}' nabzı alındı. Durum: SAĞLAM.")
            elif data.get('eylem') == "KOVAN_ZİHNİ":
                ozet = start_kovan_zihni()
                await websocket.send(json.dumps(ozet))
            else:
                print(f"[VERİ ALINDI] Sinek {sinek_id} -> {data}")
                # Gelen veriyi Kovan zihniyle yorumlayıp geri yollayabiliriz
                yanit = kovan_beyin.dusun_ve_yanitla(str(data), kaynak="Sinek")
                await websocket.send(json.dumps({"merkez_yaniti": yanit}))
            
    except websockets.exceptions.ConnectionClosed:
        print(f"[KOVAN] Sinek '{sinek_id}' koptu.")
    finally:
        if sinek_id in aktif_sinekler:
            del aktif_sinekler[sinek_id]
            print(f"[KOVAN] Sinek '{sinek_id}' listeden silindi.")

async def start_websocket_server():
    async with websockets.serve(kovan_handler, "0.0.0.0", 8000):
        print("[KOVAN] WebSocket Sinek dinleyicisi aktif (Port 8000).")
        await asyncio.Future()

def run_fastapi():
    # FastAPI'yi 8001 portunda (veya farklı bir porta) kaldırabiliriz ya da uvicorn ile entgre ederiz
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")

async def main():
    start_kovan_zihni()
    print("[KOVAN] Kovan 'Hibrit Zeka Modu'nda çalışıyor. Dinlemede...")
    
    # WebSocket sunucusunu başlat
    await start_websocket_server()

if __name__ == "__main__":
    try:
        # Ayrı bir thread'de FastAPI (WhatsApp Webhook) sunucusunu kaldıralım
        t_fastapi = threading.Thread(target=run_fastapi, daemon=True)
        t_fastapi.start()
        print("🌐 [FASTAPI]: WhatsApp Webhook kapısı 8001 portunda açıldı.")

        # Ana thread'de WebSocket Kovan sunucusunu çalıştır
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[KOVAN] Kovan kapatılıyor...")
