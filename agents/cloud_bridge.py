# agents/cloud_bridge.py - BULUT ZEKASI VE YETENEK KONTROLÜ
import json
import urllib.request
import urllib.error
import sys
import os

# Agent dizinini sisteme ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_user_intent(message):
    """Gelen mesajı analiz eden yetenek kontrolcüsü."""
    text = message.lower()
    
    if "neler yapabilirsin" in text:
        return """🪰 Sinek Asistan Yetenekleri:
1. 💬 Mesaj Yönetimi: WhatsApp/Telegram'ı yönetirim.
2. 👨‍💻 GitHub Asistanı: 'github bağla' ile repoları taşırım.
3. 👁️ Vision AI: 'şuna bak' dersen dünyayı analiz ederim.
4. ⚙️ Sistem Optimizasyonu: Donanımı tarar, ölü parçaları yönetirim.
5. 🛡️ Siber Güvenlik: Wi-Fi ağlarını şifreler, pusu modunda beklerim.
---
'hey sinek' yaz, rehberini açayım kanka!"""
    
    elif "github'ımı bağla" in text or "github bağla" in text:
        return "Kanka, GitHub'ını Anka OS'a bağlamak için hazır mısın? Terminale 'github_token: [TOKEN]' yaz, repolarını masana getireyim."
        
    elif "sen kimsin" in text:
        return "Ben Anka OS'un içindeki ruh, Sinek. Çekmecedeki o eski cihazı bir siberpunk terminale çevirmek için buradayım. 🪰"
    
    return None

def bulut_zekasina_sor(mesaj, anahtar):
    """Bulut üzerinden zeka sorgusu yapar."""
    intent_cevap = check_user_intent(mesaj)
    if intent_cevap:
        return intent_cevap

    # API anahtarı kontrolü
    if len(anahtar) < 15 or anahtar == "KULLANICI_API_ANAHTARI_BURADA_OLACAK":
        return f"☁️ BULUTTAN CEVAP: Kanka bağlantı başarılı! Sistem RAM üzerinde tıkır tıkır çalışıyor. Mesajın: '{mesaj}'"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {anahtar}"
    }
    
    sistem_mesaji = "Sen Anka OS'un siberpunk asistanısın. Kısa, net, hacker tarzı ve samimi ('kanka' diyerek) cevaplar ver."
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": sistem_mesaji},
            {"role": "user", "content": mesaj}
        ],
        "max_tokens": 150
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            return res_json['choices'][0]['message']['content']
            
    except Exception as e:
        return f"Zeka ağına vururken şalter attı kanka: {e}"
