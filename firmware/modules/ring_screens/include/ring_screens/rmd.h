/*
 * Ring memory display: the display driver that keeps the frame it receives (RGB565, 120 x 240, the panel's
 * native size). The functions below read it back for the test hook and inject a failure for the R-SIGN test.
 */
#ifndef RING_SCREENS_RMD_H
#define RING_SCREENS_RMD_H

#include <stdbool.h>
#include <stdint.h>
#include <zephyr/device.h>
#include <zephyr/kernel.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RMD_W 120
#define RMD_H 240

struct rmd_stats {
	uint32_t writes;        /* accepted display_write calls */
	uint32_t refused;       /* display_write calls that returned an error */
	uint32_t blank_on;      /* blanking_on calls */
	uint32_t blank_off;     /* blanking_off calls */
	uint32_t brightness;    /* last display_set_brightness value */
	bool blanked;           /* the display is blanked now */
};

/* The frame as the panel holds it: RMD_W x RMD_H, row by row, host byte order of each RGB565 pixel. */
const uint16_t *rmd_frame(void);
void rmd_stats_get(struct rmd_stats *s);
/* The next n display_write calls fail with -EIO (n = -1: all of them until rmd_inject_fail(0)). */
void rmd_inject_fail(int n);
/* The thread that made the last accepted display_write (a test hook: who draws) */
k_tid_t rmd_last_writer(void);
/* A hash (FNV-1a 64) of the frame as the panel holds it */
uint64_t rmd_hash(void);

#ifdef __cplusplus
}
#endif

#endif
