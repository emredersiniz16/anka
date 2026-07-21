# Makefile - ANKA OS NİHAİ MÜHÜRLEME (Temizlenmiş + Magisk)
# Redmi Note 9 (merlin) ARM64 hedefi — çapraz derleme
# Yerel geliştirme (x86_64) için: make CC=gcc
CC = clang

# Header yolları - ui klasörü eklendi
CFLAGS = -Os -fPIC \
         -DHAVE_OPENSSL \
         -I. \
         -I./core \
         -I./core/hal \
         -I./core/utils \
         -I./core/quantum \
         -I./core/engines \
         -I./core/ui

LDFLAGS = -ldl -lpthread -lcrypto -lssl -lm
QUANTUM_LDFLAGS = -L./core/quantum -Wl,-rpath,/system/lib -lanka_quantum
TARGET_BIN = anka_os.bin
QUANTUM_LIB = core/quantum/libanka_quantum.so

# Kaynaklar
SRC_BOOT = core/boot.c \
           core/hal/hal_core.c \
           core/hal/hal_loader.c \
           core/hal/backends/backend_generic.c \
           core/ui/ui_engine.c \
           core/ui/anim_engine.c \
           core/engines/audio_engine.c \
           core/engines/fly_engine.c \
           core/engines/camera_engine.c \
           core/engines/gallery_engine.c \
           core/engines/idle_engine.c \
           core/engines/input_engine.c \
           core/engines/input_handler.c \
           core/engines/ota_engine.c \
           core/engines/system_monitor.c \
           core/engines/tohum_engine.c

SRC_QUANTUM = core/quantum/quantum_dust.c \
              core/quantum/collapse_engine.c \
              core/quantum/sinek_fsm.c

all: $(QUANTUM_LIB) $(TARGET_BIN)

$(QUANTUM_LIB): $(SRC_QUANTUM)
	$(CC) $(CFLAGS) -shared $^ -o $@ $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Kuantum motoru (.so) mühürlendi."

$(TARGET_BIN): $(SRC_BOOT) $(QUANTUM_LIB)
	$(CC) $(CFLAGS) $(SRC_BOOT) -o $@ $(QUANTUM_LDFLAGS) $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği mühürlendi (Binary Hazır)."

# --- MAGISK MODÜLÜ OTOMASYONU ---
magisk: all
	@echo "🪰 [SYSTEM]: Magisk Modülü Hazırlanıyor..."
	@mkdir -p magisk_module/system/bin
	@mkdir -p magisk_module/system/lib
	@mkdir -p magisk_module/system/anka_core/agents
	@mkdir -p magisk_module/system/anka_core/assets
	@cp magisk_template/module.prop magisk_module/
	@cp magisk_template/service.sh magisk_module/
	@cp $(TARGET_BIN) magisk_module/system/bin/anka_os_bin
	@cp $(QUANTUM_LIB) magisk_module/system/lib/
	@cp assets/fly_icon.bmp magisk_module/system/anka_core/assets/ 2>/dev/null || true
	@cp agents/*.py magisk_module/system/anka_core/agents/ 2>/dev/null || true
	@chmod -R 755 magisk_module
	@chmod +x magisk_module/service.sh
	@chmod +x magisk_module/system/bin/anka_os_bin
	@cd magisk_module && zip -r ../AnkaOS_Quantum_v1.zip . > /dev/null
	@rm -rf magisk_module
	@echo "✅ [SYSTEM]: AnkaOS_Quantum_v1.zip Mühürlendi ve Flaşlanmaya Hazır!"

clean:
	rm -f $(TARGET_BIN) $(QUANTUM_LIB) core/quantum/*.o core/ui/*.o core/hal/*.o core/engines/*.o AnkaOS_Quantum_v1.zip $(ROM_ZIP)
	rm -rf rom_build
	@echo "🪰 [SYSTEM]: Mühürler kaldırıldı."

# --- ROM PAKETI (TWRP flashlanabilir .zip) ---
# Redmi Note 9 (merlin) için tam sistem katmanı
ROM_ZIP = AnkaOS_ROM_merlin.zip

rom: all
	@echo "🪰 [ROM]: Redmi Note 9 (merlin) ROM paketi hazırlanıyor..."
	@# Overlay'i çalışma dizinine kopyala
	@rm -rf rom_build
	@cp -r rom_overlay rom_build
	@# Dizinleri güvence altına al
	@mkdir -p rom_build/system/bin rom_build/system/lib
	@# Derlenmiş binary ve kütüphaneyi ekle
	@cp $(TARGET_BIN) rom_build/system/bin/anka_os
	@cp $(QUANTUM_LIB) rom_build/system/lib/libanka_quantum.so
	@# Agent'ları ve asset'leri ekle
	@mkdir -p rom_build/system/anka_core/agents rom_build/system/anka_core/assets
	@cp agents/*.py rom_build/system/anka_core/agents/ 2>/dev/null || true
	@cp assets/fly_icon.bmp rom_build/system/anka_core/assets/ 2>/dev/null || true
	@cp assets/fly.bmp rom_build/system/anka_core/assets/ 2>/dev/null || true
	@# İzinleri ayarla
	@chmod -R 755 rom_build
	@chmod 755 rom_build/system/bin/anka_os
	@chmod 644 rom_build/system/lib/libanka_quantum.so
	@chmod 644 rom_build/system/etc/init/anka_os.rc
	@chmod 644 rom_build/system/etc/anka_ota.conf
	@chmod +x rom_build/META-INF/com/google/android/update-binary
	@# ZIP'i oluştur
	@cd rom_build && zip -r ../$(ROM_ZIP) . > /dev/null || (echo "❌ [ROM]: ZIP oluşturma başarısız!" && exit 1)
	@rm -rf rom_build
	@echo "✅ [ROM]: $(ROM_ZIP) hazır — TWRP ile flashlanabilir!"
