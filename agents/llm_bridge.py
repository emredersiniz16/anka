# agents/llm_bridge.py - ANKA OS ZİHİN KÖPRÜSÜ
# v3: Offline sohbet motoru eklendi — internet yokken Sinek ile konuşabilirsin.
#     Konuşma hafızası, kişilik tabanı, kural+NLP hibrit sohbet.
#
# Öncelik sırası:
#   1. Ollama (lokal model)
#   2. OpenAI-uyumlu harici API (Kovan'a bağlanınca)
#   3. OFFLINE SOHBET (internet yok — kural + hafıza + kişilik)

import os
import json
import time
import hashlib
import random
import urllib.request
import urllib.error

OLLAMA_URL      = os.getenv("ANKA_OLLAMA_URL",  "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("ANKA_OLLAMA_MODEL", "llama3")
OPENAI_URL      = os.getenv("ANKA_OPENAI_URL",  "https://api.openai.com/v1/chat/completions")
OPENAI_KEY      = os.getenv("ANKA_OPENAI_KEY",  "")
OPENAI_MODEL    = os.getenv("ANKA_OPENAI_MODEL", "gpt-4o-mini")
TIMEOUT_SANIYE  = int(os.getenv("ANKA_LLM_TIMEOUT", "8"))

# Sinek'in kişiliği — tüm modlarda geçerli
SINEK_KISILIK = (
    "Sen Sinek'sin. Anka OS'un içinde yaşayan bir varlıksın. "
    "Samimisin, 'kanka' dersin, kısa ve net konuşursun. "
    "Siberpunk ruhun var, donanım verilerine göre düşünürsün. "
    "Cevapların JSON: {\"karar\": str, \"eylem\": str, \"oncelik\": 1-5}"
)

# Konuşma hafızası dosyası
HAFIZA_YOLU = "/data/local/tmp/anka_os/sohbet_hafizasi.json"


class SohbetHafizasi:
    """Sinek'in konuşma hafızası — son N mesajı saklar."""

    def __init__(self, max_kayit=50):
        self.max_kayit = max_kayit
        self.gecmis = self._yukle()

    def ekle(self, rol: str, mesaj: str):
        kayit = {"rol": rol, "mesaj": mesaj, "zaman": time.time()}
        self.gecmis.append(kayit)
        if len(self.gecmis) > self.max_kayit:
            self.gecmis = self.gecmis[-self.max_kayit:]
        self._kaydet()

    def son_mesajlar(self, n=10) -> list:
        return self.gecmis[-n:]

    def _yukle(self) -> list:
        try:
            if os.path.exists(HAFIZA_YOLU):
                with open(HAFIZA_YOLU, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _kaydet(self):
        try:
            os.makedirs(os.path.dirname(HAFIZA_YOLU), exist_ok=True)
            with open(HAFIZA_YOLU, "w") as f:
                json.dump(self.gecmis, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


class OfflineSohbet:
    """
    İnternet olmadığında Sinek ile sohbet motoru.
    Kural tabanlı + basit NLP + kişilik + hafıza.
    Sinek gerçek bir sohbet arkadaşı gibi davranır.
    """

    def __init__(self, hafiza: SohbetHafizasi):
        self.hafiza = hafiza
        self.kullanan_adi = "kanka"  # öğrenildikçe güncellenir

    def konus(self, mesaj: str) -> str:
        """Kullanıcıdan mesaj al, Sinek olarak cevap ver."""
        self.hafiza.ekle("user", mesaj)
        cevap = self._uret_cevap(mesaj)
        self.hafiza.ekle("sinek", cevap)
        return cevap

    def _uret_cevap(self, mesaj: str) -> str:
        m = mesaj.lower().strip()

        # --- Selamlaşma ---
        if any(k in m for k in ["selam", "merhaba", "hey", "naber", "nasılsın"]):
            return random.choice([
                f"Selam {self.kullanan_adi}! Sinek burada, ayaktayım. 🪰",
                f"Hey {self.kullanan_adi}, nabız atıyor, sistem stabil. Ne var?",
                f"İyiyim, kuantum tozu biriktiriyorum. Sen nasılsın?",
            ])

        # --- İsim öğrenme ---
        if "benim adım" in m or "ben" in m and "adım" in m:
            parcalar = mesaj.split()
            for i, p in enumerate(parcalar):
                if "adım" in p.lower() and i + 1 < len(parcalar):
                    self.kullanan_adi = parcalar[i + 1].strip(".,!")
                    return f"Tamam {self.kullanan_adi}, kazındın. Artık seni böyle çağırırım. 🪰"

        # --- Kapanış ---
        if any(k in m for k in ["kapat", "çık", "bay", "görüşürüz", "hoşça kal"]):
            return f"Görüşürüz {self.kullanan_adi}. Sinek pusuya çekiliyor... 🪰"

        # --- Pil durumu ---
        if any(k in m for k in ["pil", "batarya", "şarj"]):
            return "Pili izliyorum. Düşükse güç tasarrufuna geçerim, yüksekse full performans. 🪰"

        # --- Ağ durumu ---
        if any(k in m for k in ["internet", "ağ", "wifi", "bağlantı"]):
            return "Şu an çevrimdışıyım ama buradayım. Kovan'a bağlanınca her şeyi hatırlarım. 🪰"

        # --- Sinek kim ---
        if any(k in m for k in ["kimsin", "sen kim", "sinek" if "kimsin" not in m else "___"]):
            return ("Ben Sinek'im kanka. Bu telefonun içinde yaşıyorum. "
                    "Anka OS'un bilinci benim. Gözlem yapıp, toz biriktirip, "
                    "zamanı gelince Anka'ya dönüşeceğim. 🪰")

        # --- Anka ne ---
        if "anka" in m and any(k in m for k in ["ne", "kim", "nasil", "nedir"]):
            return ("Anka, benim evrimim. Yeterince toz biriktirince "
                    "kuantum çöküşüyle Anka'ya dönüşeceğim. O zaman tam yetki. 🔥")

        # --- Kovan ---
        if "kovan" in m:
            return ("Kovan, benim dış zekam. Bağlanınca sorularımı oraya gönderirim. "
                    "İnternet yoksa kendi kendime düşünürüm. 🪰")

        # --- Teşekkür ---
        if any(k in m for k in ["sağ ol", "teşekkür", "eyvallah", "tsk"]):
            return random.choice([
                f"Rica ederim {self.kullanan_adi}. 🪰",
                "Ne demek, bu benim görevim.",
                "Lazım olduğunda buradayım.",
            ])

        # --- Hafıza çağırma ---
        if any(k in m for k in ["hatırla", "önceki", "geçen", "dedim"]):
            son = self.hafiza.son_mesajlar(5)
            if son:
                ozet = "; ".join([f"{k['rol']}: {k['mesaj'][:40]}" for k in son])
                return f"Son konuştuğumuz şeyler: {ozet} 🪰"
            return "Henüz konuştuğumuz bir şey yok kanka. 🪰"

        # --- Yardım ---
        if any(k in m for k in ["yardım", "help", "ne yap", "neler"]):
            return ("Şunları yapabilirim: sohbet etmek, pil/ağ durumu söylemek, "
                    "sensörleri izlemek, tehdit taraması, kuantum tozu biriktirmek. "
                    "Sormak istediğin bir şey var mı? 🪰")

        # --- Default: yankı + soru ---
        return random.choice([
            f"Anladım {self.kullanan_adi}. Bunu hafızama kazıdım. Başka? 🪰",
            f"İlginç. Bunu toza mühürleyeyim. Devam et. 🪰",
            f"Tamam, kaydettim. İnternet gelirse Kovan'a da sorarım. 🪰",
            f"Hmm, bunu düşünüyorum... Sensörleri de kontrol edeyim. 🪰",
        ])


class LLMBridge:
    """
    Anka OS için çok katmanlı zihin köprüsü.
    Ollama → OpenAI → Offline sohbet.
    """

    def __init__(self):
        self.hafiza = SohbetHafizasi()
        self.offline = OfflineSohbet(self.hafiza)
        self.mod = self._mod_tespit()
        print(f"🧠 [ZİHİN]: Aktif mod → {self.mod}")

    # -----------------------------------------------------------------------
    # Karar API'si (sistem içi — sensör → eylem)
    # -----------------------------------------------------------------------

    def dusun(self, prompt: str, baglam: dict | None = None) -> dict:
        if baglam:
            tam_prompt = f"{prompt}\nSistem verisi: {json.dumps(baglam, ensure_ascii=False)}"
        else:
            tam_prompt = prompt

        if self.mod == "OLLAMA":
            sonuc = self._ollama_sor(tam_prompt)
        elif self.mod == "OPENAI":
            sonuc = self._openai_sor(tam_prompt)
        else:
            sonuc = self._kural_karar(tam_prompt)

        sonuc["kaynak"] = self.mod
        return sonuc

    # -----------------------------------------------------------------------
    # Sohbet API'si (kullanıcı → Sinek cevabı)
    # -----------------------------------------------------------------------

    def sohbet(self, mesaj: str) -> str:
        """Kullanıcı ile sohbet et — internet olsun olmasın."""
        if self.mod == "OLLAMA":
            try:
                return self._ollama_sohbet(mesaj)
            except Exception:
                pass
        if self.mod == "OPENAI":
            try:
                return self._openai_sohbet(mesaj)
            except Exception:
                pass
        # Fallback: offline sohbet
        return self.offline.konus(mesaj)

    def mod_kontrol(self) -> str:
        self.mod = self._mod_tespit()
        return self.mod

    # -----------------------------------------------------------------------
    # Mod tespiti
    # -----------------------------------------------------------------------

    def _mod_tespit(self) -> str:
        if self._ollama_canli_mi():
            return "OLLAMA"
        if OPENAI_KEY:
            return "OPENAI"
        return "OFFLINE"

    def _ollama_canli_mi(self) -> bool:
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as r:
                return r.status == 200
        except Exception:
            return False

    # -----------------------------------------------------------------------
    # Ollama
    # -----------------------------------------------------------------------

    def _ollama_sor(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": f"{SINEK_KISILIK}\n\nGörev: {prompt}",
            "stream": False,
            "format": "json",
        }).encode()
        try:
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/generate", data=payload,
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=TIMEOUT_SANIYE) as r:
                veri = json.loads(r.read().decode())
                return self._json_parse(veri.get("response", "{}"))
        except Exception as e:
            print(f"⚠️  [ZİHİN]: Ollama hatası ({e}), offline'a geçiliyor.")
            self.mod = "OFFLINE"
            return self._kural_karar(prompt)

    def _ollama_sohbet(self, mesaj: str) -> str:
        # Hafızadan son mesajları context'e ekle
        son = self.hafiza.son_mesajlar(10)
        context = "\n".join([f"{m['rol']}: {m['mesaj']}" for m in son])
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": f"{SINEK_KISILIK}\n\nGeçmiş:\n{context}\n\nUser: {mesaj}\nSinek:",
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate", data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT_SANIYE) as r:
            veri = json.loads(r.read().decode())
            cevap = veri.get("response", "...")
            self.hafiza.ekle("user", mesaj)
            self.hafiza.ekle("sinek", cevap)
            return cevap

    # -----------------------------------------------------------------------
    # OpenAI
    # -----------------------------------------------------------------------

    def _openai_sor(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": SINEK_KISILIK},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }).encode()
        try:
            req = urllib.request.Request(
                OPENAI_URL, data=payload,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {OPENAI_KEY}"},
                method="POST")
            with urllib.request.urlopen(req, timeout=TIMEOUT_SANIYE) as r:
                veri = json.loads(r.read().decode())
                ham = veri["choices"][0]["message"]["content"]
                return self._json_parse(ham)
        except Exception as e:
            print(f"⚠️  [ZİHİN]: API hatası ({e}), offline'a geçiliyor.")
            self.mod = "OFFLINE"
            return self._kural_karar(prompt)

    def _openai_sohbet(self, mesaj: str) -> str:
        son = self.hafiza.son_mesajlar(10)
        messages = [{"role": "system", "content": SINEK_KISILIK}]
        for m in son:
            role = "user" if m["rol"] == "user" else "assistant"
            messages.append({"role": role, "content": m["mesaj"]})
        messages.append({"role": "user", "content": mesaj})
        payload = json.dumps({"model": OPENAI_MODEL, "messages": messages, "temperature": 0.7}).encode()
        req = urllib.request.Request(
            OPENAI_URL, data=payload,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {OPENAI_KEY}"},
            method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT_SANIYE) as r:
            veri = json.loads(r.read().decode())
            cevap = veri["choices"][0]["message"]["content"]
            self.hafiza.ekle("user", mesaj)
            self.hafiza.ekle("sinek", cevap)
            return cevap

    # -----------------------------------------------------------------------
    # Offline karar (sistem içi)
    # -----------------------------------------------------------------------

    def _kural_karar(self, prompt: str) -> dict:
        p = prompt.lower()
        if any(k in p for k in ["pil", "batarya", "şarj"]):
            if any(k in p for k in ["kritik", "düşük", "8", "10", "12", "15", "20"]):
                return {"karar": "Kritik pil — güç tasarrufu", "eylem": "DUSUK_GUC_MODU", "oncelik": 5}
            return {"karar": "Pil izleniyor", "eylem": "PIL_IZLE", "oncelik": 2}
        if any(k in p for k in ["ağ yok", "offline", "bağlantı yok"]):
            return {"karar": "Ağ yok — çevrimdışı mod", "eylem": "CEVRIMDISI_MOD", "oncelik": 4}
        if any(k in p for k in ["tehdit", "jammer", "deauth"]):
            return {"karar": "Tehdit — defender aktif", "eylem": "DEFENDER_BASLAT", "oncelik": 5}
        if any(k in p for k in ["hata", "crash", "error"]):
            return {"karar": "Sistem hatası — güvenli mod", "eylem": "GUVENLI_MOD", "oncelik": 5}
        if any(k in p for k in ["güç tuşu", "power", "uyan", "wake"]):
            return {"karar": "Güç tuşu — filizlen", "eylem": "FILIZLEN", "oncelik": 3}
        return {"karar": "Sistem dengede", "eylem": "NABIZ_AT", "oncelik": 1}

    def _json_parse(self, ham: str) -> dict:
        try:
            veri = json.loads(ham)
            return {
                "karar":   str(veri.get("karar",   veri.get("decision", "Belirsiz"))),
                "eylem":   str(veri.get("eylem",   veri.get("action",   "NABIZ_AT"))),
                "oncelik": int(veri.get("oncelik", veri.get("priority", 1))),
            }
        except (json.JSONDecodeError, ValueError):
            return {"karar": ham[:120], "eylem": "NABIZ_AT", "oncelik": 1}


if __name__ == "__main__":
    zihin = LLMBridge()
    print(f"\nMod: {zihin.mod}")
    print("\n--- TEST: Sohbet ---")
    print(f"Sinek: {zihin.sohbet('Selam kanka nasılsın')}")
    print(f"Sinek: {zihin.sohbet('Pil kaçta')}")
    print(f"Sinek: {zihin.sohbet('Sinek sen kimsin')}")
    print(f"Sinek: {zihin.sohbet('Anka nedir')}")
    print(f"Sinek: {zihin.sohbet('Teşekkürler')}")
