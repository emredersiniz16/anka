# Makefile - ANKA OS NİHAİ ÇEKİRDEK MÜHÜRLEME (QUANTUM + ENGINES)
CC = gcc

# Header yolları: Hem kökü hem de alt klasörleri kapsayacak şekilde genişletildi
CFLAGS = -Os -fPIC \
         -I. \
         -I./core \
         -I./core/hal \
         -I./core/utils \
         -I./core/quantum \
         -I./core/engines

LDFLAGS = -ldl -lpthread -lcrypto -lssl

# Hedefler
TARGET_BIN = anka_os.bin
QUANTUM_LIB = core/quantum/libanka_quantum.so

# Kaynaklar
SRC_BOOT = core/boot.c \
           core/hal/hal_core.c \
           core/hal/hal_loader.c \
           core/hal/backends/backend_generic.c \
           core/engines/ui_engine.c \
           core/engines/fly_engine.c \
           core/engines/input_handler.c \
           core/engines/audio_engine.c

SRC_QUANTUM = core/quantum/quantum_dust.c \
              core/quantum/collapse_engine.c \
              core/quantum/sinek_fsm.c

all: $(QUANTUM_LIB) $(TARGET_BIN)

# 1. Kuantum motorunu (.so) inşa et
$(QUANTUM_LIB): $(SRC_QUANTUM)
	$(CC) $(CFLAGS) -shared $^ -o $@ $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Kuantum motoru (.so) mühürlendi."

# 2. Çekirdeği derle (SRC_BOOT içindeki tüm .c dosyalarını bağla)
$(TARGET_BIN): $(SRC_BOOT)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği mühürlendi (Binary Hazır)."

clean:
	rm -f $(TARGET_BIN) $(QUANTUM_LIB)
	@echo "🪰 [SYSTEM]: Mühürler kaldırıldı."
