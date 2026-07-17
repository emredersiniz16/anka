# Makefile - ANKA OS NİHAİ MÜHÜRLEME (Temizlenmiş)
CC = gcc

# Header yolları - ui klasörü eklendi
CFLAGS = -Os -fPIC \
         -I. \
         -I./core \
         -I./core/hal \
         -I./core/utils \
         -I./core/quantum \
         -I./core/engines \
         -I./core/ui

LDFLAGS = -ldl -lpthread -lcrypto -lssl -lm
QUANTUM_LDFLAGS = -L./core/quantum -Wl,-rpath,$(PWD)/core/quantum -lanka_quantum
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
           core/engines/system_monitor.c

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

clean:
	rm -f $(TARGET_BIN) $(QUANTUM_LIB) core/quantum/*.o core/ui/*.o core/hal/*.o core/engines/*.o
	@echo "🪰 [SYSTEM]: Mühürler kaldırıldı."
