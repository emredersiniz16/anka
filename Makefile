# ANKA OS - NİHAİ MÜHÜRLEME PROTOKOLÜ
# Cihazın içinde çalışacak otonom çekirdek ve sürücü entegrasyonu

CC = gcc
# Android/Termux üzerinde çalışacağı için dinamik linkleme ve core yolları
CFLAGS = -Os -I./core -I./core/hal -I./core/utils -ldl -fPIC

# Tüm modüler yapıdaki kaynakları topluyoruz
# engines, hal, ve backend sürücülerinin tamamını çekirdeğe dahil ediyoruz
SRC = core/boot.c \
      core/hal/hal_core.c \
      core/hal/hal_loader.c \
      core/hal/backends/generic_hal.c \
      $(wildcard core/engines/*.c)

TARGET = anka_os.bin

all: $(TARGET)

$(TARGET):
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)
	@echo "🪰 [SYSTEM]: Anka OS çekirdeği mühürlendi, donanım sürücüleri yüklendi (Binary Hazır)."

clean:
	rm -f $(TARGET)
