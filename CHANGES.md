# ANKA OS — Düzeltme Dökümü (v2)

## Yapılan Değişiklikler

### 1. boot.c — system("python3") → anka_run_python_bg() + SIGINT handler
- **system("su -c 'python3 agents/sinek_nexus.py &'") kaldırıldı**
  - Yerine: `anka_run_python_bg("agents/sinek_nexus.py", NULL)` (sh bypass)
  - /system/bin/sh artık devreye girmiyor
- **SIGINT handler eklendi** (Ctrl-C artık temiz kapanış sağlar)
  - `sigaction(SIGINT, ...)` + `sigaction(SIGTERM, ...)`
  - `while(1)` → `while(g_running)` — sinyal gelince döngü durur
- **Temiz kapanış** eklendi: collapse_shutdown(), sinek_fsm_destroy(), dlclose()
- **SIGPIPE yoksayma** eklendi (python alt processte pipe kırılırsa crash olmaz)
- **Python3 başarısızsa fallback**: SINEK_EVT_OFFLINE event'i gönderilir
- **#include "anka_env.h"** eklendi
- Dangling kod (satır 18-21) temizlendi

### 2. anka_env.h — stray EOF + anka_run_python_bg() eklendi
- **Satır 44'teki `EOF` artık metni kaldırıldı** (derleme hatası veriyordu)
- **anka_run_python_bg() fonksiyonu eklendi** — arka plan python3 başlatma (waitpid'siz)
  - `setsid()` ile kendi process grubuna geçer
  - system("... &") yerine kullanılır
- Kod düzenlendi, yorumlar eklendi

### 3. collapse_engine.h + collapse_engine.c — MAX_RULES 32 → 64
- **Header (satır 9): `#define MAX_RULES 32` → `#define MAX_RULES 64`**
- **C dosyası (satır 28): `#define MAX_RULES 32` → `#define MAX_RULES 64`**
- Artık 35+ kural yüklenebilir (eski kodda 32 slot, 35 kural → overflow)

### 4. BMP dosyaları — BI_BITFIELDS → 24-bit BI_RGB
- **fly_icon 2.bmp** (407x297, 32bpp, BI_BITFIELDS) → **fly_icon.bmp** (407x297, 24bpp, BI_RGB)
- **fly.bmp** (512x512, 32bpp, BI_BITFIELDS) → **fly.bmp** (512x512, 24bpp, BI_RGB)
- Dosya adlarındaki boşluk ve "2" soneki kaldırıldı
- "Sıkıştırılmış BMP desteklenmiyor" hatası artık çıkmayacak

### 5. ui_engine.c BMP loader — BI_BITFIELDS desteği
- **compression != 0** → **compression != 0 && compression != 3**
- BI_BITFIELDS (comp=3) artık kabul ediliyor (teknik olarak sıkıştırılmış değil)
- Hem fb_load_bmp hem fb_load_bmp_centered düzeltildi

### 6. fly_engine.c — system("su -c 'python3'") → anka_run_python_bg()
- **Satır 28**: `system("su -c 'python3 agents/sinek_nexus.py --pulse ...'")` → `anka_run_python_bg()`
- **Satır 37**: `system("su -c 'python3 agents/sinek_nexus.py --full-power ...'")` → `anka_run_python_bg()`
- **#include "anka_env.h"** eklendi

### 7. ota_engine.c — system("su -c 'python3'") → anka_run_python_bg()
- **Satır 37**: `system("su -c 'python3 agents/evrim_motoru.py --payload ...'")` → `anka_run_python_bg()`
- **#include "anka_env.h"** eklendi

### 8. magisk_template/ — eksik dosyalar oluşturuldu
- **module.prop** — Magisk modül metadatası
- **service.sh** — boot servisi (Termux python3 bekler, ANKA OS'i başlatır)
- `make magisk` artık çalışacak

## Özet: Ne Değişti

| Dosya | Değişiklik |
|-------|-----------|
| core/boot.c | system() → anka_run_python_bg() + SIGINT + temiz kapanış |
| core/anka_env.h | EOF kaldırıldı + anka_run_python_bg() eklendi |
| core/quantum/collapse_engine.h | MAX_RULES 32 → 64 |
| core/quantum/collapse_engine.c | MAX_RULES 32 → 64 |
| core/ui/ui_engine.c | BI_BITFIELDS BMP desteği |
| core/engines/fly_engine.c | 2x system("python3") → anka_run_python_bg() |
| core/engines/ota_engine.c | 1x system("python3") → anka_run_python_bg() |
| assets/fly_icon.bmp | 32bpp BI_BITFIELDS → 24bpp BI_RGB |
| assets/fly.bmp | 32bpp BI_BITFIELDS → 24bpp BI_RGB |
| magisk_template/module.prop | Yeni oluşturuldu |
| magisk_template/service.sh | Yeni oluşturuldu |

## Derleme

```bash
make clean && make
```

## Magisk modülü

```bash
make magisk
# → AnkaOS_Quantum_v1.zip flashlanmaya hazır
```

