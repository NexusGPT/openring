/* Helpers shared by the suites of tests/audio (software step 6, unit U3). Every expected value in the suites is a
 * literal written from design/firmware.md (the line is cited at each case), never produced by the code under test. */
#ifndef AUDIO_TEST_COMMON_H
#define AUDIO_TEST_COMMON_H

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_audio/rau.h>
#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>

#include "rau_chunk.h"

/* ------------------------------------------------------------------ the pure part's test ops: a pool of chunk buffers */
#define T_POOL 10
void t_reset(void);                        /* pool dirty (0xA5), counters zero, facts default */
const struct rac_ops *t_ops(void);
int t_fulls(void);                         /* chunks handed over by rac_block so far */
struct rst_chunk *t_full(int i);
int t_dropouts(void);                      /* dropout callbacks so far */
uint32_t t_dropout_chunk(int i);
uint8_t t_dropout_block(int i);
void t_facts(uint16_t mv, int16_t temp, uint32_t fw, bool b15);   /* what the next chunk's start gets; mv += 1 per chunk */
struct rac_start t_start(bool time_set, int64_t start_ms, uint64_t start_cycles, uint32_t hz);
/* feed blocks first..first+n-1 of the frame-counter source (left = frame number since the PDM start, 16 bits,
 * right = its bitwise inverse) */
void t_feed(struct rac *s, uint32_t first, uint32_t n);
/* feed one block of the counter source, but with the one chosen sample forced to a value */
void t_feed_block_with(struct rac *s, uint32_t k, uint32_t frame_in_block, int channel, int16_t v);
/* left and right sample of kept frame i of a chunk's payload */
int16_t t_left(const struct rst_chunk *c, uint32_t i);
int16_t t_right(const struct rst_chunk *c, uint32_t i);
/* the counter source's value at raw frame f since the PDM start */
int16_t t_counter_left(uint32_t f);
/* check that all unused payload bytes after `frames` frames are zero */
bool t_tail_zero(const struct rst_chunk *c, uint32_t frames);

/* ------------------------------------------------------------------ stand-in for the store's chunk hand-off */
#define SI_MAX 12
void si_reset(void);
void si_hold(bool hold);                   /* true: chunks are never reported written until si_complete() */
void si_enobufs_after(int n);              /* the (n+1)th put and later return -ENOBUFS; -1 = never */
int si_puts(void);
const struct rst_chunk *si_copy(int i);    /* the chunk as it was when put */
const struct rst_chunk *si_live(int i);    /* the buffer the audio part handed over, as it is now */
void si_complete(int i);
void si_complete_all(void);
int si_put(struct rst_chunk *c, rst_chunk_done_fn done);

/* ------------------------------------------------------------------ the thin part on the simulated input */
struct svc_events {
	int dropouts;
	uint32_t dr_rec, dr_chunk;
	uint8_t dr_block;
	int no_block;
	int64_t no_block_ms;
};
extern struct svc_events svc_ev;
extern uint32_t svc_fw_version;
void svc_setup(void);                      /* rhw_sim_reset, stand-in reset, rau_init with the callbacks below */
void svc_cleanup(void);
/* rails on (as the join does), HFXO, 1 ms, rau_start; returns the uptime ms of the PDM start */
int64_t svc_begin(bool time_set, bool b15);
/* index in the simulated event log of the first entry of this kind at or after `from`, or -1 */
int32_t ev_find(uint16_t kind, uint32_t from);
int64_t ev_t_us(int32_t idx);
int64_t ev_a0(int32_t idx);

#endif
