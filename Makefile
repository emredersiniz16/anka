# Makefile - ANKA OS NİHAİ ÇEKİRDEK MÜHÜRLEME
CC = gcc

# Header yolları
CFLAGS = -Os -fPIC \
         -I. \
         -I./core \
         -I./core/hal \
         -I./core/utils \
         -I./core/quantum \
         -I./core/engines

# LDFLAGS: -lm (math kütüphanesi) eklendi (anim_engine için şart)
LDFLAGS = -ldl -lpthread -lcrypto -lssl -lm
QUANTUM_LDFLAGS = -L./core/quantum -lanka_quantum

# Hedefler
TARGET_BIN = anka_os.bin
QUANTUM_LIB = core/quantum/libanka_quantum.so

# Kaynaklar (Tüm motorları kapsayacak şekilde genişletildi)
SRC_BOOT = core/boot.c \
           core/hal/hal_core.c \
           core/hal/hal_loader.c \
           core/hal/backends/backend_generic.c \
           core/engines/ui_engine.c \
           core/engines/anim_engine.c \
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

# 1. Kuantum motorunu (.so) inşa et
$(QUANTUM_LIB): $(SRC_QUANTUM)
	$(CC) $(CFLAGS) -shared $^ -o $@ $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Kuantum motoru (.so) mühürlendi."

# 2. Çekirdeği derle
$(TARGET_BIN): $(SRC_BOOT) $(QUANTUM_LIB)
	$(CC) $(CFLAGS) $(SRC_BOOT) -o $@ $(QUANTUM_LDFLAGS) $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği mühürlendi (Binary Hazır)."

clean:
	rm -f $(TARGET_BIN) $(QUANTUM_LIB)
	@echo "🪰 [SYSTEM]: Mühürler kaldırıldı."
