#!/bin/bash

# Hata oluşursa scripti durdur
set -e 

echo "🔄 1. GitHub'dan güncel kodlar çekiliyor..."
git pull origin main

echo "⚙️ 2. Proje derleniyor..."
# Kendi derleme komutunu buraya yaz (Örn: make, ./build.sh veya Anka OS derleme komutu)
make 

echo "☁️ 3. Değişiklikler GitHub'a yükleniyor..."
# Derlenen dosyaları veya yeni değişiklikleri ekle
git add .
git commit -m "Otomatik derleme ve güncelleme: $(date +'%Y-%m-%d %H:%M')"
git push origin main

echo "🚀 4. Proje başlatılıyor..."
# Başlatma komutunu buraya yaz
./start.sh 

echo "✅ İşlem başarıyla tamamlandı!"
