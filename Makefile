# Makefile - ANKA OS NİHAİ ÇEKİRDEK VE KÖPRÜ MÜHÜRLEME
CC = aarch64-linux-gnu-gcc
# Termux içinde yerel derleme yapıyorsan alttakini kullanabilirsin, cross-compiler için üstteki kalır:
# CC = gcc

TARGET_BIN = anka_os.bin
TARGET_HAL = core/hal/anka_hal.so
BACKEND_SRC = core/hal/backends/backend_legacy_qualcomm_msm.c
BACKEND_SO = core/hal/backends/libhal_backend_legacy_qualcomm_msm.so

# Derleme bayrakları (-Wno-error ile usleep uyarısı ezildi)
CFLAGS = -Os -fPIC -DHAVE_OPENSSL -Wno-unused-result -Wno-error \
         -I. -I./core -I./core/hal -I./core/utils \
         -I./core/quantum -I./core/engines -I./core/ui

LDFLAGS = -ldl -lpthread -lcrypto -lssl -lm -lc

# Tüm kaynaklar tek havuzda (Kuantum ve Dokunmatik motoru dahil)
SRC_ALL = core/boot.c \
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
          core/engines/tohum_engine.c \
          core/touch_engine.c \
          core/quantum/quantum_dust.c \
          core/quantum/collapse_engine.c \
          core/quantum/sinek_fsm.c

all: $(TARGET_BIN) $(TARGET_HAL) $(BACKEND_SO)

# 1. Çekirdeği tüm motorlarla birlikte tek seferde mühürle
$(TARGET_BIN): $(SRC_ALL)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği tek parça halinde mühürlendi."

# 2. Python köprüsü için anka_hal.so (Shared Library) mühürlemesi
$(TARGET_HAL): $(BACKEND_SRC)
	$(CC) -shared -fPIC $(CFLAGS) $< -o $@
	@echo "🪰 [SYSTEM]: Python Donanım Köprüsü (anka_hal.so) mühürlendi."

# 3. Hasta Sıfır Qualcomm Backend .so mühürlemesi
$(BACKEND_SO): $(BACKEND_SRC)
	$(CC) -shared -fPIC $(CFLAGS) $< -o $@
	@echo "🪰 [SYSTEM]: Hasta Sıfır Qualcomm Backend mühürlendi."

# --- MAGISK MODÜLÜ OTOMASYONU ---
magisk: all
	@echo "🪰 [SYSTEM]: Magisk Modülü Hazırlanıyor..."
	@mkdir -p magisk_module/system/bin
	@mkdir -p magisk_module/system/anka_core/agents
	@mkdir -p magisk_module/system/anka_core/assets
	@cp magisk_template/module.prop magisk_module/
	@cp magisk_template/service.sh magisk_module/
	@cp magisk_template/sepolicy.rule magisk_module/
	@cp $(TARGET_BIN) magisk_module/system/bin/anka_os_bin
	@cp assets/fly_icon.bmp magisk_module/system/anka_core/assets/ 2>/dev/null || true
	@cp agents/*.py magisk_module/system/anka_core/agents/ 2>/dev/null || true
	@chmod -R 755 magisk_module
	@chmod +x magisk_module/service.sh
	@chmod +x magisk_module/system/bin/anka_os_bin
	@cd magisk_module && zip -r ../AnkaOS_Quantum_v1.zip . > /dev/null
	@rm -rf magisk_module
	@echo "✅ [SYSTEM]: AnkaOS_Quantum_v1.zip Mühürlendi ve Flaşlanmaya Hazır!"

clean:
	rm -f $(TARGET_BIN) $(TARGET_HAL) $(BACKEND_SO) core/quantum/*.o core/ui/*.o core/hal/*.o core/engines/*.o AnkaOS_Quantum_v1.zip $(ROM_ZIP)
	rm -rf rom_build
	@echo "🪰 [SYSTEM]: Mühürler kaldırıldı."

# --- ROM PAKETİ (TWRP flashlanabilir .zip) ---
ROM_ZIP = AnkaOS_ROM_merlin.zip

rom: all
	@echo "🪰 [ROM]: Redmi Note 9 (merlin) ROM paketi hazırlanıyor..."
	@rm -rf rom_build
	@cp -r rom_overlay rom_build
	@mkdir -p rom_build/system/bin
	@cp $(TARGET_BIN) rom_build/system/bin/anka_os
	@mkdir -p rom_build/system/anka_core/agents rom_build/system/anka_core/assets
	@cp agents/*.py rom_build/system/anka_core/agents/ 2>/dev/null || true
	@cp assets/fly_icon.bmp rom_build/system/anka_core/assets/ 2>/dev/null || true
	@cp assets/fly.bmp rom_build/system/anka_core/assets/ 2>/dev/null || true
	@# Launcher APK (varsa)
	@if [ -f rom_overlay/system/app/AnkaLauncher/AnkaLauncher.apk ]; then \
		echo "🪰 [ROM]: Launcher APK ekleniyor..."; \
		mkdir -p rom_build/system/app/AnkaLauncher; \
		cp rom_overlay/system/app/AnkaLauncher/AnkaLauncher.apk rom_build/system/app/AnkaLauncher/; \
	else \
		echo "⚠️ [ROM]: Launcher APK bulunamadı, atlanıyor."; \
	fi
	@# İzinleri ayarla
	@chmod -R 755 rom_build
	@chmod 755 rom_build/system/bin/anka_os
	@chmod 644 rom_build/system/etc/init/anka_os.rc
	@chmod 644 rom_build/system/etc/anka_ota.conf
	@if [ -f rom_build/system/app/AnkaLauncher/AnkaLauncher.apk ]; then \
		chmod 644 rom_build/system/app/AnkaLauncher/AnkaLauncher.apk; \
	fi
	@chmod +x rom_build/META-INF/com/google/android/update-binary
	@cd rom_build && zip -r ../$(ROM_ZIP) . > /dev/null || (echo "❌ [ROM]: ZIP oluşturma başarısız!" && exit 1)
	@rm -rf rom_build
	@echo "✅ [ROM]: $(ROM_ZIP) hazır — TWRP ile flashlanabilir!"
