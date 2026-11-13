/*
 * recorder_unmount: VDD_SD off when TRANSFER is left while a command uses the store (step 6 fix round 1, review finding
 * R6-03): design/firmware.md l.178 ("finish the current command; VDD_SD off"), l.179 ("abort the command; VDD_SD off"),
 * and 8.2 (l.912 to l.920: VDD_SD off in STANDBY and CHARGING). The simulated card stalls only its writes
 * (rhw_sim_disk_stall_ms); a stalled chunk READ is not simulated. The "read command" is GET_LOG (FW l.706, lead's ruling),
 * whose store call first writes the queued event log records, so with queued records and a stalled card it holds the
 * store for the stall times the records.
 * The transfer part runs its bus events on the transfer thread after the command that runs (rxf_class.c), so "unconfigured
 * while a command runs" does not reach the core through the class until the command ended; the cases of l.178 give the
 * core the event themselves (rglue_event, as the cases of the Bluetooth highlight do) while GET_LOG holds the store.
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#include <ring_store/rst.h>
#include <ring_xfer/rxf.h>

#include "rt.h"

/* a TRANSFER with the card mounted, then `records` event log records queued on a card that stalls each write by
 * `stall_ms`, then GET_LOG sent (not waited for) */
static void transfer_with_busy_store(uint32_t stall_ms, int records)
{
	uint8_t pl[RREC_GET_LOG_REQ_BYTES];
	uint8_t a[4] = { 0 };

	rt_fresh(NULL);
	rt_vbus(true);
	rt_usb_configured();
	zassert_equal(rt_state(), RC_ST_TRANSFER, "TRANSFER");
	zassert_true(rt_sd(), "VDD_SD on in TRANSFER");
	rhw_sim_disk_stall_ms(stall_ms);
	for (int i = 0; i < records; i++) {
		a[0] = (uint8_t)i;
		rrec_log(RREC_LOG_BATTERY, a, sizeof(a));   /* records to write: the storage thread and GET_LOG write them */
	}
	sys_put_le32(1, pl);
	sys_put_le16(RREC_GET_LOG_MAX_MAX, &pl[4]);
	zassert_equal(rt_usb_send(RREC_OP_GET_LOG, pl, sizeof(pl)), 0, "GET_LOG sent");
	rt_sleep(100);
	zassert_true(rxf_busy(), "the command runs");
	rt_steps_clear();
	rhw_sim_log_clear();
}

/* the end of a case: the command ended (the transfer thread is free again) and the card no longer stalls */
static void command_ended(void)
{
	for (int i = 0; i < 600 && rxf_busy(); i++) {
		rt_sleep(100);
	}
	zassert_false(rxf_busy(), "the command ended");
	rhw_sim_disk_stall_ms(0);
	rt_settle();
}

/* the step of `row` ended with VDD_SD off: the rail went off inside that step (before its after-call), not in a later one */
static void sd_off_in_the_step(int row)
{
	int32_t i_off = rt_find_rail(RHW_RAIL_SD, false, 0);
	int64_t step_ms = -1;

	for (uint32_t i = 0; i < rt_steps(); i++) {
		if (rt_step_get(i).row == row) {
			step_ms = rt_step_get(i).t_ms;
			break;
		}
	}
	TC_PRINT("unmount: row %d step at %lld ms, VDD_SD off at %lld us, steps %u, VDD_SD now %d\n", row, step_ms,
		 rt_ev_us(i_off), rt_steps(), rt_sd());
	zassert_true(step_ms >= 0, "row %d taken", row);
	zassert_false(rt_sd(), "VDD_SD off when the step of row %d ended", row);
	zassert_true(i_off >= 0 && rt_ev_us(i_off) <= step_ms * 1000 + 1000, "VDD_SD went off inside the step of row %d",
		     row);
}

/* FW l.179: VBUS removed in TRANSFER while GET_LOG holds the store: abort, the command ends, VDD_SD off in that step */
ZTEST(recorder_unmount, test_vbus_out_during_read_command)
{
	transfer_with_busy_store(400, 6);
	rt_vbus(false);
	zassert_equal(rt_state(), RC_ST_STANDBY, "STANDBY (FW l.179)");
	sd_off_in_the_step(47);
	command_ended();
}

/* FW l.178: unconfigured in TRANSFER while GET_LOG holds the store longer than the finish waits (5,000 ms, the join's
 * bound): the finish times out, the unmount waits for the store call, VDD_SD off in that step */
ZTEST(recorder_unmount, test_unconfigured_finish_times_out)
{
	int64_t t0;

	transfer_with_busy_store(1300, 6);
	t0 = k_uptime_get();
	rglue_event(RC_EV_USB_UNCONFIGURED);
	rt_settle();
	TC_PRINT("unmount: the unconfigured step took about %lld ms\n", k_uptime_get() - t0);
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING (FW l.178)");
	sd_off_in_the_step(46);
	zassert_true(k_uptime_get() - t0 > 5000, "the finish timed out first (the command held the store longer)");
	zassert_true(rhw_sim_pmic_charger_on(), "charge on (FW l.178)");
	command_ended();
}

/* a store call longer than both waits: the failed unmount is reported (event log) and tried again until VDD_SD is off */
ZTEST(recorder_unmount, test_failed_unmount_retried_and_reported)
{
	struct rrec_tap_rec t;
	int busy = 0;
	bool order_ok = true;
	uint8_t first_state = 0xFF;

	rrec_tap_clear();
	transfer_with_busy_store(3000, 6);
	rrec_tap_clear();
	rglue_event(RC_EV_USB_UNCONFIGURED);
	for (int i = 0; i < 400 && rt_sd(); i++) {
		rt_sleep(100);
	}
	rt_settle();
	/* FW l.1234 (the code table, the lead's ruling): 0x0290 RREC_LOG_UNMOUNT_FAILED, errno i32, state u8, try u8, written
	 * at the FIRST failed try (its errno, try 1) and once when the tries end (errno 0 when the unmount then succeeded,
	 * try = the number of tries made) */
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_UNMOUNT_FAILED) {
			busy++;
			TC_PRINT("unmount: record %d: errno %d, state %s, try %u\n", busy, (int32_t)sys_get_le32(t.args),
				 rc_state_name((enum rc_state)t.args[4]), t.args[5]);
			if (busy == 1) {
				first_state = t.args[4];
				order_ok &= (int32_t)sys_get_le32(t.args) == -EBUSY && t.args[5] == 1;
			} else if (busy == 2) {
				order_ok &= (int32_t)sys_get_le32(t.args) == 0 && t.args[5] >= 2;
			}
		}
	}
	TC_PRINT("unmount: %d records 0x0290, VDD_SD now %d, state %s\n", busy, rt_sd(), rc_state_name(rt_state()));
	zassert_equal(RREC_LOG_UNMOUNT_FAILED, 0x0290, "the code of FW l.1234");
	zassert_equal(busy, 2, "two records for a step with several failed tries (%d)", busy);
	zassert_true(order_ok, "first: errno -EBUSY, try 1; second: errno 0, the number of tries (2 or more)");
	zassert_equal(first_state, RC_ST_TRANSFER, "the first try in the step of row 46 (from TRANSFER)");
	zassert_false(rt_sd(), "tried again until VDD_SD went off");
	zassert_false(rst_mounted(), "unmounted");
	command_ended();
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_unmount, NULL, setup, NULL, NULL, NULL);
