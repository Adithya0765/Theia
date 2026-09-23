/* Homestead K0 kernel — proof of life via framebuffer.
 * Pinned to Limine 7.x boot protocol (see build-kernel.sh).
 * No Linux code here: clean-room K0, ports come later with GPL eyes open.
 */
#include <stdint.h>
#include <stddef.h>
#include "limine.h"

__attribute__((used, section(".requests")))
static volatile LIMINE_BASE_REVISION(2);

__attribute__((used, section(".requests")))
static volatile struct limine_framebuffer_request framebuffer_request = {
    .id = LIMINE_FRAMEBUFFER_REQUEST,
    .revision = 0
};

__attribute__((used, section(".requests_start_marker")))
static volatile LIMINE_REQUESTS_START_MARKER;

__attribute__((used, section(".requests_end_marker")))
static volatile LIMINE_REQUESTS_END_MARKER;

static void hcf(void) {
    for (;;) {
        asm volatile ("hlt");
    }
}

void kmain(void) {
    if (LIMINE_BASE_REVISION_SUPPORTED == false) {
        hcf();
    }
    if (framebuffer_request.response == NULL ||
        framebuffer_request.response->framebuffer_count < 1) {
        hcf();
    }
    struct limine_framebuffer *fb = framebuffer_request.response->framebuffers[0];
    volatile uint32_t *fb_ptr = (volatile uint32_t *)fb->address;
    uint64_t stride = fb->pitch / 4;
    for (uint64_t y = 0; y < fb->height; y++) {
        for (uint64_t x = 0; x < fb->width; x++) {
            uint32_t r = (uint32_t)(x * 255 / fb->width);
            uint32_t g = (uint32_t)(y * 255 / fb->height);
            fb_ptr[y * stride + x] = r | (g << 8) | 0x00100000;
        }
    }
    hcf();
}
