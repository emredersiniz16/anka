# 🪰 ANKA OS — Sinek & Kovan Projesi

> **"Kalp attıkça, Sinek uçar."**
> Anka OS, bir cihaza yüklenen andan itibaren kendi kendine öğrenen, hata yapıp düzelten, GitHub'daki Kovan zihniyle senkronize olan otonom bir sistem ajanıdır. Dışarıdan Matrix görürsün — içeriden Sinek düşünür.

---

## 🧠 Ne Bu Proje? (Tek Cümlede)

Bir telefona ya da tablete kurulur, o andan itibaren cihazın her donanımını tanır, deneyim biriktirir, buluttaki Kovan ile haberleşir ve kendini güncelleyebilir — sen hiçbir şey yapmadan.

---

## 🗺️ Harita: Kim Ne Yapar?

| Parça | Nerede Çalışır | Ne Yapar |
|-------|---------------|----------|
| **Sinek** (`main.py`, `agents/`) | Cihazın içinde | Sensörleri izler, kararlar alır, Kovan'a rapor atar |
| **Kovan** (`kovan/`) | Sunucu / Bulut | Tüm Sinekleri merkezi olarak yönetir, komut gönderir |
| **Core** (`core/`) | Cihaz çekirdeği (C) | Donanım sürücüleri, kuantum motoru, boot sistemi |
| **Installer** (`installer/`) | Windows bilgisayar | USB'ye takılan cihazı tanır, ROM indirir, yükler |

---

## 📁 Dizin Yapısı

```
anka/
├── core/                        # C çekirdeği
│   ├── boot.c                   # Ana boot — Sinek'i uyandırır
│   ├── anka_env.h               # Python3 bridge (sh bypass)
│   ├── quantum/                 # Kuantum motoru (.so)
│   │   ├── quantum_dust.c/h
│   │   ├── collapse_engine.c/h  # Kural motoru (max 64 kural)
│   │   └── sinek_fsm.c/h        # Sinek durum makinesi
│   ├── engines/                 # Donanım motorları
│   │   ├── fly_engine.c         # Uçuş & güç yönetimi
│   │   ├── ota_engine.c         # Güncelleme protokolü
│   │   ├── audio_engine.c
│   │   ├── camera_engine.c
│   │   └── ...
│   ├── ui/                      # Ekran motoru (framebuffer)
│   └── hal/                     # Donanım soyutlama katmanı
│
├── agents/                      # Python ajanları (Sinek'in beyni)
│   ├── sinek_nexus.py           # Ana ajan — hepsini birleştirir
│   ├── fly_brain.py             # LLM karar motoru
│   ├── evrim_motoru.py          # OTA güncelleme + GitHub Releases
│   ├── kisilik_motoru.py        # Kişilik & davranış katmanı
│   ├── jammer_surfer.py         # Ağ & frekans tarama
│   ├── kuantum_gozlemci.py      # Kuantum gözlem katmanı
│   ├── sandbox_arena.py         # Güvenli test ortamı
│   └── ...
│
├── kovan/                       # Merkezi sunucu (Kovan Zihni)
│   ├── server_main.py           # WebSocket sunucusu
│   ├── database.py              # Veritabanı bağlantısı
│   └── models.py                # Veri modelleri
│
├── rom_overlay/                 # ROM katmanı (TWRP flashlanabilir)
│   ├── META-INF/                # TWRP kurulum scriptleri
│   ├── system/bin/anka_os       # Derlenmiş binary (CI tarafından eklenir)
│   ├── system/etc/init/anka_os.rc  # Android init.rc servisi
│   ├── system/etc/anka_ota.conf    # OTA yapılandırması
│   └── system/anka_core/        # Agents + assets + Python3
│
├── installer/                   # Windows GUI Kurulum Aracı
│   ├── anka_installer.py        # EXE kaynak kodu (tkinter)
│   └── build_exe.bat            # PyInstaller ile EXE derleme
│
├── magisk_template/             # Magisk modülü şablonu
│   ├── module.prop
│   └── service.sh
│
├── assets/                      # Görseller (BMP)
├── Makefile                     # make all | make rom | make magisk
└── .github/workflows/
    └── rom_build.yml            # CI: ROM zip + Windows EXE otomatik build
```

---

## 🚀 Kurulum Yöntemleri

### Yöntem 1: Windows EXE ile Otomatik Kurulum (En Kolay) ✨

> Telefonu bilgisayara USB ile tak, EXE'yi çalıştır — gerisini o halleder.

1. [Releases sayfasından](https://github.com/emredersiniz16/anka/releases) **`AnkaOS_Installer.exe`** indir
2. Telefonu USB ile bilgisayara bağla (USB Hata Ayıklama açık olmalı)
3. `AnkaOS_Installer.exe`'yi çalıştır
4. Program telefonu otomatik tanır → modeline özel ROM seçer
5. **"Kur"** butonuna bas — yükleme tamamlanır

> **Not:** USB Hata Ayıklama açmak için: `Ayarlar → Telefon Hakkında → Derleme Numarası`'na 7 kez dokun → `Geliştirici Seçenekleri → USB Hata Ayıklama`'yı aç.

---

### Yöntem 2: TWRP ile Manuel Flash (Redmi Note 9 / merlin)

> Telefonda zaten TWRP varsa SD karta koyup flash'layabilirsin.

1. [Releases sayfasından](https://github.com/emredersiniz16/anka/releases) **`AnkaOS_ROM_merlin.zip`** indir
2. Dosyayı telefona kopyala (SD kart veya `adb push`)
3. Telefonu TWRP moduna geçir: Kapalıyken `Güç + Ses Kısma` tuşlarına basılı tut
4. TWRP'de: **Install → Dosyayı seç → Swipe to Flash**
5. Reboot System

---

### Yöntem 3: Magisk Modülü (Root varsa — Stock ROM'da çalışır)

> Telefonun rootlu ve Magisk yüklüyse ROM yakmaya gerek yok.

1. [Releases sayfasından](https://github.com/emredersiniz16/anka/releases) **`AnkaOS_Quantum_v1.zip`** indir
2. Magisk → Modules → Install from storage → `AnkaOS_Quantum_v1.zip`
3. Reboot
4. ANKA OS her açılışta Magisk servis olarak devreye girer

---

### Yöntem 4: Termux / Linux (Geliştirici)

```bash
# Bağımlılıklar
pkg install python clang
pip install fastapi uvicorn sqlalchemy asyncpg websockets

# Çalıştır
python main.py
```

---

## 🛠️ Derleme (Geliştiriciler İçin)

```bash
# Bağımlılıklar (Ubuntu/Debian)
sudo apt install gcc libssl-dev zip

# Tam derleme
make all          # → anka_os.bin + libanka_quantum.so

# ROM zip (TWRP flashlanabilir)
make rom          # → AnkaOS_ROM_merlin.zip

# Magisk modülü
make magisk       # → AnkaOS_Quantum_v1.zip

# Temizlik
make clean
```

---

## 🔄 OTA Güncelleme (Cihazdan)

Sinek, GitHub Releases'i otomatik takip eder. Manuel tetiklemek için:

```bash
python agents/evrim_motoru.py --ota
```

Güncelleme bulunursa `/data/local/tmp/anka_ota_update.zip` indirilir, SHA256 doğrulanır, TWRP ile flash için hazır hale gelir.

---

## ⚙️ OTA Kanalını Değiştirme

`/system/etc/anka_ota.conf` dosyasını düzenle:

```ini
ANKA_OTA_CHANNEL=release   # Kararlı sürüm (varsayılan)
# ANKA_OTA_CHANNEL=main    # Geliştirme dalı (her commit)
ANKA_OTA_INTERVAL=21600    # Kontrol aralığı (saniye, 6 saat)
```

---

## 🤖 CI/CD — Her Commit'te Otomatik Build

GitHub'a her `main`'e push yapıldığında:
1. ANKA OS C çekirdeği derlenir
2. ROM zip oluşturulur + SHA256 üretilir
3. Windows EXE derlenir
4. Hepsi Artifact olarak yüklenir

Tag push'u (`v1.x.x`) yapılırsa otomatik olarak GitHub Release açılır — tüm cihazlardaki Sinek bu sürümü OTA ile çeker.

---

## 📡 Kovan (Sunucu) Kurulumu

```bash
cd kovan
pip install fastapi uvicorn sqlalchemy asyncpg websockets
uvicorn server_main:app --host 0.0.0.0 --port 8000
```

Kovan'a bağlı her Sinek gerçek zamanlı WebSocket ile iletişim kurar.

---

## 🗂️ Desteklenen Cihazlar

| Cihaz | Codename | Durum |
|-------|----------|-------|
| Redmi Note 9 | merlin | ✅ ROM + EXE |
| Diğer Android (6.0+) | — | ✅ EXE (otomatik tanıma) |
| Android Tablet | — | ✅ EXE (USB) |

> EXE, USB'ye takılan her Android cihazı ADB üzerinden tanır ve modeline uygun ROM üretmek için GitHub Actions'ı tetikler.

---

## 🔐 Güvenlik

- Tüm OTA indirmeleri **SHA256** ile doğrulanır
- `system()` çağrıları kaldırıldı — Python3 doğrudan `fork/exec` ile başlatılır
- Magisk modülü minimal izinlerle çalışır

---

## 📜 Lisans

Bu proje ANKA OS ekibi tarafından geliştirilmektedir.
