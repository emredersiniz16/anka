#!/usr/bin/env python3
# agents/sinek_memory.py - SINEK UZUN SÜRELİ ANI VERİTABANI
# Sıfır bağımlılık — sadece standart Python (sqlite3, hashlib, re, time, os)
# Sinek'in tüm anıları burada saklanır ve kelime benzerliği ile aranır.

import sqlite3
import hashlib
import re
import time
import os
import json

DB_PATH = "/data/local/tmp/anka_memory.db"

AN_TURLERI = {
    "KULLANICI_SOHBET": "Kullanıcı ile sohbet anısı",
    "FREKANS_IZI": "Frekans/ağ gözlem izi",
    "EVRIM_NOTU": "Evrim aşaması değişimi",
    "DUYGU_KAYDI": "Duygu durumu kaydı",
}


class SinekMemory:
    """Sinek'in uzun süreli anı veritabanı — SQLite tabanlı."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS anilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tur TEXT NOT NULL,
                icerik TEXT NOT NULL,
                duygu TEXT,
                duygu_siddet REAL DEFAULT 0.5,
                kuantum_tozu INTEGER DEFAULT 0,
                zaman INTEGER NOT NULL,
                hash TEXT UNIQUE,
                kelimeler TEXT
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_tur ON anilar(tur)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_zaman ON anilar(zaman)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_kelimeler ON anilar(kelimeler)")
        conn.commit()
        conn.close()

    def _kelime_ayikla(self, metin):
        """Metni kelimelere ayır, küçük harfe çevir, stop-word'leri ele."""
        kelimeler = re.findall(r'\b\w{2,}\b', metin.lower())
        stop_words = {"bir", "ve", "ile", "için", "bu", "şu", "o", "de", "da", "ki",
                      "mi", "mı", "ne", "ama", "fakat", "veya", "ya", "ise",
                      "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
                      "is", "are", "was", "were", "be", "been", "it", "this", "that"}
        return [k for k in kelimeler if k not in stop_words]

    def _hash_hesapla(self, icerik, tur):
        ham = f"{tur}:{icerik}"
        return hashlib.sha256(ham.encode()).hexdigest()[:16]

    def ani_kaz(self, tur, icerik, duygu=None, duygu_siddet=0.5, kuantum_tozu=0):
        """
        Yeni bir anı veritabanına kazır.
        Aynı içerik+tur varsa çağırma sayısını artırır.
        """
        if tur not in AN_TURLERI:
            return False
        if not icerik or not icerik.strip():
            return False
        
        hash_deger = self._hash_hesapla(icerik, tur)
        kelimeler = " ".join(self._kelime_ayikla(icerik))
        zaman = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO anilar (tur, icerik, duygu, duygu_siddet, kuantum_tozu, zaman, hash, kelimeler)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tur, icerik, duygu, duygu_siddet, kuantum_tozu, zaman, hash_deger, kelimeler))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
        return True

    def ani_ara(self, sorgu, limit=5):
        """
        Metin bazlı kelime/vektör benzerliği arama.
        Sorgu kelimelerini anı içerikleri ile karşılaştırır.
        """
        sorgu_kelimeler = set(self._kelime_ayikla(sorgu))
        if not sorgu_kelimeler:
            return []
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, tur, icerik, duygu, duygu_siddet, kuantum_tozu, zaman, kelimeler FROM anilar ORDER BY zaman DESC")
        satirlar = c.fetchall()
        conn.close()
        
        skorlar = []
        for satir in satirlar:
            ani_kelimeler = set(satir[7].split()) if satir[7] else set()
            if not ani_kelimeler:
                continue
            kesisim = len(sorgu_kelimeler & ani_kelimeler)
            benzerlik = kesisim / max(len(sorgu_kelimeler), 1)
            if benzerlik > 0:
                skorlar.append({
                    "id": satir[0],
                    "tur": satir[1],
                    "icerik": satir[2],
                    "duygu": satir[3],
                    "duygu_siddet": satir[4],
                    "kuantum_tozu": satir[5],
                    "zaman": satir[6],
                    "benzerlik": benzerlik,
                })
        
        skorlar.sort(key=lambda x: x["benzerlik"], reverse=True)
        return skorlar[:limit]

    def turden_al(self, tur, limit=10):
        """Belirli türdeki son anıları getir."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, icerik, duygu, duygu_siddet, kuantum_tozu, zaman FROM anilar WHERE tur=? ORDER BY zaman DESC LIMIT ?", (tur, limit))
        satirlar = c.fetchall()
        conn.close()
        return [{"id": s[0], "icerik": s[1], "duygu": s[2], "duygu_siddet": s[3], "kuantum_tozu": s[4], "zaman": s[5]} for s in satirlar]

    def son_anilar(self, limit=10):
        """En son anıları getir."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, tur, icerik, duygu, duygu_siddet, kuantum_tozu, zaman FROM anilar ORDER BY zaman DESC LIMIT ?", (limit,))
        satirlar = c.fetchall()
        conn.close()
        return [{"id": s[0], "tur": s[1], "icerik": s[2], "duygu": s[3], "duygu_siddet": s[4], "kuantum_tozu": s[5], "zaman": s[6]} for s in satirlar]

    def duygu_durumu_al(self):
        """Son DUYGU_KAYDI türünden anıdan duygu durumunu getir."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT duygu, duygu_siddet FROM anilar WHERE tur='DUYGU_KAYDI' ORDER BY zaman DESC LIMIT 1")
        satir = c.fetchone()
        conn.close()
        if satir:
            return {"duygu": satir[0], "siddet": satir[1]}
        return {"duygu": "nötr", "siddet": 0.5}

    def kuantum_tozu_al(self):
        """Son anıdaki kuantum tozu seviyesini getir."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT kuantum_tozu FROM anilar ORDER BY zaman DESC LIMIT 1")
        satir = c.fetchone()
        conn.close()
        return satir[0] if satir else 0

    def toplam_ani_sayisi(self):
        """Veritabanındaki toplam anı sayısı."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM anilar")
        sayi = c.fetchone()[0]
        conn.close()
        return sayi

    def temizle(self, esik_zaman=None):
        """Belirli zamandan eski anıları sil (esik_zaman=None ise hepsini sil)."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if esik_zaman:
            c.execute("DELETE FROM anilar WHERE zaman < ?", (esik_zaman,))
        else:
            c.execute("DELETE FROM anilar")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    mem = SinekMemory()
    print(f"Toplam anı: {mem.toplam_ani_sayisi()}")
    mem.ani_kaz("KULLANICI_SOHBET", "Selam kanka nasılsın bugün", duygu="merak", duygu_siddet=0.7, kuantum_tozu=42)
    mem.ani_kaz("DUYGU_KAYDI", "Sinek meraklı hissediyor", duygu="merak", duygu_siddet=0.8, kuantum_tozu=42)
    mem.ani_kaz("FREKANS_IZI", "2.4GHz sinyali tespit edildi -55dBm", duygu="tedbirli", duygu_siddet=0.6, kuantum_tozu=42)
    print(f"Toplam anı: {mem.toplam_ani_sayisi()}")
    print("\n--- Arama: 'sinyal' ---")
    print(mem.ani_ara("sinyal"))
    print("\n--- Arama: 'merak' ---")
    print(mem.ani_ara("merak"))
    print("\n--- Son anılar ---")
    print(mem.son_anilar(3))
