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
	/* fix round 2 (R2-08): GET_LOG holds the store about 6 s, longer than one 5,000 ms wait, so neither wait alone
	 * (the abort's wait for the command, the waiting unmount) keeps VDD_SD from staying on */
	transfer_with_busy_store(1000, 6);
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

/* ------------------------------------------------------------------ fix round 2 (review 2: R2-01, R2-02, R2-03) */
static K_SEM_DEFINE(retry_seen, 0, 1);
static K_SEM_DEFINE(retry_go, 0, 1);

static void retry_hook(void)
{
	k_sem_give(&retry_seen);
	(void)k_sem_take(&retry_go, K_SECONDS(30));
}

/* R2-01: VBUS removed while GET_LOG holds the store longer than both waits: the unmount fails, its retry is queued. The
 * retry job is held at its start; meanwhile the wearer starts a recording (STANDBY -> RECORDING, FW l.144). When the
 * retry goes on it must not take the card of the recording (it decides under the glue's lock, from the state then) */
ZTEST(recorder_unmount, test_retry_never_takes_the_card)
{
	struct rrec_tap_rec t;
	int n = 0;
	int32_t err[4] = { 1, 1, 1, 1 };
	uint8_t tries[4] = { 0 };

	transfer_with_busy_store(2000, 6);
	rrec_tap_clear();
	rrec_test_set_retry_hook(retry_hook);
	k_sem_reset(&retry_seen);
	k_sem_reset(&retry_go);
	rhw_sim_vbus(false);
	zassert_equal(k_sem_take(&retry_seen, K_SECONDS(30)), 0, "the retry job came");
	zassert_equal(rt_state(), RC_ST_STANDBY, "STANDBY (FW l.179)");
	zassert_true(rt_sd(), "the unmount failed: VDD_SD still on");
	for (int i = 0; i < 300 && rxf_busy(); i++) {
		rt_sleep(100);
	}
	rglue_input(RC_SW_CENTRE, true);   /* the long press (FW l.128) while the retry waits */
	rt_sleep(1100);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(200);
	zassert_equal(rt_state(), RC_ST_RECORDING, "RECORDING");
	rrec_test_set_retry_hook(NULL);
	k_sem_give(&retry_go);
	rt_sleep(3000);
	rt_settle();
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_UNMOUNT_FAILED && n < 4) {
			err[n] = (int32_t)sys_get_le32(t.args);
			tries[n] = t.args[5];
			n++;
		}
	}
	TC_PRINT("retry: state %s, VDD_SD %d, records 0x0290 %d: (%d, try %u), (%d, try %u)\n", rc_state_name(rt_state()),
		 rt_sd(), n, err[0], tries[0], err[1], tries[1]);
	zassert_equal(rt_state(), RC_ST_RECORDING, "the recording goes on (its card was not taken)");
	zassert_true(rt_sd(), "VDD_SD on in RECORDING (FW l.917)");
	zassert_true(n >= 1 && err[0] == -EBUSY, "the failed try was logged (FW l.1234)");
	rt_long();
	command_ended();
}

/* R2-02: the episode starts in CHARGING (row 46 while GET_LOG holds the store), and while the store is still held the
 * state wants the card again (TRANSFER, row 39, FW l.171): the end record carries this episode's last errno (-EBUSY),
 * never a 0 (FW l.1234: "0 when the unmount then succeeded, else the last errno") */
ZTEST(recorder_unmount, test_episode_end_keeps_its_errno)
{
	struct rrec_tap_rec t;
	int n = 0;
	int32_t err[4] = { 1, 1, 1, 1 };
	uint8_t st[4] = { 0 };

	transfer_with_busy_store(3000, 6);
	rrec_tap_clear();
	rglue_event(RC_EV_USB_UNCONFIGURED);   /* row 46: the finish and the unmount wait 5 s each, the unmount fails */
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING");
	zassert_true(rt_sd(), "VDD_SD still on (the store is held)");
	rglue_event(RC_EV_USB_CONFIGURED);     /* row 39: TRANSFER wants the card again; the store is still held */
	zassert_equal(rt_state(), RC_ST_TRANSFER, "TRANSFER");
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_UNMOUNT_FAILED && n < 4) {
			err[n] = (int32_t)sys_get_le32(t.args);
			st[n] = t.args[4];
			n++;
		}
	}
	TC_PRINT("episode end: records 0x0290 %d: (%d, %s), (%d, %s), store busy %d\n", n, err[0],
		 rc_state_name((enum rc_state)st[0]), err[1], rc_state_name((enum rc_state)st[1]), rxf_busy());
	zassert_equal(n, 2, "the first failed try and the end of the episode");
	zassert_equal(err[0], -EBUSY, "first: -EBUSY");
	zassert_equal(err[1], -EBUSY, "end: the episode's last errno, not 0");
	command_ended();
}

/* R2-03: one step waits at most once for the command (5,000 ms) and once for the unmount (5,000 ms): the glue's lock is
 * free again within 10 s plus the unmount's own time, although the store is held about 20 s */
ZTEST(recorder_unmount, test_one_wait_each_per_step)
{
	int64_t t0, held;

	transfer_with_busy_store(3000, 7);
	t0 = k_uptime_get();
	rglue_event(RC_EV_USB_UNCONFIGURED);   /* row 46 on this thread: the step's finish wait times out, then its unmount */
	held = -1;
	for (uint32_t i = 0; i < rt_steps(); i++) {
		if (rt_step_get(i).row == 46) {
			held = rt_step_get(i).t_end_ms - t0;
		}
	}
	TC_PRINT("one wait each: the step of row 46 held the glue's lock %lld ms\n", held);
	zassert_true(held >= 0, "row 46 taken");
	zassert_true(held < 10000 + 1500, "at most one wait for the command and one for the unmount (%lld ms)", held);
	command_ended();
	for (int i = 0; i < 100 && rt_sd(); i++) {
		rt_sleep(100);
	}
	zassert_false(rt_sd(), "the retry job unmounted in the end");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_unmount, NULL, setup, NULL, NULL, NULL);
