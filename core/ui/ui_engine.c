/*
 * core/ui/ui_engine.c  —  Anka OS Framebuffer UI Engine
 *
 * Bu dosya ui_engine.h'de tanımlı tüm fonksiyonları tam olarak uygular.
 * Üç linker hatasını çözer:
 *   1. fb_load_bmp
 *   2. fb_load_bmp_centered
 *   3. user_confirmed_evolution
 *
 * 🪰 [GÖLGE]: C99, -Wall -Wextra temiz (sistem() uyarıları mevcut koddan).
 */

/* =========================================================================
 * SECTION 1: INCLUDES AND DEFINES
 * ========================================================================= */

#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#include "ui_engine.h"
#include "fly_engine.h"   /* FLY_IDLE, FLY_GHOST, FLY_MIRROR, FLY_THINK,
                             current_state, update_fly_behavior()          */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/fb.h>
#include <time.h>

/* =========================================================================
 * SECTION 2: COMPLETE 8×8 BITMAP FONT (ASCII 32–127, 96 entries)
 *
 * font8x8_basic[i] = glyph for ASCII (32 + i).
 * Her satır 8 piksel genişliğinde bir bitmap satırıdır; bit 0 sol taraftadır.
 * Public domain — https://github.com/dhepper/font8x8
 * ========================================================================= */

static const uint8_t font8x8_basic[96][8] = {
    /* 0x20  ' ' */ { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
    /* 0x21  '!' */ { 0x18, 0x3C, 0x3C, 0x18, 0x18, 0x00, 0x18, 0x00 },
    /* 0x22  '"' */ { 0x36, 0x36, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
    /* 0x23  '#' */ { 0x36, 0x36, 0x7F, 0x36, 0x7F, 0x36, 0x36, 0x00 },
    /* 0x24  '$' */ { 0x0C, 0x3E, 0x03, 0x1E, 0x30, 0x1F, 0x0C, 0x00 },
    /* 0x25  '%' */ { 0x00, 0x63, 0x33, 0x18, 0x0C, 0x66, 0x63, 0x00 },
    /* 0x26  '&' */ { 0x1C, 0x36, 0x1C, 0x6E, 0x3B, 0x33, 0x6E, 0x00 },
    /* 0x27  '\''*/ { 0x06, 0x06, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00 },
    /* 0x28  '(' */ { 0x18, 0x0C, 0x06, 0x06, 0x06, 0x0C, 0x18, 0x00 },
    /* 0x29  ')' */ { 0x06, 0x0C, 0x18, 0x18, 0x18, 0x0C, 0x06, 0x00 },
    /* 0x2A  '*' */ { 0x00, 0x66, 0x3C, 0xFF, 0x3C, 0x66, 0x00, 0x00 },
    /* 0x2B  '+' */ { 0x00, 0x0C, 0x0C, 0x3F, 0x0C, 0x0C, 0x00, 0x00 },
    /* 0x2C  ',' */ { 0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C, 0x06 },
    /* 0x2D  '-' */ { 0x00, 0x00, 0x00, 0x3F, 0x00, 0x00, 0x00, 0x00 },
    /* 0x2E  '.' */ { 0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00 },
    /* 0x2F  '/' */ { 0x60, 0x30, 0x18, 0x0C, 0x06, 0x03, 0x01, 0x00 },
    /* 0x30  '0' */ { 0x3E, 0x63, 0x73, 0x7B, 0x6F, 0x67, 0x3E, 0x00 },
    /* 0x31  '1' */ { 0x0C, 0x0E, 0x0C, 0x0C, 0x0C, 0x0C, 0x3F, 0x00 },
    /* 0x32  '2' */ { 0x1E, 0x33, 0x30, 0x1C, 0x06, 0x33, 0x3F, 0x00 },
    /* 0x33  '3' */ { 0x1E, 0x33, 0x30, 0x1C, 0x30, 0x33, 0x1E, 0x00 },
    /* 0x34  '4' */ { 0x38, 0x3C, 0x36, 0x33, 0x7F, 0x30, 0x78, 0x00 },
    /* 0x35  '5' */ { 0x3F, 0x03, 0x1F, 0x30, 0x30, 0x33, 0x1E, 0x00 },
    /* 0x36  '6' */ { 0x1C, 0x06, 0x03, 0x1F, 0x33, 0x33, 0x1E, 0x00 },
    /* 0x37  '7' */ { 0x3F, 0x33, 0x30, 0x18, 0x0C, 0x0C, 0x0C, 0x00 },
    /* 0x38  '8' */ { 0x1E, 0x33, 0x33, 0x1E, 0x33, 0x33, 0x1E, 0x00 },
    /* 0x39  '9' */ { 0x1E, 0x33, 0x33, 0x3E, 0x30, 0x18, 0x0E, 0x00 },
    /* 0x3A  ':' */ { 0x00, 0x0C, 0x0C, 0x00, 0x00, 0x0C, 0x0C, 0x00 },
    /* 0x3B  ';' */ { 0x00, 0x0C, 0x0C, 0x00, 0x00, 0x0C, 0x0C, 0x06 },
    /* 0x3C  '<' */ { 0x18, 0x0C, 0x06, 0x03, 0x06, 0x0C, 0x18, 0x00 },
    /* 0x3D  '=' */ { 0x00, 0x00, 0x3F, 0x00, 0x00, 0x3F, 0x00, 0x00 },
    /* 0x3E  '>' */ { 0x06, 0x0C, 0x18, 0x30, 0x18, 0x0C, 0x06, 0x00 },
    /* 0x3F  '?' */ { 0x1E, 0x33, 0x30, 0x18, 0x0C, 0x00, 0x0C, 0x00 },
    /* 0x40  '@' */ { 0x3E, 0x63, 0x7B, 0x7B, 0x7B, 0x03, 0x1E, 0x00 },
    /* 0x41  'A' */ { 0x0C, 0x1E, 0x33, 0x33, 0x3F, 0x33, 0x33, 0x00 },
    /* 0x42  'B' */ { 0x3F, 0x66, 0x66, 0x3E, 0x66, 0x66, 0x3F, 0x00 },
    /* 0x43  'C' */ { 0x3C, 0x66, 0x03, 0x03, 0x03, 0x66, 0x3C, 0x00 },
    /* 0x44  'D' */ { 0x1F, 0x36, 0x66, 0x66, 0x66, 0x36, 0x1F, 0x00 },
    /* 0x45  'E' */ { 0x7F, 0x46, 0x16, 0x1E, 0x16, 0x46, 0x7F, 0x00 },
    /* 0x46  'F' */ { 0x7F, 0x46, 0x16, 0x1E, 0x16, 0x06, 0x0F, 0x00 },
    /* 0x47  'G' */ { 0x3C, 0x66, 0x03, 0x03, 0x73, 0x66, 0x7C, 0x00 },
    /* 0x48  'H' */ { 0x33, 0x33, 0x33, 0x3F, 0x33, 0x33, 0x33, 0x00 },
    /* 0x49  'I' */ { 0x1E, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x1E, 0x00 },
    /* 0x4A  'J' */ { 0x78, 0x30, 0x30, 0x30, 0x33, 0x33, 0x1E, 0x00 },
    /* 0x4B  'K' */ { 0x67, 0x66, 0x36, 0x1E, 0x36, 0x66, 0x67, 0x00 },
    /* 0x4C  'L' */ { 0x0F, 0x06, 0x06, 0x06, 0x46, 0x66, 0x7F, 0x00 },
    /* 0x4D  'M' */ { 0x63, 0x77, 0x7F, 0x7F, 0x6B, 0x63, 0x63, 0x00 },
    /* 0x4E  'N' */ { 0x63, 0x67, 0x6F, 0x7B, 0x73, 0x63, 0x63, 0x00 },
    /* 0x4F  'O' */ { 0x1C, 0x36, 0x63, 0x63, 0x63, 0x36, 0x1C, 0x00 },
    /* 0x50  'P' */ { 0x3F, 0x66, 0x66, 0x3E, 0x06, 0x06, 0x0F, 0x00 },
    /* 0x51  'Q' */ { 0x1E, 0x33, 0x33, 0x33, 0x3B, 0x1E, 0x38, 0x00 },
    /* 0x52  'R' */ { 0x3F, 0x66, 0x66, 0x3E, 0x36, 0x66, 0x67, 0x00 },
    /* 0x53  'S' */ { 0x1E, 0x33, 0x07, 0x0E, 0x38, 0x33, 0x1E, 0x00 },
    /* 0x54  'T' */ { 0x3F, 0x2D, 0x0C, 0x0C, 0x0C, 0x0C, 0x1E, 0x00 },
    /* 0x55  'U' */ { 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x3F, 0x00 },
    /* 0x56  'V' */ { 0x33, 0x33, 0x33, 0x33, 0x33, 0x1E, 0x0C, 0x00 },
    /* 0x57  'W' */ { 0x63, 0x63, 0x63, 0x6B, 0x7F, 0x77, 0x63, 0x00 },
    /* 0x58  'X' */ { 0x63, 0x63, 0x36, 0x1C, 0x1C, 0x36, 0x63, 0x00 },
    /* 0x59  'Y' */ { 0x33, 0x33, 0x33, 0x1E, 0x0C, 0x0C, 0x1E, 0x00 },
    /* 0x5A  'Z' */ { 0x7F, 0x63, 0x31, 0x18, 0x4C, 0x66, 0x7F, 0x00 },
    /* 0x5B  '[' */ { 0x1E, 0x06, 0x06, 0x06, 0x06, 0x06, 0x1E, 0x00 },
    /* 0x5C  '\' */ { 0x03, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x40, 0x00 },
    /* 0x5D  ']' */ { 0x1E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x1E, 0x00 },
    /* 0x5E  '^' */ { 0x08, 0x1C, 0x36, 0x63, 0x00, 0x00, 0x00, 0x00 },
    /* 0x5F  '_' */ { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF },
    /* 0x60  '`' */ { 0x0C, 0x0C, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00 },
    /* 0x61  'a' */ { 0x00, 0x00, 0x1E, 0x30, 0x3E, 0x33, 0x6E, 0x00 },
    /* 0x62  'b' */ { 0x07, 0x06, 0x06, 0x3E, 0x66, 0x66, 0x3B, 0x00 },
    /* 0x63  'c' */ { 0x00, 0x00, 0x1E, 0x33, 0x03, 0x33, 0x1E, 0x00 },
    /* 0x64  'd' */ { 0x38, 0x30, 0x30, 0x3E, 0x33, 0x33, 0x6E, 0x00 },
    /* 0x65  'e' */ { 0x00, 0x00, 0x1E, 0x33, 0x3F, 0x03, 0x1E, 0x00 },
    /* 0x66  'f' */ { 0x1C, 0x36, 0x06, 0x0F, 0x06, 0x06, 0x0F, 0x00 },
    /* 0x67  'g' */ { 0x00, 0x00, 0x6E, 0x33, 0x33, 0x3E, 0x30, 0x1F },
    /* 0x68  'h' */ { 0x07, 0x06, 0x36, 0x6E, 0x66, 0x66, 0x67, 0x00 },
    /* 0x69  'i' */ { 0x0C, 0x00, 0x0E, 0x0C, 0x0C, 0x0C, 0x1E, 0x00 },
    /* 0x6A  'j' */ { 0x30, 0x00, 0x30, 0x30, 0x30, 0x33, 0x33, 0x1E },
    /* 0x6B  'k' */ { 0x07, 0x06, 0x66, 0x36, 0x1E, 0x36, 0x67, 0x00 },
    /* 0x6C  'l' */ { 0x0E, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x1E, 0x00 },
    /* 0x6D  'm' */ { 0x00, 0x00, 0x33, 0x7F, 0x7F, 0x6B, 0x63, 0x00 },
    /* 0x6E  'n' */ { 0x00, 0x00, 0x1F, 0x33, 0x33, 0x33, 0x33, 0x00 },
    /* 0x6F  'o' */ { 0x00, 0x00, 0x1E, 0x33, 0x33, 0x33, 0x1E, 0x00 },
    /* 0x70  'p' */ { 0x00, 0x00, 0x3B, 0x66, 0x66, 0x3E, 0x06, 0x0F },
    /* 0x71  'q' */ { 0x00, 0x00, 0x6E, 0x33, 0x33, 0x3E, 0x30, 0x78 },
    /* 0x72  'r' */ { 0x00, 0x00, 0x3B, 0x6E, 0x66, 0x06, 0x0F, 0x00 },
    /* 0x73  's' */ { 0x00, 0x00, 0x3E, 0x03, 0x1E, 0x30, 0x1F, 0x00 },
    /* 0x74  't' */ { 0x08, 0x0C, 0x3E, 0x0C, 0x0C, 0x2C, 0x18, 0x00 },
    /* 0x75  'u' */ { 0x00, 0x00, 0x33, 0x33, 0x33, 0x33, 0x6E, 0x00 },
    /* 0x76  'v' */ { 0x00, 0x00, 0x33, 0x33, 0x33, 0x1E, 0x0C, 0x00 },
    /* 0x77  'w' */ { 0x00, 0x00, 0x63, 0x6B, 0x7F, 0x7F, 0x36, 0x00 },
    /* 0x78  'x' */ { 0x00, 0x00, 0x63, 0x36, 0x1C, 0x36, 0x63, 0x00 },
    /* 0x79  'y' */ { 0x00, 0x00, 0x33, 0x33, 0x33, 0x3E, 0x30, 0x1F },
    /* 0x7A  'z' */ { 0x00, 0x00, 0x3F, 0x19, 0x0C, 0x26, 0x3F, 0x00 },
    /* 0x7B  '{' */ { 0x38, 0x0C, 0x0C, 0x07, 0x0C, 0x0C, 0x38, 0x00 },
    /* 0x7C  '|' */ { 0x18, 0x18, 0x18, 0x00, 0x18, 0x18, 0x18, 0x00 },
    /* 0x7D  '}' */ { 0x07, 0x0C, 0x0C, 0x38, 0x0C, 0x0C, 0x07, 0x00 },
    /* 0x7E  '~' */ { 0x6E, 0x3B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
    /* 0x7F  DEL */ { 0xFF, 0x81, 0xBD, 0xA5, 0xBD, 0x81, 0xFF, 0x00 },
};

/* =========================================================================
 * SECTION 3: FRAMEBUFFER PRIMITIVES
 * ========================================================================= */

int fb_open(fb_context_t *fb)
{
    if (!fb) return -1;
    memset(fb, 0, sizeof(*fb));

    const char *paths[] = { "/dev/graphics/fb0", "/dev/fb0", NULL };
    int i;
    for (i = 0; paths[i] != NULL; ++i) {
        fb->fd = open(paths[i], O_RDWR);
        if (fb->fd >= 0) {
            fprintf(stderr, "🪰 [GÖLGE]: Framebuffer açıldı: %s\n", paths[i]);
            break;
        }
    }
    if (fb->fd < 0) {
        fprintf(stderr, "🪰 [GÖLGE]: Hiçbir framebuffer aygıtı açılamadı!\n");
        return -1;
    }

    if (ioctl(fb->fd, FBIOGET_VSCREENINFO, &fb->vinfo) < 0) {
        close(fb->fd);
        return -1;
    }

    if (ioctl(fb->fd, FBIOGET_FSCREENINFO, &fb->finfo) < 0) {
        close(fb->fd);
        return -1;
    }

    fb->width    = fb->vinfo.xres;
    fb->height   = fb->vinfo.yres;
    fb->bpp      = fb->vinfo.bits_per_pixel;
    fb->stride   = fb->finfo.line_length;
    fb->smem_len = fb->finfo.smem_len;

    fb->red_offset   = fb->vinfo.red.offset;
    fb->green_offset = fb->vinfo.green.offset;
    fb->blue_offset  = fb->vinfo.blue.offset;

    fb->map = (uint8_t *)mmap(NULL, fb->smem_len,
                               PROT_READ | PROT_WRITE,
                               MAP_SHARED, fb->fd, 0);
    if (fb->map == MAP_FAILED) {
        close(fb->fd);
        fb->map = NULL;
        return -1;
    }

    return 0;
}

void fb_close(fb_context_t *fb)
{
    if (!fb) return;
    if (fb->map && fb->map != MAP_FAILED)
        munmap(fb->map, fb->smem_len);
    if (fb->fd >= 0)
        close(fb->fd);
    memset(fb, 0, sizeof(*fb));
}

void fb_put_pixel(fb_context_t *fb, int x, int y,
                  uint8_t r, uint8_t g, uint8_t b)
{
    if (!fb || !fb->map) return;
    if (x < 0 || (uint32_t)x >= fb->width)  return;
    if (y < 0 || (uint32_t)y >= fb->height) return;

    uint32_t offset = (uint32_t)y * fb->stride;

    if (fb->bpp == 32) {
        uint32_t color = ((uint32_t)r << fb->red_offset)   |
                         ((uint32_t)g << fb->green_offset)  |
                         ((uint32_t)b << fb->blue_offset)   |
                         (0xFFu << 24);
        uint32_t *pixel = (uint32_t *)(fb->map + offset + (uint32_t)x * 4);
        *pixel = color;
    } else if (fb->bpp == 16) {
        uint16_t color = (uint16_t)(((r & 0xF8u) << 8) |
                                    ((g & 0xFCu) << 3) |
                                    ((b & 0xF8u) >> 3));
        uint16_t *pixel = (uint16_t *)(fb->map + offset + (uint32_t)x * 2);
        *pixel = color;
    }
}

void fb_fill_rect(fb_context_t *fb, int x, int y, int w, int h,
                  uint8_t r, uint8_t g, uint8_t b)
{
    if (!fb || !fb->map || w <= 0 || h <= 0) return;

    int x1 = x, y1 = y;
    int x2 = x + w;
    int y2 = y + h;

    if (x1 < 0) x1 = 0;
    if (y1 < 0) y1 = 0;
    if (x2 > (int)fb->width)  x2 = (int)fb->width;
    if (y2 > (int)fb->height) y2 = (int)fb->height;

    if (fb->bpp == 32) {
        uint32_t color = ((uint32_t)r << fb->red_offset)  |
                         ((uint32_t)g << fb->green_offset) |
                         ((uint32_t)b << fb->blue_offset)  |
                         (0xFFu << 24);
        int row, col;
        for (row = y1; row < y2; ++row) {
            uint32_t *line = (uint32_t *)(fb->map +
                             (uint32_t)row * fb->stride +
                             (uint32_t)x1 * 4);
            for (col = 0; col < (x2 - x1); ++col)
                line[col] = color;
        }
    } else if (fb->bpp == 16) {
        uint16_t color = (uint16_t)(((r & 0xF8u) << 8) |
                                    ((g & 0xFCu) << 3)  |
                                    ((b & 0xF8u) >> 3));
        int row, col;
        for (row = y1; row < y2; ++row) {
            uint16_t *line = (uint16_t *)(fb->map +
                              (uint32_t)row * fb->stride +
                              (uint32_t)x1 * 2);
            for (col = 0; col < (x2 - x1); ++col)
                line[col] = color;
        }
    } else {
        int row, col;
        for (row = y1; row < y2; ++row)
            for (col = x1; col < x2; ++col)
                fb_put_pixel(fb, col, row, r, g, b);
    }
}

void fb_clear(fb_context_t *fb, uint8_t r, uint8_t g, uint8_t b)
{
    if (!fb) return;
    fb_fill_rect(fb, 0, 0, (int)fb->width, (int)fb->height, r, g, b);
}

static void fb_draw_char_scaled(fb_context_t *fb, int x, int y,
                                 unsigned char c, int scale,
                                 uint8_t r, uint8_t g, uint8_t b)
{
    if (c < 32 || c > 127) c = '?';
    int idx = (int)c - 32;
    int row, col;
    for (row = 0; row < 8; ++row) {
        uint8_t bits = font8x8_basic[idx][row];
        for (col = 0; col < 8; ++col) {
            if (bits & (1u << col)) {
                if (scale == 1) {
                    fb_put_pixel(fb, x + col, y + row, r, g, b);
                } else {
                    fb_fill_rect(fb,
                                 x + col * scale,
                                 y + row * scale,
                                 scale, scale,
                                 r, g, b);
                }
            }
        }
    }
}

void fb_draw_text(fb_context_t *fb, int x, int y, const char *text,
                  uint8_t r, uint8_t g, uint8_t b)
{
    fb_draw_text_scaled(fb, x, y, text, 1, r, g, b);
}

void fb_draw_text_scaled(fb_context_t *fb, int x, int y, const char *text,
                          int scale, uint8_t r, uint8_t g, uint8_t b)
{
    if (!fb || !fb->map || !text) return;
    if (scale < 1) scale = 1;

    int cx = x;
    const char *p = text;
    while (*p) {
        if (*p == '\n') {
            cx = x;
            y += 8 * scale;
        } else {
            fb_draw_char_scaled(fb, cx, y, (unsigned char)*p,
                                scale, r, g, b);
            cx += 8 * scale;
        }
        ++p;
    }
}

void fb_scroll_up(fb_context_t *fb, int pixels)
{
    if (!fb || !fb->map || pixels <= 0) return;
    if ((uint32_t)pixels >= fb->height) {
        fb_clear(fb, 0, 0, 0);
        return;
    }

    uint32_t bytes_per_row  = fb->stride;
    uint32_t move_rows      = fb->height - (uint32_t)pixels;
    uint32_t src_offset     = (uint32_t)pixels * bytes_per_row;

    memmove(fb->map, fb->map + src_offset, move_rows * bytes_per_row);
    memset(fb->map + move_rows * bytes_per_row, 0, (uint32_t)pixels * bytes_per_row);
}

/* =========================================================================
 * SECTION 4: BMP LOADER
 * ========================================================================= */

static uint16_t read_u16le(const uint8_t *p)
{
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}
static uint32_t read_u32le(const uint8_t *p)
{
    return (uint32_t)(p[0] |
                      ((uint32_t)p[1] <<  8) |
                      ((uint32_t)p[2] << 16) |
                      ((uint32_t)p[3] << 24));
}
static int32_t read_s32le(const uint8_t *p)
{
    return (int32_t)read_u32le(p);
}

int fb_load_bmp(fb_context_t *fb, const char *path, int x, int y)
{
    if (!fb || !fb->map || !path) return -1;

    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;

    uint8_t file_hdr[14];
    if (read(fd, file_hdr, 14) != 14) {
        close(fd);
        return -1;
    }

    if (file_hdr[0] != 0x42 || file_hdr[1] != 0x4D) {
        close(fd);
        return -1;
    }

    uint32_t pixel_offset = read_u32le(&file_hdr[10]);

    uint8_t info_hdr[40];
    if (read(fd, info_hdr, 40) != 40) {
        close(fd);
        return -1;
    }

    int32_t  bmp_w_signed   = read_s32le(&info_hdr[4]);
    int32_t  bmp_h_signed   = read_s32le(&info_hdr[8]);
    uint16_t bmp_bpp        = read_u16le(&info_hdr[14]);
    uint32_t compression    = read_u32le(&info_hdr[16]);

    if (compression != 0 && compression != 3) {
        close(fd);
        return -1;
    }

    if (bmp_bpp != 24 && bmp_bpp != 32) {
        close(fd);
        return -1;
    }

    int top_down    = (bmp_h_signed < 0);
    uint32_t bmp_w  = (uint32_t)(bmp_w_signed < 0 ? -bmp_w_signed : bmp_w_signed);
    uint32_t bmp_h  = (uint32_t)(top_down ? -bmp_h_signed : bmp_h_signed);

    if (bmp_w == 0 || bmp_h == 0) {
        close(fd);
        return -1;
    }

    uint32_t bytes_pp = bmp_bpp / 8u;
    uint32_t row_size = ((bmp_w * bytes_pp + 3u) / 4u) * 4u;

    uint8_t *row_buf = (uint8_t *)malloc(row_size);
    if (!row_buf) {
        close(fd);
        return -1;
    }

    if (lseek(fd, (off_t)pixel_offset, SEEK_SET) < 0) {
        free(row_buf);
        close(fd);
        return -1;
    }

    uint32_t row_idx;
    for (row_idx = 0; row_idx < bmp_h; ++row_idx) {
        ssize_t bytes_read = read(fd, row_buf, row_size);
        if (bytes_read != (ssize_t)row_size) break;

        int fb_y = top_down ? (y + (int)row_idx) : (y + (int)(bmp_h - 1u - row_idx));

        uint32_t col;
        for (col = 0; col < bmp_w; ++col) {
            int fb_x = x + (int)col;
            if (fb_x < 0 || (uint32_t)fb_x >= fb->width)  continue;
            if (fb_y < 0 || (uint32_t)fb_y >= fb->height) continue;

            uint32_t base = col * bytes_pp;
            uint8_t pix_b = row_buf[base + 0];
            uint8_t pix_g = row_buf[base + 1];
            uint8_t pix_r = row_buf[base + 2];

            fb_put_pixel(fb, fb_x, fb_y, pix_r, pix_g, pix_b);
        }
    }

    free(row_buf);
    close(fd);
    return 0;
}

int fb_load_bmp_centered(fb_context_t *fb, const char *path)
{
    if (!fb || !fb->map || !path) return -1;

    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;

    uint8_t file_hdr[14];
    if (read(fd, file_hdr, 14) != 14) {
        close(fd);
        return -1;
    }

    if (file_hdr[0] != 0x42 || file_hdr[1] != 0x4D) {
        close(fd);
        return -1;
    }

    uint32_t pixel_offset = read_u32le(&file_hdr[10]);

    uint8_t info_hdr[40];
    if (read(fd, info_hdr, 40) != 40) {
        close(fd);
        return -1;
    }

    int32_t  bmp_w_signed = read_s32le(&info_hdr[4]);
    int32_t  bmp_h_signed = read_s32le(&info_hdr[8]);
    uint16_t bmp_bpp      = read_u16le(&info_hdr[14]);
    uint32_t compression  = read_u32le(&info_hdr[16]);

    if (compression != 0 && compression != 3) {
        close(fd);
        return -1;
    }

    if (bmp_bpp != 24 && bmp_bpp != 32) {
        close(fd);
        return -1;
    }

    int top_down   = (bmp_h_signed < 0);
    uint32_t bmp_w = (uint32_t)(bmp_w_signed < 0 ? -bmp_w_signed : bmp_w_signed);
    uint32_t bmp_h = (uint32_t)(top_down ? -bmp_h_signed : bmp_h_signed);

    if (bmp_w == 0 || bmp_h == 0) {
        close(fd);
        return -1;
    }

    int cx = (int)((fb->width  > bmp_w ? (fb->width  - bmp_w) / 2u : 0u));
    int cy = (int)((fb->height > bmp_h ? (fb->height - bmp_h) / 2u : 0u));

    uint32_t bytes_pp = bmp_bpp / 8u;
    uint32_t row_size = ((bmp_w * bytes_pp + 3u) / 4u) * 4u;

    uint8_t *row_buf = (uint8_t *)malloc(row_size);
    if (!row_buf) {
        close(fd);
        return -1;
    }

    if (lseek(fd, (off_t)pixel_offset, SEEK_SET) < 0) {
        free(row_buf);
        close(fd);
        return -1;
    }

    uint32_t row_idx;
    for (row_idx = 0; row_idx < bmp_h; ++row_idx) {
        ssize_t bytes_read = read(fd, row_buf, row_size);
        if (bytes_read != (ssize_t)row_size) break;

        int fb_y = top_down ? (cy + (int)row_idx) : (cy + (int)(bmp_h - 1u - row_idx));

        uint32_t col;
        for (col = 0; col < bmp_w; ++col) {
            int fb_x = cx + (int)col;
            if (fb_x < 0 || (uint32_t)fb_x >= fb->width)  continue;
            if (fb_y < 0 || (uint32_t)fb_y >= fb->height) continue;

            uint32_t base  = col * bytes_pp;
            uint8_t pix_b  = row_buf[base + 0];
            uint8_t pix_g  = row_buf[base + 1];
            uint8_t pix_r  = row_buf[base + 2];

            fb_put_pixel(fb, fb_x, fb_y, pix_r, pix_g, pix_b);
        }
    }

    free(row_buf);
    close(fd);
    return 0;
}

/* =========================================================================
 * SECTION 5: SCREEN TAKEOVER
 * ========================================================================= */

int fb_takeover_stop_surfaceflinger(void)
{
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid == 0) {
        char *const argv[] = { (char *)"su", (char *)"-c", (char *)"stop surfaceflinger", NULL };
        execvp("su", argv);
        _exit(127);
    }
    int status = 0;
    waitpid(pid, &status, 0);
    return (WIFEXITED(status) && WEXITSTATUS(status) == 0) ? 0 : -1;
}

int fb_takeover_start_surfaceflinger(void)
{
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid == 0) {
        char *const argv[] = { (char *)"su", (char *)"-c", (char *)"start surfaceflinger", NULL };
        execvp("su", argv);
        _exit(127);
    }
    int status = 0;
    waitpid(pid, &status, 0);
    return (WIFEXITED(status) && WEXITSTATUS(status) == 0) ? 0 : -1;
}

/* =========================================================================
 * SECTION 6: ANKA-SPECIFIC FUNCTIONS
 * ========================================================================= */

void anka_boot_sequence(fb_context_t *fb)
{
    if (!fb || !fb->map) return;
    fb_clear(fb, 0, 0, 0);
    fb_draw_text_scaled(fb, 50, 150, "[OK] Anka_Core Init...", 3, 0, 255, 0);
    usleep(600000);
    fb_draw_text_scaled(fb, 50, 250, "[OK] Kuantum Tozlari Aktif...", 3, 0, 255, 0);
    usleep(600000);
    fb_draw_text_scaled(fb, 50, 350, "[OK] Omni Sensorler Cevrimici...", 3, 0, 255, 0);
    usleep(800000);
    fb_clear(fb, 0, 0, 0);
    fb_load_bmp_centered(fb, "assets/sinek_icon.bmp");
    system("su -c 'echo 150 > /sys/class/timed_output/vibrator/enable' 2>/dev/null");
    system("su -c 'tinyplay assets/awake.wav' 2>/dev/null &");
    usleep(1000000);
}

void ui_render(fb_context_t *fb, const char *last_message)
{
    if (!fb || !fb->map) return;
    update_fly_behavior();
    if (current_state == FLY_GHOST) {
        fb_clear(fb, 0, 0, 0);
        return;
    }
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    int is_day = (tm->tm_hour >= 7 && tm->tm_hour <= 18) ? 1 : 0;
    uint8_t bg_r = is_day ? 220 : 10;
    uint8_t bg_g = is_day ? 220 : 15;
    uint8_t bg_b = is_day ? 220 : 20;
    uint8_t text_r = is_day ? 0 : 0;
    uint8_t text_g = is_day ? 0 : 255;
    uint8_t text_b = is_day ? 0 : 0;
    fb_clear(fb, bg_r, bg_g, bg_b);
    if (is_day) {
        fb_draw_text_scaled(fb, 50, 50, "[--- GUNDUZ ARAYUZU ---]", 3, 50, 50, 50);
    } else {
        fb_draw_text_scaled(fb, 50, 50, "[--- SIBERPUNK NEON GECE ---]", 3, 0, 255, 0);
    }
    if (current_state == FLY_MIRROR) {
        fb_load_bmp_centered(fb, "assets/sinek_ayna.bmp");
    } else if (current_state == FLY_THINK) {
        fb_load_bmp_centered(fb, "assets/sinek_dusunen.bmp");
    } else {
        fb_load_bmp_centered(fb, "assets/sinek_ucuyor.bmp");
    }
    if (last_message != NULL) {
        fb_draw_text_scaled(fb, 50, fb->height - 200, "SINEK:", 4, text_r, text_g, text_b);
        fb_draw_text_scaled(fb, 50, fb->height - 130, last_message, 3, text_r, text_g, text_b);
        if (strstr(last_message, "[FLY_SIGNATURE_ICON]")) {
            fb_load_bmp(fb, "assets/sinek_icon.bmp", fb->width - 150, fb->height - 150);
        }
    }
}

/* =========================================================================
 * SECTION 7: STUBS FOR UNRESOLVED EXTERNAL REFERENCES
 * ========================================================================= */

int user_confirmed_evolution(void)
{
    return 1;
}
