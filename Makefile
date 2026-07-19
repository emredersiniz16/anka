# Makefile - ANKA OS NİHAİ MÜHÜRLEME (GitHub Actions Uyumlu)
CC = aarch64-linux-gnu-gcc

# Yollar
LIB_PATH = ./core/quantum
LIB_FILE = $(LIB_PATH)/libanka_quantum.so
TARGET_BIN = anka_os.bin

# Derleme bayrakları: -Wno-error eklenerek uyarıların derlemeyi durdurması engellendi
CFLAGS = -Os -fPIC -DHAVE_OPENSSL -Wno-unused-result -Wno-error \
         -I. -I./core -I./core/hal -I./core/utils \
         -I./core/quantum -I./core/engines -I./core/ui

LDFLAGS = -ldl -lpthread -lcrypto -lssl -lm -lc

# Kaynaklar
SRC_BOOT = core/boot.c core/hal/hal_core.c core/hal/hal_loader.c \
           core/hal/backends/backend_generic.c core/ui/ui_engine.c \
           core/ui/anim_engine.c core/engines/audio_engine.c \
           core/engines/fly_engine.c core/engines/camera_engine.c \
           core/engines/gallery_engine.c core/engines/idle_engine.c \
           core/engines/input_engine.c core/engines/input_handler.c \
           core/engines/ota_engine.c core/engines/system_monitor.c \
           core/engines/tohum_engine.c

SRC_QUANTUM = core/quantum/quantum_dust.c core/quantum/collapse_engine.c \
              core/quantum/sinek_fsm.c

all: $(LIB_FILE) $(TARGET_BIN)

# Kuantum motorunu derle (bağımlılıkları ekledik ki linker hata vermesin)[span_1](start_span)[span_1](end_span)
$(LIB_FILE): $(SRC_QUANTUM)
	@mkdir -p $(LIB_PATH)
	$(CC) $(CFLAGS) -shared $^ -o $@ $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Kuantum motoru (.so) başarıyla mühürlendi."

# Binary'yi kütüphane bağımlılığı ile derle
$(TARGET_BIN): $(SRC_BOOT) $(LIB_FILE)
	$(CC) $(CFLAGS) $(SRC_BOOT) -o $@ -L$(LIB_PATH) -lanka_quantum -Wl,-rpath,'$$ORIGIN' $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği mühürlendi."

# --- MAGISK MODÜLÜ OTOMASYONU ---
magisk: all
	@echo "🪰 [SYSTEM]: Magisk Modülü Hazırlanıyor..."
	@mkdir -p magisk_module/system/bin magisk_module/system/lib magisk_module/system/anka_core/agents
	@cp magisk_template/module.prop magisk_module/
	@cp magisk_template/service.sh magisk_module/
	@cp $(TARGET_BIN) magisk_module/system/bin/anka_os_bin
	@cp $(LIB_FILE) magisk_module/system/lib/
	@cp agents/*.py magisk_module/system/anka_core/agents/ 2>/dev/null || true
	@cd magisk_module && zip -r ../AnkaOS_Quantum_v1.zip . > /dev/null
	@rm -rf magisk_module
	@echo "✅ [SYSTEM]: AnkaOS_Quantum_v1.zip hazır!"

clean:
	rm -f $(TARGET_BIN) $(LIB_FILE) *.o AnkaOS_Quantum_v1.zip AnkaOS_ROM_merlin.zip
	rm -rf rom_build
	@echo "🪰 [SYSTEM]: Mühürler kaldırıldı."

# --- ROM PAKETI ---
ROM_ZIP = AnkaOS_ROM_merlin.zip
rom: all
	@echo "🪰 [ROM]: Redmi Note 9 (merlin) ROM paketi hazırlanıyor..."
	@rm -rf rom_build && cp -r rom_overlay rom_build
	@mkdir -p rom_build/system/bin rom_build/system/lib
	@cp $(TARGET_BIN) rom_build/system/bin/anka_os
	@cp $(LIB_FILE) rom_build/system/lib/libanka_quantum.so
	@mkdir -p rom_build/system/anka_core/agents
	@cp agents/*.py rom_build/system/anka_core/agents/ 2>/dev/null || true
	@chmod -R 755 rom_build
	@cd rom_build && zip -r ../$(ROM_ZIP) . > /dev/null
	@rm -rf rom_build
	@echo "✅ [ROM]: $(ROM_ZIP) hazır!"
