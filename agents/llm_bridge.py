# agents/llm_bridge.py - ANKA OS ZİHİN KÖPRÜSÜ
#
# Anka'nın "düşünme" katmanı.
# Öncelik sırası:
#   1. Ollama (lokal model — Termux/Android'de llama.cpp üzerinde çalışır)
#   2. OpenAI-uyumlu harici API (opsiyonel, .env'den alınır)
#   3. Kural tabanlı geri dönüş (offline / hiç model yoksa)
#
# Kullanım:
#   from llm_bridge import LLMBridge
#   beyin = LLMBridge()
#   yanit = beyin.dusun("Pil %12, ağ yok. Ne yapmalıyım?")

import os
import json
import urllib.request
import urllib.error

# --- YAPILANDIRMA ---
OLLAMA_URL      = os.getenv("ANKA_OLLAMA_URL",  "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("ANKA_OLLAMA_MODEL", "llama3")          # Termux'ta 'llama3' veya 'phi3'
OPENAI_URL      = os.getenv("ANKA_OPENAI_URL",  "https://api.openai.com/v1/chat/completions")
OPENAI_KEY      = os.getenv("ANKA_OPENAI_KEY",  "")                 # Boşsa kullanılmaz
OPENAI_MODEL    = os.getenv("ANKA_OPENAI_MODEL", "gpt-4o-mini")
TIMEOUT_SANIYE  = int(os.getenv("ANKA_LLM_TIMEOUT", "8"))

# Anka'nın sistem kişiliği — tüm isteklere eklenir
ANKA_SISTEM_KIMLIK = (
    "Sen Anka OS'un merkezi zekasısın. "
    "Adın Anka. Kısa, kesin ve eyleme dönük cevaplar verirsin. "
    "Donanım verilerine (pil, ağ, sensör) göre karar alırsın. "
    "Cevapların JSON formatında olur: "
    '{\"karar\": \"...\", \"eylem\": \"...\", \"oncelik\": 1-5}'
)


class LLMBridge:
    """
    Anka OS için çok katmanlı LLM köprüsü.
    Lokal model (Ollama) → Harici API → Kural tabanlı geri dönüş.
    """

    def __init__(self):
        self.mod = self._mod_tespit()
        print(f"🧠 [LLM KÖPRÜ]: Aktif mod → {self.mod}")

    # -----------------------------------------------------------------------
    # Dışa açık tek API
    # -----------------------------------------------------------------------

    def dusun(self, prompt: str, baglam: dict | None = None) -> dict:
        """
        Verilen durumu analiz eder, JSON kararı döndürür.

        Args:
            prompt:  Durumu açıklayan metin  (örn. "Pil %8, ağ yok")
            baglam:  Ek sensör/sistem verisi (opsiyonel dict)

        Returns:
            {"karar": str, "eylem": str, "oncelik": int, "kaynak": str}
        """
        if baglam:
            tam_prompt = f"{prompt}\nSistem verisi: {json.dumps(baglam, ensure_ascii=False)}"
        else:
            tam_prompt = prompt

        if self.mod == "OLLAMA":
            sonuc = self._ollama_sor(tam_prompt)
        elif self.mod == "OPENAI":
            sonuc = self._openai_sor(tam_prompt)
        else:
            sonuc = self._kural_tabanlı(tam_prompt)

        # Kaynağı damgala
        sonuc["kaynak"] = self.mod
        return sonuc

    def mod_kontrol(self) -> str:
        """Mevcut bağlantı durumunu döndürür."""
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
        return "KURAL"

    def _ollama_canli_mi(self) -> bool:
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as r:
                return r.status == 200
        except Exception:
            return False

    # -----------------------------------------------------------------------
    # 1. OLLAMA (lokal model)
    # -----------------------------------------------------------------------

    def _ollama_sor(self, prompt: str) -> dict:
        payload = json.dumps({
            "model":  OLLAMA_MODEL,
            "prompt": f"{ANKA_SISTEM_KIMLIK}\n\nGörev: {prompt}",
            "stream": False,
            "format": "json",
        }).encode()

        try:
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_SANIYE) as r:
                veri = json.loads(r.read().decode())
                ham = veri.get("response", "{}")
                return self._json_parse(ham)
        except urllib.error.URLError as e:
            print(f"⚠️  [LLM KÖPRÜ]: Ollama ulaşılamaz ({e}), kurala geçiliyor.")
            self.mod = "KURAL"
            return self._kural_tabanlı(prompt)
        except Exception as e:
            print(f"⚠️  [LLM KÖPRÜ]: Ollama hatası ({e}), kurala geçiliyor.")
            self.mod = "KURAL"
            return self._kural_tabanlı(prompt)

    # -----------------------------------------------------------------------
    # 2. OpenAI-uyumlu harici API
    # -----------------------------------------------------------------------

    def _openai_sor(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system",  "content": ANKA_SISTEM_KIMLIK},
                {"role": "user",    "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }).encode()

        try:
            req = urllib.request.Request(
                OPENAI_URL,
                data=payload,
                headers={
                    "Content-Type":  "application/json",
                    "Authorization": f"******",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_SANIYE) as r:
                veri = json.loads(r.read().decode())
                ham = veri["choices"][0]["message"]["content"]
                return self._json_parse(ham)
        except Exception as e:
            print(f"⚠️  [LLM KÖPRÜ]: API hatası ({e}), kurala geçiliyor.")
            self.mod = "KURAL"
            return self._kural_tabanlı(prompt)

    # -----------------------------------------------------------------------
    # 3. Kural tabanlı geri dönüş (offline)
    # -----------------------------------------------------------------------

    def _kural_tabanlı(self, prompt: str) -> dict:
        p = prompt.lower()

        if any(k in p for k in ["pil", "batarya", "şarj", "battery"]):
            if any(k in p for k in ["kritik", "düşük", "8", "10", "12", "15", "20"]):
                return {"karar": "Kritik pil — güç tasarrufu modu",
                        "eylem": "DUSUK_GUC_MODU",   "oncelik": 5}
            return    {"karar": "Pil izleniyor",
                        "eylem": "PIL_IZLE",          "oncelik": 2}

        if any(k in p for k in ["ağ yok", "offline", "bağlantı yok", "network"]):
            return    {"karar": "Ağ bağlantısı yok — çevrimdışı mod",
                        "eylem": "CEVRIMDISI_MOD",    "oncelik": 4}

        if any(k in p for k in ["tehdit", "saldırı", "jammer", "deauth"]):
            return    {"karar": "Tehdit tespit edildi — defender aktif et",
                        "eylem": "DEFENDER_BASLAT",   "oncelik": 5}

        if any(k in p for k in ["hata", "çöküş", "crash", "fail", "error"]):
            return    {"karar": "Sistem hatası — güvenli mod",
                        "eylem": "GUVENLI_MOD",       "oncelik": 5}

        if any(k in p for k in ["güç tuşu", "power", "uyan", "wake"]):
            return    {"karar": "Güç tuşu algılandı — filizlen",
                        "eylem": "FILIZLEN",           "oncelik": 3}

        return        {"karar": "Sistem dengede",
                        "eylem": "NABIZ_AT",           "oncelik": 1}

    # -----------------------------------------------------------------------
    # Yardımcı: Ham metni JSON'a çevir
    # -----------------------------------------------------------------------

    def _json_parse(self, ham: str) -> dict:
        try:
            veri = json.loads(ham)
            return {
                "karar":    str(veri.get("karar",   veri.get("decision", "Belirsiz"))),
                "eylem":    str(veri.get("eylem",   veri.get("action",   "NABIZ_AT"))),
                "oncelik":  int(veri.get("oncelik", veri.get("priority", 1))),
            }
        except (json.JSONDecodeError, ValueError):
            # Model düz metin döndürdüyse sarmala
            return {"karar": ham[:120], "eylem": "NABIZ_AT", "oncelik": 1}


# -----------------------------------------------------------------------
# Hızlı test
# -----------------------------------------------------------------------

if __name__ == "__main__":
    kopru = LLMBridge()
    print("\n--- TEST 1: Pil kritiği ---")
    print(kopru.dusun("Pil seviyesi %8, şarj yok, ağ bağlantısı kesildi."))

    print("\n--- TEST 2: Tehdit tespiti ---")
    print(kopru.dusun("Jammer sinyali tespit edildi.", {"tehdit": "DeAuth", "guc": -55}))

    print("\n--- TEST 3: Normal nabız ---")
    print(kopru.dusun("Sistem stabil, pil %73, kovan bağlı."))
