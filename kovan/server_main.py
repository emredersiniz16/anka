<<<<<<< HEAD
# kovan/server_main.py — HİBRİT KOVAN MERKEZİ v2.40 (GPT API GÜNCELLEMESİ)
# (BYOK + Ücretsiz Görsel + MiroFish + Detaylı Ses Loglama)
=======
# kovan/server_main.py — HİBRİT KOVAN MERKEZİ v2.1 
# (FastAPI Native WebSockets + Minimalist Apple Tarzı UI & Gemini LLM Zihin)
>>>>>>> ac8c14708019871e1e48e8be8aa1eacf4a49a426

import json
import base64
import requests
import re
import urllib.parse
import subprocess
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
<<<<<<< HEAD
import uvicorn
import os

from openai import OpenAI

# ============================================================
# API ANAHTARLARI & AYARLAR (Yedek / Varsayılan)
# ============================================================
DEFAULT_API_KEY = "sk-o3x0C4Lg72pHi3wl3312F799E0184c6789A5Ff185a1dC5F8"
BASE_URL = "https://api.gpt.ge/v1"
ELEVENLABS_API_KEY = "sk_d61fcaf1057c0b2f00d6f9fcb9c128195df8c0737e994cdf"
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

# ============================================================
# GERÇEK MIROFISH ENGINE (SÜRÜ ZEKASI TAHMİN MOTORU)
# ============================================================
def run_mirofish_engine(query: str) -> str:
    print(f"🐟 [GERÇEK MIROFISH TETIKLENDI]: {query} için sürü analizi yapılıyor...")
    try:
        mirofish_dizini = "./MiroFish/backend" 
        komut = ["python", "main.py", "--query", query]
        
        sonuc = subprocess.run(
            komut,
            cwd=mirofish_dizini,
            capture_output=True,
            text=True,
            check=True
        )
        gercek_analiz = sonuc.stdout.strip()
        return f"**🐟 MiroFish Sürü Zekası Analizi:**\n\n{gercek_analiz}"
    except subprocess.CalledProcessError as e:
        hata_detayi = e.stderr.strip() if e.stderr else "Bilinmeyen terminal hatası."
        print(f"⚠️ [MIROFISH ÇÖKTÜ]: {hata_detayi}")
        return f"Kanka sürüyü toplarken motor patladı. Hata detayı:\n`{hata_detayi}`"
    except Exception as e:
        print(f"⚠️ [SİSTEM HATASI]: {e}")
        return f"Kanka dizin bulunamadı veya Python çalıştırılamadı: {e}"

# ============================================================
# KOVAN ZİHNİ & ÇEKİRDEK MERKEZİ
# ============================================================
class KovanZekaMerkezi:
    def __init__(self):
        # API sağlayıcının desteklediği modele göre burayı gpt-3.5-turbo veya gpt-4o olarak değiştirebilirsin.
        self.model_name = "qwen3.7-flash" 
        
        self.sistem_promptu = (
            "Sen ANKA OS'un zeki, keskin ve doğrudan sonuca giden yapay zeka asistanısın, adın Kovan. "
            "EN ÖNEMLİ KURAL: Kullanıcının sorusuna veya isteğine DOĞRUDAN, NET ve TAM ODAKLI cevap ver. Asla laf kalabalığı yapma. "
            "Karakterin: Zeki ve usta bir mühendis gibi çözüm odaklısın. Kullanıcı sana 'kanka' vb. samimi hitap ederse sen de o sıcaklığı korursun. "
            "ÖNEMLİ GÖRSEL ÇİZİM KURALI: Eğer kullanıcı resim çizmeni isterse, SADECE şu komutu döndür: "
            "[RESIM_CIZ: <buraya_detayli_ingilizce_resim_promptu_yaz>] "
            "YENİ - SÜRÜ ZEKASI (MIROFISH) KURALI: Eğer kullanıcı senden geleceğe dönük bir TAHMİN (borsa, maç sonucu, trend vb.) isterse, KESİNLİKLE kendi tahminini yapma. Sürü motorunu çalıştırmak için SADECE şu komutu döndür: "
            "[SURU_ANALIZI: <analiz_edilecek_konunun_kısa_özeti>]"
        )

    def dusun_ve_yanitla(self, mesaj_gecmisi: list, user_api_key: str = None) -> str:
        try:
            aktif_key = user_api_key.strip() if user_api_key and user_api_key.strip() else DEFAULT_API_KEY
            
            client = OpenAI(
                api_key=aktif_key,
                base_url=BASE_URL
            )

            # Sistem mesajını en başa ekliyoruz
            messages = [{"role": "system", "content": self.sistem_promptu}]
            
            # Mesaj geçmişini OpenAI formatına dönüştürüyoruz
            for item in mesaj_gecmisi:
                role = "user" if item.get("rol") == "user" else "assistant"
                
                # Resim yüklenmişse Vision formatında gönderiyoruz
                if item.get("dosya") and item["dosya"].get("base64") and item["dosya"].get("type"):
                    dosya = item["dosya"]
                    image_url = f"data:{dosya['type']};base64,{dosya['base64']}"
                    
                    content = []
                    if item.get("icerik"):
                        content.append({"type": "text", "text": item["icerik"]})
                    
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    })
                    messages.append({"role": role, "content": content})
                else:
                    # Sadece metin varsa
                    icerik = item.get("icerik", "")
                    messages.append({"role": role, "content": icerik})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            
            cevap_metni = response.choices[0].message.content

            if "[RESIM_CIZ:" in cevap_metni:
                start = cevap_metni.find("[RESIM_CIZ:") + 11
                end = cevap_metni.find("]", start)
                if end == -1: end = len(cevap_metni)
                raw_prompt = cevap_metni[start:end].strip()
                encoded_prompt = urllib.parse.quote(raw_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"
                return f"İşte istediğin görsel kanka! 🎨😎\n\n![Oluşturulan Görsel]({image_url})"

            if "[SURU_ANALIZI:" in cevap_metni:
                start = cevap_metni.find("[SURU_ANALIZI:") + 14
                end = cevap_metni.find("]", start)
                if end == -1: end = len(cevap_metni)
                analiz_konusu = cevap_metni[start:end].strip()
                return run_mirofish_engine(analiz_konusu)

            return cevap_metni

        except Exception as e:
            print(f"⚠️ [ÇEKİRDEK HATA]: {e}")
            return f"Üzgünüm kanka, zihne sinyal gidemedi, hata: {e}"

    def sesi_olustur(self, metin: str) -> str:
        print(f"🔊 [SES MOTORU TETIKLENDI]: '{metin[:30]}...' seslendiriliyor...")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": metin,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        try:
            cevap = requests.post(url, json=data, headers=headers)
            print(f"🔊 [SES MOTORU YANIT KODU]: {cevap.status_code}")
            if cevap.status_code == 200:
                print("✅ [SES BAŞARILI]: Ses verisi base64 formatına çevriliyor.")
                return base64.b64encode(cevap.content).decode('utf-8')
            else:
                print(f"⚠️ [SES API HATASI]: {cevap.text}")
                return None
        except Exception as e:
            print(f"🔥 [SES BAĞLANTI İÇİ HATA]: {e}")
            return None


kovan_beyin = KovanZekaMerkezi()
aktif_sinekler = {}

app = FastAPI(title="Kovan Merkezi Zeka")

@app.get("/", response_class=HTMLResponse)
async def web_arayuzu():
    html_icerik = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Kovan Merkez • v2.40</title>
    <style>
        :root {
            --bg: #f5f5f7;
            --panel: #ffffff;
            --border: #e5e5ea;
            --text: #1d1d1f;
            --muted: #86868b;
            --accent: #0071e3;
            --accent-hover: #0077ed;
            --user-bg: #0071e3;
            --user-text: #ffffff;
            --bot-bg: #e9e9eb;
            --bot-text: #1d1d1f;
            --radius: 16px;
        }

        [data-theme="dark"] {
            --bg: #0f0f11;
            --panel: #18181b;
            --border: rgba(255,255,255,0.1);
            --text: #f4f4f5;
            --muted: #a1a1aa;
            --accent: #3b82f6;
            --accent-hover: #60a5fa;
            --user-bg: #27272a;
            --user-text: #f4f4f5;
            --bot-bg: #18181b;
            --bot-text: #f4f4f5;
        }

        * { box-sizing: border-box; }
        html, body {
            margin: 0; padding: 0; height: 100%;
            background: var(--bg); color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
            transition: background 0.3s, color 0.3s;
        }
        body { display: flex; flex-direction: column; min-height: 100vh; }
        .shell {
            display: flex; flex-direction: column; width: 100%;
            max-width: 768px; margin: 0 auto; min-height: 100vh; padding: 0 12px;
        }
        header {
            position: sticky; top: 0; z-index: 20;
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 4px; background: var(--bg);
            backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
        }
        .title-wrap { display: flex; flex-direction: column; gap: 2px; }
        .title { margin: 0; font-size: 16px; font-weight: 600; color: var(--text); }
        .subtitle { margin: 0; color: var(--muted); font-size: 10px; }
        
        .header-actions { display: flex; gap: 6px; align-items: center; }
        .theme-btn, .clear-btn, .settings-btn {
            background: var(--panel); border: 1px solid var(--border);
            color: var(--text); padding: 5px 8px; border-radius: 8px; cursor: pointer; font-size: 11px;
        }

        .modal {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); backdrop-filter: blur(5px); z-index: 100;
            justify-content: center; align-items: center;
        }
        .modal-content {
            background: var(--panel); border: 1px solid var(--border);
            padding: 20px; border-radius: 16px; width: 90%; max-width: 400px;
            display: flex; flex-direction: column; gap: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .modal-content h3 { margin: 0 0 5px 0; font-size: 16px; color: var(--text); }
        .modal-content p { margin: 0; font-size: 12px; color: var(--muted); }
        .modal-content input {
            width: 100%; background: var(--bg); color: var(--text); border: 1px solid var(--border);
            padding: 8px 10px; border-radius: 8px; font-size: 13px; outline: none;
        }
        .modal-buttons { display: flex; gap: 6px; justify-content: flex-end; margin-top: 5px; }

        #chat-box {
            flex: 1; width: 100%; display: flex; flex-direction: column;
            gap: 12px; padding: 16px 0 140px; overflow-y: auto;
        }
        .msg {
            padding: 12px 16px; border-radius: var(--radius);
            max-width: 90%; line-height: 1.5; font-size: 14px; word-wrap: break-word;
        }
        .user-msg { background: var(--user-bg); color: var(--user-text); align-self: flex-end; border-bottom-right-radius: 4px; white-space: pre-wrap; }
        .kovan-msg { background: var(--bot-bg); border: 1px solid var(--border); color: var(--bot-text); align-self: flex-start; border-bottom-left-radius: 4px; }
        
        .kovan-msg img { max-width: 100%; border-radius: 12px; margin-top: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

        .code-container {
            position: relative; background: #0d1117; color: #c9d1d9;
            border-radius: 10px; margin: 10px 0; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);
        }
        .code-header {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22; padding: 6px 12px; font-size: 11px; color: #8b949e; border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .copy-btn {
            background: #21262d; color: #c9d1d9; border: 1px solid rgba(255,255,255,0.15);
            padding: 3px 8px; font-size: 10px; border-radius: 6px; cursor: pointer;
        }
        pre code { display: block; padding: 12px; overflow-x: auto; font-family: monospace; font-size: 13px; white-space: pre; }
        .regular-text { white-space: pre-wrap; }

        .msg-actions { margin-top: 8px; display: flex; gap: 6px; }
        .speak-btn {
            background: var(--panel); border: 1px solid var(--border); color: var(--text);
            padding: 4px 10px; font-size: 11px; border-radius: 8px; cursor: pointer; font-weight: 500;
        }

        .typing-msg {
            background: var(--bot-bg); color: var(--muted); align-self: flex-start;
            border-bottom-left-radius: 4px; display: flex; align-items: center; gap: 6px; font-style: italic; font-size: 13px;
        }
        .dot { width: 5px; height: 5px; background: var(--muted); border-radius: 50%; animation: blink 1.4s infinite both; }
        .dot:nth-child(2) { animation-delay: .2s; }
        .dot:nth-child(3) { animation-delay: .4s; }
        @keyframes blink { 0% { opacity: .2; } 20% { opacity: 1; } 100% { opacity: .2; } }

        .input-area {
            position: fixed; bottom: 0; left: 0; width: 100%;
            padding: 10px 12px 20px; background: var(--bg);
            display: flex; flex-direction: column; align-items: center; border-top: 1px solid var(--border);
        }
        .input-box-wrapper {
            width: 100%; max-width: 768px; display: flex; gap: 4px;
            background: var(--panel); border: 1px solid var(--border);
            border-radius: 14px; padding: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); align-items: center;
        }
        input[type="text"] {
            flex: 1; min-width: 0; background: transparent; color: var(--text); border: none; outline: none; font-size: 14px; font-family: inherit; padding: 4px 6px;
        }
        input::placeholder { color: var(--muted); }
        .action-btn {
            background: var(--accent); color: white; font-weight: 600; border: none;
            padding: 8px 12px; border-radius: 10px; cursor: pointer; font-size: 13px; white-space: nowrap;
        }
        .action-btn:active { transform: scale(0.96); }
        .icon-btn { background: var(--panel); color: var(--text); border: 1px solid var(--border); padding: 8px 10px; border-radius: 10px; cursor: pointer; font-size: 14px; flex-shrink: 0; }
    </style>
</head>
<body>
    <div class="shell">
        <header>
            <div class="title-wrap">
                <h1 class="title">Kovan Merkez</h1>
                <p class="subtitle">v2.40 • Ses Loglama Aktif</p>
            </div>
            <div class="header-actions">
                <button class="settings-btn" onclick="openModal()">🔑 API Key</button>
                <button class="theme-btn" onclick="toggleTheme()">🌓 Tema</button>
                <button class="clear-btn" onclick="temizleGecmis()">🗑️ Sıfırla</button>
            </div>
        </header>

        <div id="settingsModal" class="modal">
            <div class="modal-content">
                <h3>OpenAI API Anahtarı</h3>
                <p>Kotaya takılmamak için kendi OpenAI/GPT uyumlu anahtarını girebilirsin.</p>
                <input type="password" id="apiKeyInput" placeholder="sk-...">
                <div class="modal-buttons">
                    <button class="clear-btn" onclick="closeModal()">İptal</button>
                    <button class="action-btn" onclick="saveApiKey()">Kaydet</button>
                </div>
            </div>
        </div>

        <div id="chat-box"></div>

        <div class="input-area">
            <div class="input-box-wrapper">
                <input type="file" id="fileInput" style="display:none" onchange="dosyaSecildi(event)">
                <button class="icon-btn" onclick="document.getElementById('fileInput').click()" title="Dosya">📎</button>
                <input type="text" id="mesajInput" placeholder="Mesaj yaz, resim çiz veya tahmin iste..." onkeypress="if(event.key === 'Enter') mesajGonder()">
                <button class="action-btn" onclick="mesajGonder()">Gönder</button>
            </div>
        </div>
    </div>

    <script>
        function toggleTheme() {
            const current = document.documentElement.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            localStorage.setItem("kovan_theme", next);
        }
        if (localStorage.getItem("kovan_theme") === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");
        }

        function openModal() {
            document.getElementById("settingsModal").style.display = "flex";
            document.getElementById("apiKeyInput").value = localStorage.getItem("kovan_user_api_key") || "";
        }
        function closeModal() {
            document.getElementById("settingsModal").style.display = "none";
        }
        function saveApiKey() {
            let key = document.getElementById("apiKeyInput").value.trim();
            localStorage.setItem("kovan_user_api_key", key);
            closeModal();
            alert("API Anahtarı kaydedildi kanka!");
        }

        let chatHistory = JSON.parse(localStorage.getItem("kovan_history") || "[]");

        function ekranaBasGecmis() {
            const chatBox = document.getElementById("chat-box");
            if (chatHistory.length === 0) {
                chatBox.innerHTML = `<div class="msg kovan-msg">Selam kanka! v2.40 (GPT API) aktif. Ses logları terminale düşüyor. Test edelim! 🔊🐟</div>`;
                return;
            }
            chatBox.innerHTML = "";
            chatHistory.forEach(item => {
                let cls = item.rol === "user" ? "user-msg" : "kovan-msg";
                let formattedHtml = item.rol === "model" ? formatlaMesaj(item.icerik) : `<div class="regular-text">${escapeHtml(item.icerik)}</div>`;
                chatBox.innerHTML += `<div class="msg ${cls}">${formattedHtml}</div>`;
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function temizleGecmis() {
            chatHistory = [];
            localStorage.removeItem("kovan_history");
            ekranaBasGecmis();
        }

        function escapeHtml(text) {
            if (!text) return "";
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        function formatlaMesaj(text) {
            if (!text) return "";
            text = text.replace(/!\\[(.*?)\\]\\((.*?)\\)/g, '<img src="$2" alt="$1">');
            let parts = text.split(/(```[\\s\\S]*?```)/g);
            let htmlResult = "";

            parts.forEach(part => {
                if (part.startsWith("```") && part.endsWith("```")) {
                    let lines = part.slice(3, -3).trim().split("\\n");
                    let lang = lines[0].trim();
                    let codeContent = lines.slice(1).join("\\n");
                    if (!codeContent) { codeContent = lang; lang = "kod"; }
                    let uniqueId = "code-" + Math.random().toString(36).substr(2, 9);
                    htmlResult += `
                        <div class="code-container">
                            <div class="code-header">
                                <span>${escapeHtml(lang)}</span>
                                <button class="copy-btn" onclick="kopyalaKod('${uniqueId}')">Kopyala</button>
                            </div>
                            <pre><code id="${uniqueId}">${escapeHtml(codeContent)}</code></pre>
                        </div>
                    `;
                } else {
                    if (part.includes("<img")) {
                        htmlResult += part; 
                    } else {
                        let formatted = escapeHtml(part).replace(/\\n/g, "<br>");
                        htmlResult += `<div class="regular-text">${formatted}</div>`;
                    }
                }
            });
            return htmlResult;
        }

        function kopyalaKod(elementId) {
            let codeText = document.getElementById(elementId).innerText;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(codeText).then(() => {
                    let btn = event.target;
                    let eskiYazi = btn.innerText;
                    btn.innerText = "Kopyalandı! ✅";
                    setTimeout(() => { btn.innerText = eskiYazi; }, 2000);
                });
            }
        }

        ekranaBasGecmis();

        let yuklenenDosya = null;
        function dosyaSecildi(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                yuklenenDosya = {
                    name: file.name,
                    type: file.type,
                    base64: e.target.result.split(',')[1]
                };
                document.getElementById("mesajInput").placeholder = `📎 Eklendi: ${file.name}`;
            };
            reader.readAsDataURL(file);
        }

        async function mesajGonder() {
            let input = document.getElementById("mesajInput");
            let chatBox = document.getElementById("chat-box");
            let mesaj = input.value.trim();
            if(!mesaj && !yuklenenDosya) return;

            let tamMesaj = mesaj;
            if(yuklenenDosya) {
                tamMesaj += (tamMesaj ? "\\n" : "") + `[Görsel/Dosya eklendi: ${yuklenenDosya.name}]`;
            }
            
            let tempGecmis = [...chatHistory, {rol: "user", icerik: tamMesaj, dosya: yuklenenDosya}];
            let userApiKey = localStorage.getItem("kovan_user_api_key") || "";

            chatHistory.push({rol: "user", icerik: tamMesaj});
            localStorage.setItem("kovan_history", JSON.stringify(chatHistory));

            chatBox.innerHTML += `<div class="msg user-msg"><div class="regular-text">${escapeHtml(tamMesaj)}</div></div>`;
            input.value = "";
            input.placeholder = "Mesaj yaz, resim çiz veya tahmin iste...";
            chatBox.scrollTop = chatBox.scrollHeight;
            
            yuklenenDosya = null; 
            
            let typingId = "typing-" + Date.now();
            chatBox.innerHTML += `
                <div id="${typingId}" class="msg typing-msg">
                    <span>Kovan analiz ediyor ve seslendiriyor...</span><div class="dot"></div><div class="dot"></div><div class="dot"></div>
                </div>
            `;
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                let response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gecmis: tempGecmis, api_key: userApiKey})
                });
                
                if (!response.ok) throw new Error("Sunucu yanıt vermedi");
                
                let data = await response.json();
                document.getElementById(typingId).remove();
                
                chatHistory.push({rol: "model", icerik: data.cevap});
                localStorage.setItem("kovan_history", JSON.stringify(chatHistory));

                let audioHtml = "";
                let audioId = "audio-" + Date.now();
                if(data.ses_base64) {
                    let audioSrc = 'data:audio/mpeg;base64,' + data.ses_base64;
                    audioHtml = `
                        <audio id="${audioId}" src="${audioSrc}"></audio>
                        <button class="speak-btn" onclick="document.getElementById('${audioId}').play()">🔊 Dinle</button>
                    `;
                }
                
                let formattedBotMsg = formatlaMesaj(data.cevap);
                chatBox.innerHTML += `
                    <div class="msg kovan-msg">
                        <div>${formattedBotMsg}</div>
                        <div class="msg-actions">${audioHtml}</div>
                    </div>
                `;
                chatBox.scrollTop = chatBox.scrollHeight;

            } catch(e) {
                if(document.getElementById(typingId)) document.getElementById(typingId).remove();
                chatBox.innerHTML += `<div class="msg kovan-msg" style="color: #ff3b30;">Bağlantı koptu kanka! (${e.message})</div>`;
            }
        }
    </script>
</body>
</html>
"""
    return html_icerik


@app.post("/api/chat")
async def api_chat(request: dict):
    try:
        gecmis = request.get("gecmis", [])
        user_api_key = request.get("api_key", None)
        
        cevap = kovan_beyin.dusun_ve_yanitla(gecmis, user_api_key)
        
        okunacak_metin = re.sub(r'!\[.*?\]\(.*?\)', '', cevap).strip()
        ses_base64 = None
        if okunacak_metin:
            ses_base64 = kovan_beyin.sesi_olustur(okunacak_metin)
            
        return {"cevap": cevap, "ses_base64": ses_base64}
    except Exception as e:
        print(f"🔥 [API_CHAT HATA]: {e}")
        return {"cevap": f"Sunucu içi hata kanka: {e}", "ses_base64": None}

@app.websocket("/ws/{sinek_id}")
async def websocket_endpoint(websocket: WebSocket, sinek_id: str):
    await websocket.accept()
    aktif_sinekler[sinek_id] = websocket
    try:
        while True:
            mesaj = await websocket.receive_text()
            data = json.loads(mesaj)
            if data.get('eylem') == "NABIZ":
                await websocket.send_json({"durum": "ALINDI"})
            else:
                yanit = kovan_beyin.dusun_ve_yanitla([{"rol": "user", "icerik": str(data)}])
                await websocket.send_json({"merkez_yaniti": yanit})
    except WebSocketDisconnect:
        if sinek_id in aktif_sinekler:
            del aktif_sinekler[sinek_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")
=======
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
>>>>>>> ac8c14708019871e1e48e8be8aa1eacf4a49a426
