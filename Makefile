CC=gcc
CFLAGS=-fPIC -shared

all: audio_engine.so

audio_engine.so: core/engines/audio_engine.c
	$(CC) $(CFLAGS) -o core/engines/audio_engine.so core/engines/audio_engine.c

clean:
	rm core/engines/*.so
