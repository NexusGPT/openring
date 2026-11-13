/* tst.h: helpers shared by the suites of tests/store (unit U2). */
#ifndef TST_H
#define TST_H

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>
#include <ring_store/rst.h>

#include "rst_fmt.h"
#include "rst_layout.h"
#include "rst_log.h"

/* A bit-wise CRC-32 (ISO-HDLC, reflected polynomial) written for the tests: the expected values never come from the
 * code under test (which calls the C library's crc32_ieee). */
uint32_t tst_crc32(const uint8_t *d, size_t n);

/* Little-endian writes at typed offsets, for the expected bytes the tests write out by hand from design/firmware.md */
void tst_le(uint8_t *buf, unsigned off, uint64_t v, unsigned bytes);

/* Both suites' common start: the simulated drivers back to the start values and the store started again. */
void tst_reset(void);
void tst_reset_cb(const struct rst_cb *cb);
/* A power cycle of the ring: the card is kept, the store's RAM state is gone, the store is started again. */
void tst_reboot(void);
/* A card with this many chunks in the chunk area (sectors = 81,920 + 65 x chunks). */
void tst_card(uint32_t chunks);
/* mounts as BOOT does */
void tst_mount_boot(struct rst_mount_info *mi);

/* A chunk of 8,192 frames with a payload pattern that depends on seed and in_rec, header fields filled as audio does. */
void tst_fill(struct rst_chunk *c, uint32_t rec_id, uint32_t in_rec, uint32_t frames, uint32_t seed);

/* Chunk completion counters for rst_put_chunk(). */
void tst_done_cb(struct rst_chunk *c, int err);
int tst_done_count(void);
int tst_done_last_err(void);
void tst_done_reset(void);
/* waits (simulated time) until n completions were counted; false after timeout_ms */
bool tst_wait_done(int n, uint32_t timeout_ms);

/* open + chunks of full size + close of one recording, on a mounted store. digest = the digest typed by the test's
 * own reference code. Returns 0 or the first error. */
int tst_record(uint8_t type, uint32_t nchunks, uint32_t *id, uint32_t *digest);

/* the digest of chunks filled with tst_fill(c, id, i, 8192, seed = i), computed with the reference CRC */
uint32_t tst_ref_digest(uint32_t id, uint32_t nchunks);

/* ---- a small RAM disk for the pure suites (sectors by LBA, unwritten read as zero) */
void rd_reset(void);
int rd_read(void *ctx, uint32_t lba, uint8_t *buf, uint32_t count);
void rd_write(uint32_t lba, const uint8_t *buf, uint32_t count);
void rd_fail_at(uint32_t lba);     /* a read that covers it fails with -EIO; UINT32_MAX clears */

/* the `before` of every suite that may use the simulated card (written out in each file: twister reads the suite name
 * from the ZTEST_SUITE line, not from a macro) */
void tst_before(void *f);

#endif
