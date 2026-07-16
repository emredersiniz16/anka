# Makefile - ANKA OS NİHAİ ÇEKİRDEK MÜHÜRLEME
CC = gcc
# -I yolları ile header dosyalarını (hal_common.h vb.) bulmasını sağlıyoruz
CFLAGS = -Os -I./core -I./core/hal -I./core/utils -ldl -fPIC

# Kaynak kodları: boot.c çekirdektir, geri kalanı modüller
SRC = core/boot.c \
      core/hal/hal_core.c \
      core/hal/hal_loader.c \
      core/hal/backends/backend_generic.c \
      core/engines/*.c

TARGET = anka_os.bin

all: $(TARGET)

$(TARGET):
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği mühürlendi (Binary Hazır)."

clean:
	rm -f $(TARGET)
