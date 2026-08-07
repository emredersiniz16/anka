# kovan/server_main.py — HİBRİT KOVAN MERKEZİ v3.0
# (OpenAI/qwen backend + Minimalist Apple Dark UI)

import json
import base64
import requests
import re
import urllib.parse
import subprocess
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
import uvicorn
import os

from openai import OpenAI

# ============================================================
# API ANAHTARLARI & AYARLAR
# ============================================================
DEFAULT_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-o3x0C4Lg72pHi3wl3312F799E0184c6789A5Ff185a1dC5F8")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.gpt.ge/v1")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# ============================================================
# MIROFISH ENGINE (SÜRÜ ZEKASı TAHMİN MOTORU)
# ============================================================
def run_mirofish_engine(query: str) -> str:
    print(f"🐟 [MIROFISH TETIKLENDI]: {query}")
    try:
        sonuc = subprocess.run(
            ["python", "main.py", "--query", query],
            cwd="./MiroFish/backend",
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return f"**🐟 MiroFish Sürü Zekası Analizi:**\n\n{sonuc.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        hata = e.stderr.strip() or "Bilinmeyen hata."
        return f"Sürü motoru hata verdi:\n`{hata}`"
    except Exception as e:
        return f"MiroFish çalıştırılamadı: {e}"

# ============================================================
# KOVAN ZEKASı
# ============================================================
class KovanZekaMerkezi:
    def __init__(self):
        self.model_name = "qwen3.7-flash"
        self.sistem_promptu = (
            "Sen ANKA OS'un zeki, keskin ve doğrudan sonuca giden yapay zeka asistanısın, adın Kovan. "
            "EN ÖNEMLİ KURAL: Kullanıcının sorusuna DOĞRUDAN, NET ve TAM ODAKLI cevap ver. Asla laf kalabalığı yapma. "
            "Karakterin: Çözüm odaklı, usta bir mühendis. Kullanıcı samimi hitap ederse sen de sıcak kal. "
            "GÖRSEL ÇİZİM KURALI: Resim isterlerse SADECE şunu döndür: "
            "[RESIM_CIZ: <detaylı İngilizce prompt>] "
            "SÜRÜ ZEKASı KURALI: Tahmin (borsa, maç, trend) istenirse kendi tahminini yapma, SADECE şunu döndür: "
            "[SURU_ANALIZI: <konunun kısa özeti>]"
        )

    def dusun_ve_yanitla(self, mesaj_gecmisi: list, user_api_key: str = None) -> str:
        try:
            aktif_key = (user_api_key or "").strip() or DEFAULT_API_KEY
            client = OpenAI(api_key=aktif_key, base_url=BASE_URL)

            messages = [{"role": "system", "content": self.sistem_promptu}]
            for item in mesaj_gecmisi:
                role = "user" if item.get("rol") == "user" else "assistant"
                dosya = item.get("dosya")
                if dosya and dosya.get("base64") and dosya.get("type"):
                    image_url = f"data:{dosya['type']};base64,{dosya['base64']}"
                    content = []
                    if item.get("icerik"):
                        content.append({"type": "text", "text": item["icerik"]})
                    content.append({"type": "image_url", "image_url": {"url": image_url}})
                    messages.append({"role": role, "content": content})
                else:
                    messages.append({"role": role, "content": item.get("icerik", "")})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
            )
            cevap = response.choices[0].message.content

            if "[RESIM_CIZ:" in cevap:
                start = cevap.find("[RESIM_CIZ:") + 11
                end = cevap.find("]", start)
                raw_prompt = cevap[start: end if end != -1 else len(cevap)].strip()
                encoded = urllib.parse.quote(raw_prompt)
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed=42"
                return f"İşte görsel kanka! 🎨\n\n![Oluşturulan Görsel]({url})"

            if "[SURU_ANALIZI:" in cevap:
                start = cevap.find("[SURU_ANALIZI:") + 14
                end = cevap.find("]", start)
                konu = cevap[start: end if end != -1 else len(cevap)].strip()
                return run_mirofish_engine(konu)

            return cevap

        except Exception as e:
            print(f"⚠️ [KOVAN HATA]: {e}")
            return f"Zihne sinyal gidemedi, hata: {e}"

    def sesi_olustur(self, metin: str) -> str | None:
        if not ELEVENLABS_API_KEY:
            return None
        try:
            r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
                json={
                    "text": metin,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                },
                headers={"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY},
                timeout=20,
            )
            if r.status_code == 200:
                return base64.b64encode(r.content).decode("utf-8")
        except Exception as e:
            print(f"🔥 [SES HATA]: {e}")
        return None


kovan_beyin = KovanZekaMerkezi()
aktif_sinekler: dict = {}

app = FastAPI(title="Kovan Merkezi Zeka")

# ============================================================
# WEB ARAYÜZÜ — Minimalist Apple Dark
# ============================================================
HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kovan Merkez</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg:      #121214;
  --surface: #18181b;
  --border:  #27272a;
  --text:    #f4f4f5;
  --muted:   #71717a;
  --accent:  #3b82f6;
  --accent2: #2563eb;
  --radius:  12px;
}
html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.5;
}
body { display: flex; flex-direction: column; height: 100vh; }

/* ── Header ── */
header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.brand { display: flex; flex-direction: column; gap: 2px; }
.brand-name { font-size: 15px; font-weight: 600; letter-spacing: -0.3px; }
.brand-sub  { font-size: 11px; color: var(--muted); }
.header-btns { display: flex; gap: 6px; }
.hbtn {
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 11px;
  padding: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
}
.hbtn:hover { border-color: var(--accent); }

/* ── Modal ── */
.modal-backdrop {
  display: none;
  position: fixed; inset: 0;
  background: rgba(0,0,0,.6);
  backdrop-filter: blur(4px);
  z-index: 50;
  align-items: center; justify-content: center;
}
.modal-backdrop.open { display: flex; }
.modal-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px;
  width: 90%; max-width: 380px;
  display: flex; flex-direction: column; gap: 12px;
  box-shadow: 0 16px 48px rgba(0,0,0,.5);
}
.modal-box h3 { font-size: 15px; font-weight: 600; }
.modal-box p  { font-size: 12px; color: var(--muted); }
.modal-box input {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 13px;
  padding: 8px 10px;
  border-radius: 8px;
  outline: none;
}
.modal-box input:focus { border-color: var(--accent); }
.modal-btns { display: flex; justify-content: flex-end; gap: 6px; }

/* ── Chat ── */
#chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.chat-inner {
  max-width: 760px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.msg {
  padding: 11px 15px;
  border-radius: var(--radius);
  max-width: 82%;
  word-wrap: break-word;
}
.user-msg {
  background: #27272a;
  color: var(--text);
  align-self: flex-end;
  border-bottom-right-radius: 4px;
  white-space: pre-wrap;
}
.kovan-msg {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}
.kovan-msg img {
  max-width: 100%;
  border-radius: 10px;
  margin-top: 8px;
  display: block;
}
.typing-msg {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--muted);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-style: italic;
  font-size: 13px;
}
.dot { width: 5px; height: 5px; background: var(--muted); border-radius: 50%; animation: blink 1.4s infinite both; }
.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,100% { opacity:.2; } 20% { opacity:1; } }

/* ── Code blocks ── */
.code-wrap { background:#0d1117; border:1px solid rgba(255,255,255,.08); border-radius:10px; overflow:hidden; margin:8px 0; }
.code-head { background:#161b22; display:flex; justify-content:space-between; align-items:center; padding:5px 12px; font-size:11px; color:#8b949e; }
.copy-btn { background:#21262d; color:#c9d1d9; border:1px solid rgba(255,255,255,.1); padding:3px 8px; font-size:10px; border-radius:6px; cursor:pointer; }
pre code { display:block; padding:12px; overflow-x:auto; font-family:monospace; font-size:13px; white-space:pre; color:#c9d1d9; }

/* ── Input ── */
.input-area {
  flex-shrink: 0;
  background: var(--bg);
  border-top: 1px solid var(--border);
  padding: 12px 20px 20px;
  display: flex;
  justify-content: center;
}
.input-wrap {
  max-width: 760px;
  width: 100%;
  display: flex;
  gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 6px;
  align-items: center;
}
.input-wrap:focus-within { border-color: var(--accent); }
.attach-btn { background:var(--bg); border:1px solid var(--border); color:var(--text); font-size:15px; padding:7px 9px; border-radius:8px; cursor:pointer; flex-shrink:0; }
.msg-input { flex:1; background:transparent; border:none; outline:none; color:var(--text); font-size:14px; font-family:inherit; padding:4px 6px; }
.msg-input::placeholder { color:var(--muted); }
.send-btn { background:var(--accent); color:#fff; font-weight:600; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:13px; flex-shrink:0; }
.send-btn:hover { background:var(--accent2); }
.send-btn:active { transform:scale(.96); }
.speak-btn { background:var(--bg); border:1px solid var(--border); color:var(--text); padding:4px 10px; font-size:11px; border-radius:8px; cursor:pointer; margin-top:8px; }
</style>
</head>
<body>

<header>
  <div class="brand">
    <span class="brand-name">Kovan Merkez</span>
    <span class="brand-sub">v3.0 — OpenAI/qwen</span>
  </div>
  <div class="header-btns">
    <button class="hbtn" onclick="openModal()">🔑 API Key</button>
    <button class="hbtn" onclick="clearHistory()">🗑️ Sıfırla</button>
  </div>
</header>

<div id="apiModal" class="modal-backdrop">
  <div class="modal-box">
    <h3>OpenAI API Anahtarı</h3>
    <p>Kendi GPT-uyumlu anahtarını girerek kota sınırını aşabilirsin.</p>
    <input type="password" id="apiKeyInput" placeholder="sk-...">
    <div class="modal-btns">
      <button class="hbtn" onclick="closeModal()">İptal</button>
      <button class="send-btn" onclick="saveApiKey()">Kaydet</button>
    </div>
  </div>
</div>

<div id="chat-box">
  <div class="chat-inner" id="chat-inner">
    <div class="msg kovan-msg">Selam kanka! Zihin açık, hatlar yerinde. Ne yapıyoruz? 🤙</div>
  </div>
</div>

<div class="input-area">
  <div class="input-wrap">
    <input type="file" id="fileInput" style="display:none" accept="image/*" onchange="onFileSelect(event)">
    <button class="attach-btn" title="Görsel ekle" onclick="document.getElementById('fileInput').click()">📎</button>
    <input class="msg-input" id="msgInput" type="text" placeholder="Mesaj yaz, resim çiz, tahmin iste..."
           onkeypress="if(event.key==='Enter') sendMsg()">
    <button class="send-btn" onclick="sendMsg()">Gönder</button>
  </div>
</div>

<script>
// ── utils ──
function esc(t) {
  if (!t) return "";
  return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
function formatMsg(text) {
  if (!text) return "";
  // Render markdown images
  text = text.replace(/!\\[(.*?)\\]\\((https?:\\/\\/[^\\s)]+)\\)/g, '<img src="$2" alt="$1">');
  // Split on code fences
  const parts = text.split(/(```[\\s\\S]*?```)/g);
  return parts.map(p => {
    if (p.startsWith("```") && p.endsWith("```")) {
      const inner = p.slice(3, -3).trim();
      const nlIdx = inner.indexOf("\\n");
      let lang = nlIdx !== -1 ? inner.slice(0, nlIdx).trim() : "kod";
      let code = nlIdx !== -1 ? inner.slice(nlIdx + 1) : inner;
      if (!code) { code = lang; lang = "kod"; }
      const uid = "c" + Math.random().toString(36).slice(2, 9);
      return `<div class="code-wrap"><div class="code-head"><span>${esc(lang)}</span><button class="copy-btn" onclick="copyCode('${uid}')">Kopyala</button></div><pre><code id="${uid}">${esc(code)}</code></pre></div>`;
    }
    if (p.includes("<img")) return p;
    return `<span style="white-space:pre-wrap">${esc(p)}</span>`;
  }).join("");
}
function copyCode(id) {
  const t = document.getElementById(id)?.innerText || "";
  navigator.clipboard?.writeText(t).then(() => {
    const btn = event.target;
    btn.textContent = "✅";
    setTimeout(() => btn.textContent = "Kopyala", 2000);
  });
}
function scrollBottom() {
  const cb = document.getElementById("chat-box");
  cb.scrollTop = cb.scrollHeight;
}

// ── history ──
let history = JSON.parse(localStorage.getItem("kv_hist") || "[]");
function saveHistory() { localStorage.setItem("kv_hist", JSON.stringify(history)); }
function clearHistory() {
  history = [];
  localStorage.removeItem("kv_hist");
  document.getElementById("chat-inner").innerHTML =
    '<div class="msg kovan-msg">Geçmiş silindi. Taze başlıyoruz kanka! 🧹</div>';
}

// ── modal ──
function openModal()  { document.getElementById("apiModal").classList.add("open"); document.getElementById("apiKeyInput").value = localStorage.getItem("kv_key") || ""; }
function closeModal() { document.getElementById("apiModal").classList.remove("open"); }
function saveApiKey() { localStorage.setItem("kv_key", document.getElementById("apiKeyInput").value.trim()); closeModal(); }

// ── file attach ──
let attachedFile = null;
function onFileSelect(e) {
  const f = e.target.files[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = ev => {
    attachedFile = { name: f.name, type: f.type, base64: ev.target.result.split(",")[1] };
    document.getElementById("msgInput").placeholder = `📎 ${f.name}`;
  };
  r.readAsDataURL(f);
}

// ── send ──
async function sendMsg() {
  const input = document.getElementById("msgInput");
  const ci    = document.getElementById("chat-inner");
  const text  = input.value.trim();
  if (!text && !attachedFile) return;

  const displayText = text + (attachedFile ? `\\n[📎 ${attachedFile.name}]` : "");
  const userEntry = { rol: "user", icerik: displayText, dosya: attachedFile };

  // Render user bubble
  ci.innerHTML += `<div class="msg user-msg">${esc(displayText)}</div>`;
  history.push({ rol: "user", icerik: displayText });
  saveHistory();
  input.value = "";
  input.placeholder = "Mesaj yaz, resim çiz, tahmin iste...";

  const tempGecmis = [...history.slice(-20).map(h => ({...h}))];
  if (attachedFile) tempGecmis[tempGecmis.length - 1].dosya = attachedFile;
  attachedFile = null;
  document.getElementById("fileInput").value = "";

  // Typing indicator
  const tid = "t" + Date.now();
  ci.innerHTML += `<div id="${tid}" class="msg typing-msg"><span>Kovan düşünüyor</span><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
  scrollBottom();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gecmis: tempGecmis, api_key: localStorage.getItem("kv_key") || "" }),
    });
    const data = await res.json();
    document.getElementById(tid)?.remove();

    history.push({ rol: "model", icerik: data.cevap });
    saveHistory();

    let audioHtml = "";
    if (data.ses_base64) {
      const aid = "a" + Date.now();
      audioHtml = `<audio id="${aid}" src="data:audio/mpeg;base64,${data.ses_base64}"></audio>
        <button class="speak-btn" onclick="document.getElementById('${aid}').play()">🔊 Dinle</button>`;
    }
    ci.innerHTML += `<div class="msg kovan-msg">${formatMsg(data.cevap)}${audioHtml}</div>`;
  } catch (e) {
    document.getElementById(tid)?.remove();
    ci.innerHTML += `<div class="msg kovan-msg" style="color:#ef4444;">Bağlantı hatası: ${esc(e.message)}</div>`;
  }
  scrollBottom();
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def web_arayuzu():
    return HTML


@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        body = await request.json()
        gecmis = body.get("gecmis", [])
        user_api_key = body.get("api_key", None)

        cevap = kovan_beyin.dusun_ve_yanitla(gecmis, user_api_key)

        ses_base64 = None
        okunacak = re.sub(r"!\[.*?\]\(.*?\)", "", cevap).strip()
        if okunacak:
            ses_base64 = kovan_beyin.sesi_olustur(okunacak)

        return {"cevap": cevap, "ses_base64": ses_base64}
    except Exception as e:
        print(f"🔥 [API_CHAT HATA]: {e}")
        return {"cevap": f"Sunucu hatası: {e}", "ses_base64": None}


@app.websocket("/ws/{sinek_id}")
async def websocket_endpoint(websocket: WebSocket, sinek_id: str):
    await websocket.accept()
    aktif_sinekler[sinek_id] = websocket
    print(f"🔗 Sinek '{sinek_id}' bağlandı.")
    try:
        while True:
            mesaj = await websocket.receive_text()
            try:
                data = json.loads(mesaj)
            except json.JSONDecodeError:
                data = {"eylem": "BILINMEYEN", "raw": mesaj}

            if data.get("eylem") == "NABIZ":
                await websocket.send_json({"durum": "ALINDI"})
            else:
                yanit = kovan_beyin.dusun_ve_yanitla([{"rol": "user", "icerik": str(data)}])
                await websocket.send_json({"merkez_yaniti": yanit})
    except WebSocketDisconnect:
        print(f"❌ Sinek '{sinek_id}' koptu.")
        aktif_sinekler.pop(sinek_id, None)


if __name__ == "__main__":
    uvicorn.run("server_main:app", host="0.0.0.0", port=8001, reload=True, log_level="warning")
