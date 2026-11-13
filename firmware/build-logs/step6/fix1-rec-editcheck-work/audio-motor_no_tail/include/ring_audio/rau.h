/*
 * rau.h: the audio part (software step 6, unit U3 builds it; U0 wrote this header, frozen: changes only through the
 * lead). The microphones of design/firmware.md section 4 ("FW l.N" = line N of that file).
 *
 * Pure part (rau_chunk.c: blocks into chunks, the 800-frame discard, zero fill, flags, highlights, motor intervals,
 * timestamps) is declared in the unit's own src/ header. This header is the thin part.
 *
 * Order of a start (FW l.455 to l.460, the join carries it out):
 *   rau_prepare()  (HFXO requested and running, FW l.456)
 *   rec_mics_on()  (ring_recorder: the sign, then VDD_MIC; FW l.457)
 *   k_sleep(RREC_MIC_RAIL_WAIT_MS)  (FW l.458)
 *   rau_start()    (configure, pins default, trigger; the first RREC_DISCARD_FRAMES frames dropped, FW l.459, l.460)
 * Order of a stop: "close" of FW l.125 (partial chunk, CLOSE record, superblock, stop PDM, clocks low, VDD_MIC off,
 * VDD_SD off) with the stop of FW l.463:
 *   rau_cut(mark)  (frames up to the mark kept, FW l.448; later frames dropped; returns the partial chunk)
 *   rst_close()    (partial chunk, CLOSE record, superblock)
 *   rau_halt()     (trigger STOP, blocks released, clock pins to the sleep state = clocks low)
 *   rec_mics_off() (VDD_MIC off), rau_release() (HFXO, after VDD_MIC, FW l.463), rst_unmount() (VDD_SD off)
 * Hardware only through rhw.h: rhw_mic(), rhw_hfxo(), rhw_clock(). The audio part never switches a rail.
 */
#ifndef RING_AUDIO_RAU_H
#define RING_AUDIO_RAU_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_rhw/rrec_spec.h>
#include <ring_store/rst.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rau_cb {
	/* Hand a full chunk to the store (FW l.443). NULL = rst_put_chunk. Audio thread. */
	int (*put)(struct rst_chunk *c, rst_chunk_done_fn done);
	/* No block for RREC_MIC_NO_BLOCK_MS while capturing (FW l.169). Audio thread; once per recording; must not block. */
	void (*no_block)(void);
	/* A block replaced by zeros (FW l.430: "is logged"). Audio thread; must not block. */
	void (*dropout)(uint32_t recording_id, uint32_t chunk_in_recording, uint8_t block);
	/* Battery, temperature and fw version for each chunk header (FW l.567 to l.571). Audio thread; must not block.
	 * NULL = zeros. */
	void (*chunk_facts)(uint16_t *battery_mv, int16_t *temp_c_x10, uint32_t *fw_version);
};

/* Start the audio thread and put the clock pins in their sleep state (FW l.465: at boot, before VDD_MIC is ever on).
 * Once, at boot. cb may be NULL. Blocks briefly. */
int rau_init(const struct rau_cb *cb);

/* Request HFXO and wait until it runs (FW l.428, l.456). 0; -ETIMEDOUT after timeout_ms (the request is released).
 * Caller's thread (the join's); blocks up to timeout_ms. */
int rau_prepare(int32_t timeout_ms);

struct rau_start_args {
	uint32_t recording_id;        /* from rst_open */
	uint8_t recording_type;       /* RREC_REC_TYPE_RECORDING or _FACTORY (FW l.1024) */
	uint32_t boot_count;          /* from rst_mount (FW l.569) */
	bool time_set;                /* false: flag bit 5 and utc_ms 0 in every chunk (FW l.547, l.1005) */
	int64_t utc_offset_ms;        /* utc = uptime ms + offset, when time_set */
	bool b15;                     /* the battery at B15 or under now (flag bit 6) */
};

/* Configure the input with the values of FW 4.1 (struct rhw_mic_cfg from rrec_spec.h numbers), pins default,
 * trigger START (FW l.429). The caller has switched VDD_MIC on through rec_mics_on() and waited 1 ms. 0, -EIO.
 * The recording's time is that of its first kept frame (FW l.460). Join's thread; blocks for the trigger only. */
int rau_start(const struct rau_start_args *a);

struct rau_cut_result {
	struct rst_chunk *last;       /* the partial chunk to give to rst_close, or NULL; valid until the next rau_start */
	struct rst_close_args close;  /* duration and highlights for the CLOSE record */
};

/* End the recording's audio at the long press mark (FW l.448: frames up to mark_ms kept, later ones dropped). Waits
 * until the block holding the mark has arrived; full chunks before it are handed to the store as usual. The PDM keeps
 * running until rau_halt. 0, -EIO. Join's thread; blocks up to RREC_MIC_NO_BLOCK_MS. */
int rau_cut(int64_t mark_ms, struct rau_cut_result *out);

/* Stop the input (FW l.463): trigger STOP, read until the input returns an error (blocks released), clock pins to the
 * sleep state. Returns when the caller may switch VDD_MIC off. 0, -EIO. Join's thread; blocks up to
 * RREC_BLOCK_COUNT x RREC_BLOCK_MS. Also the stop after a chunk write fault (FW l.168) and after "no block" (l.169). */
int rau_halt(void);

/* Release HFXO (FW l.463, after VDD_MIC is off). */
int rau_release(void);

/* A highlight at the time of CENTRE_DOWN of the short press, in uptime ms (FW l.159, l.582). Any thread (not an
 * interrupt); never blocks; ignored outside a capture. */
void rau_highlight(int64_t centre_down_ms);

/* A MOTOR edge (FW l.496): high or low, at this cycle count (rhw_clock()->cycles()). ANY context, the motor's timer
 * included; never blocks. Kept while capturing; the last edges before a start are kept too, so the M1 that starts
 * before the PDM is marked (FW l.497). */
void rau_motor_edge(bool high, uint64_t cycles);

/* The battery fact B15 for flag bit 6 of the next chunks (FW l.547). Any thread; never blocks. */
void rau_set_b15(bool b15);

/* true between rau_start and the end of rau_halt. Does not block. */
bool rau_capturing(void);  /* FW l.112 */

#ifdef __cplusplus
}
#endif

#endif
