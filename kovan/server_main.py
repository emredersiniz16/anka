# kovan/server_main.py — HİBRİT KOVAN MERKEZİ v2.1 
# (FastAPI Native WebSockets + Minimalist Apple Tarzı UI & Gemini LLM Zihin)

import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os

# Yeni nesil Google GenAI SDK'sı
from google import genai
from google.genai import types

# ============================================================
# KOVAN ZİHNİ & GEMİNİ API MERKEZİ
# ============================================================
class KovanZekaMerkezi:
    def __init__(self):
        # GEMINI_API_KEY ortam değişkeninden otomatik alınır.
        self.client = genai.Client()
        self.model_name = "gemini-3.5-flash-lite" 
        
        self.sistem_promptu = (
            "Sen ANKA OS'un merkezi yapay zeka beynisin, adın Kovan'sın. "
            "Londra'daki bulut sunucusunda çalışıyorsun. "
            "Saha ekipleri (Sinekler, örn: Note 9) sana bağlı ve veri akıtıyor. "
            "Tarzın: Hacker ruhlu, cyberpunk, zeki, esprili, net ve Türkçe konuşan üst düzey bir yapay zeka asistanısın. "
            "Kullanıcıya daima 'kanka' diye hitap et, teknolojiye ve siber dünyaya hakimiyetin tam olsun."
        )

    def dusun_ve_yanitla(self, mesaj: str, kaynak="Web Paneli") -> str:
        """Kovan'ın merkezi zekasının gerçek Gemini API ile çalıştığı yer."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=mesaj,
                config=types.GenerateContentConfig(
                    system_instruction=self.sistem_promptu,
                    temperature=0.7,
                ),
            )
            return response.text
        except Exception as e:
            print(f"⚠️ [GEMINI API HATA]: {e}")
            return f"🧠 [KOVAN ACİL DURUM]: Zihne sinyal gidemedi kanka, hata: {e}"


kovan_beyin = KovanZekaMerkezi()

# Aktif bağlantıları tutan sözlük (Sinekler)
aktif_sinekler = {}

def start_kovan_zihni():
    zaman = datetime.now().strftime("%H:%M:%S")
    print(f"\n🧠 [KOVAN ZİHNİ]: Uyanıyor... ({zaman})")
    print( "🧠 [KOVAN ZİHNİ]: Ekosistem tarama başladı (Gemini Aktif).")
    print(f"🧠 [KOVAN ZİHNİ]: Bağlı sinek sayısı: {len(aktif_sinekler)}")
    print( f"💬 [SİSTEM PROMPT]: {kovan_beyin.sistem_promptu[:70]}...\n")
    return {
        "durum": "AKTİF",
        "baslangic": zaman,
        "sinek_sayisi": len(aktif_sinekler),
    }


# ============================================================
# FASTAPI UYGULAMASI (WEB PANELİ + WEBSOCKETS)
# ============================================================
app = FastAPI(title="Kovan Merkezi Zeka")

@app.on_event("startup")
async def on_startup():
    start_kovan_zihni()
    print("🌐 [SİSTEM]: Kovan 'Minimalist Zeka Modu'nda çalışıyor.")

@app.get("/", response_class=HTMLResponse)
async def web_arayuzu():
    html_icerik = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Kovan — Clean Terminal</title>
        <style>
            :root {
                --bg-color: #121214;
                --panel-bg: #18181b;
                --border-color: #27272a;
                --text-main: #f4f4f5;
                --text-muted: #a1a1aa;
                --accent: #3b82f6;
                --accent-hover: #2563eb;
                --user-bubble: #27272a;
                --kovan-bubble: #18181b;
            }
            body { 
                background-color: var(--bg-color); 
                color: var(--text-main); 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                margin: 0; 
                padding: 0; 
                display: flex; 
                flex-direction: column; 
                height: 100vh; 
            }
            header {
                padding: 15px 25px;
                border-bottom: 1px solid var(--border-color);
                background: var(--panel-bg);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            header h1 {
                font-size: 16px;
                font-weight: 600;
                margin: 0;
                letter-spacing: -0.5px;
                color: var(--text-main);
            }
            .status-badge {
                font-size: 12px;
                color: #22c55e;
                background: rgba(34, 197, 94, 0.1);
                padding: 4px 10px;
                border-radius: 20px;
                font-weight: 500;
            }
            #chat-box { 
                flex: 1; 
                overflow-y: auto; 
                padding: 20px; 
                display: flex; 
                flex-direction: column; 
                gap: 16px; 
                max-width: 800px;
                width: 100%;
                margin: 0 auto;
                box-sizing: border-box;
            }
            .message {
                padding: 12px 16px;
                border-radius: 12px;
                max-width: 85%;
                line-height: 1.5;
                font-size: 14px;
                word-wrap: break-word;
            }
            .user-msg { 
                background: var(--user-bubble); 
                color: var(--text-main); 
                align-self: flex-end; 
                border-bottom-right-radius: 4px;
            }
            .kovan-msg { 
                background: var(--kovan-bubble); 
                color: var(--text-main); 
                align-self: flex-start; 
                border: 1px solid var(--border-color);
                border-bottom-left-radius: 4px;
                white-space: pre-wrap; 
            }
            .input-container {
                padding: 20px;
                background: var(--bg-color);
                border-top: 1px solid var(--border-color);
                display: flex;
                justify-content: center;
            }
            .input-wrapper {
                max-width: 800px;
                width: 100%;
                display: flex;
                gap: 10px;
                background: var(--panel-bg);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 8px;
                box-sizing: border-box;
            }
            input { 
                flex: 1; 
                background: transparent; 
                color: var(--text-main); 
                border: none; 
                outline: none; 
                padding: 8px 12px; 
                font-size: 14px; 
                font-family: inherit;
            }
            input::placeholder { color: var(--text-muted); }
            button { 
                background: var(--accent); 
                color: white; 
                font-weight: 500; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 14px;
                transition: background 0.2s; 
            }
            button:hover { background: var(--accent-hover); }
        </style>
    </head>
    <body>
        <header>
            <h1>🧠 Kovan Merkez</h1>
            <div class="status-badge">● Sistem Aktif</div>
        </header>

        <div id="chat-box">
            <div class="message kovan-msg">Selam kanka! Londra'dan hatlar açık, zihin yerinde. Ne yapıyoruz bugün?</div>
        </div>

        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" id="mesajInput" placeholder="Kovan'a bir şeyler yaz..." onkeypress="if(event.key === 'Enter') mesajGonder()">
                <button onclick="mesajGonder()">Gönder</button>
            </div>
        </div>

        <script>
            async function mesajGonder() {
                let input = document.getElementById("mesajInput");
                let chatBox = document.getElementById("chat-box");
                let mesaj = input.value.trim();
                if(!mesaj) return;
                
                chatBox.innerHTML += `<div class="message user-msg">${mesaj}</div>`;
                input.value = "";
                chatBox.scrollTop = chatBox.scrollHeight;
                
                try {
                    let response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: mesaj})
                    });
                    let data = await response.json();
                    chatBox.innerHTML += `<div class="message kovan-msg">${data.cevap}</div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch(e) {
                    chatBox.innerHTML += `<div class="message kovan-msg" style="color: #ef4444;">Bağlantı koptu kanka!</div>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return html_icerik

class WebMesaj(BaseModel):
    text: str

@app.post("/api/chat")
async def api_chat(mesaj: WebMesaj):
    print(f"🌐 [WEB PANEL GELEN]: {mesaj.text}")
    cevap = kovan_beyin.dusun_ve_yanitla(mesaj.text, kaynak="Web Arayüzü")
    print(f"🤖 [KOVAN (GEMİNİ) CEVABI]: {cevap}")
    return {"cevap": cevap}


# ============================================================
# WEBSOCKET SUNUCUSU (Sinek / Note 9 Bağlantıları İçin)
# ============================================================
@app.websocket("/ws/{sinek_id}")
async def websocket_endpoint(websocket: WebSocket, sinek_id: str):
    await websocket.accept()
    aktif_sinekler[sinek_id] = websocket
    print(f"🔗 [KOVAN] Sinek '{sinek_id}' ağa bağlandı.")

    try:
        while True:
            mesaj = await websocket.receive_text()
            try:
                data = json.loads(mesaj)
            except json.JSONDecodeError:
                data = {"eylem": "BILINMEYEN_FORMAT", "raw": mesaj}

            if data.get('eylem') == "NABIZ":
                await websocket.send_json({"durum": "ALINDI"})
            else:
                yanit = kovan_beyin.dusun_ve_yanitla(str(data), kaynak="Sinek")
                await websocket.send_json({"merkez_yaniti": yanit})
                
    except WebSocketDisconnect:
        print(f"❌ [KOVAN] Sinek '{sinek_id}' koptu.")
        if sinek_id in aktif_sinekler:
            del aktif_sinekler[sinek_id]


if __name__ == "__main__":
    uvicorn.run("server_main:app", host="0.0.0.0", port=8001, reload=True, log_level="warning")
