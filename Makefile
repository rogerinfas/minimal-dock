CC = gcc
CFLAGS = -O2 -Wall `pkg-config --cflags gtk+-3.0 gtk-layer-shell-0`
LIBS = `pkg-config --libs gtk+-3.0 gtk-layer-shell-0`
TARGET = minimal-dock

all: $(TARGET)

$(TARGET): main.c
	$(CC) $(CFLAGS) main.c -o $(TARGET) $(LIBS)

install: $(TARGET)
	install -Dm755 $(TARGET) ~/.local/bin/$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all install clean
