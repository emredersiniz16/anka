# Anka OS - Sinek & Kovan Projesi

Anka OS tabanlı mobil cihazlarda otonom veri toplama ve merkezi yönetim sistemi.

## 📂 Dizin Yapısı
- `/main.py`: Sinek (Cihaz tarafı - Otonom Ajan)
- `/core/engines/`: Donanım sürücüleri (.so motorlar)
- `/kovan/`: Merkezi kontrol paneli (Sunucu tarafı)
  - `server_main.py`: WebSocket Sunucusu
  - `database.py`: Veritabanı bağlantı yönetimi

## 🚀 Kurulum (Termux/Linux)
1. Gerekli kütüphaneleri yükle:
   ```bash
   pip install fastapi uvicorn sqlalchemy asyncpg websockets
   pkg install clang
