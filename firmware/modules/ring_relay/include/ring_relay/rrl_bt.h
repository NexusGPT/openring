/*
 * Ring relay, Bluetooth part (design/firmware.md section 7.7): the GATT service a helper app on an Android phone writes
 * its notifications to. The service is registered at start (a static service, nothing to call), and the part registers
 * itself with the iPhone part at start (SYS_INIT), so an action chosen on the ring reaches the helper. The store is the
 * iPhone part's (rip_relay_* in ring_iphone/rip.h): one store for both sources.
 *
 * Nothing in this part includes or calls the core, the glue, the devices part, the control part or the screens, and it never wakes
 * the screen (tools/build_all.sh, stage relay-no-core, searches these sources for their names).
 *
 * Locks: one mutex of this part ("relay lock") guards the session and the queue of frames for Out. Order: relay lock, then
 * the iPhone part's lock. The iPhone part calls rrl_bt's action hook without its lock held.
 */
#ifndef RING_RELAY_RRL_BT_H
#define RING_RELAY_RRL_BT_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rrl_stats {
	uint32_t writes;          /* frames written to In that reached the part */
	uint32_t refused;         /* ... refused (any code) */
	uint32_t by_code[8];      /* refusals per code 1 to 7 (index 0 unused) */
	uint32_t hellos, puts, removes, clears; /* accepted */
	uint32_t pieces;          /* PUT pieces taken that did not finish a record */
	uint32_t sec_refused;     /* writes and reads that reached a handler below security level 4 (the host should stop these) */
	uint32_t out_sent, out_dropped, out_retries; /* frames notified on Out; dropped (no subscription, queue full for READY or ERROR, failed) */
	uint32_t actions_sent;    /* ACTION frames queued */
	uint32_t actions_refused; /* actions refused on the ring (no session, no subscription to Out, no room in the Out queue); counted here once, not in out_dropped */
	uint32_t link_ends;       /* links with a session that ended */
};

void rrl_stats_get(struct rrl_stats *out);

#ifdef CONFIG_RING_RELAY_TEST_HOOKS
/* Test ring only (never set in the product): block Out as if the controller had no buffer for a notification. Frames stay queued. */
void rrl_test_block_out(bool on);
#endif

#ifdef __cplusplus
}
#endif

#endif
