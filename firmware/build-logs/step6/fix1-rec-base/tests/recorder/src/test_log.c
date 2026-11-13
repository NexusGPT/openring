/*
 * recorder_log: the event log records of the join (design/firmware.md l.1062, the codes of the section "Event log
 * codes", ruling R23; plan rows T27, C33, A10).
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#include "rt.h"

static uint32_t count_code(uint16_t code)
{
	return rrec_tap_count_code(code);
}

/* FW l.1062: each state change, fault, battery threshold and transfer command becomes a record (T27) */
ZTEST(recorder_log, test_each_kind_logged)
{
	static uint8_t resp[RREC_MSG_HEADER_BYTES + 2 + 4 * RREC_LOG_RECORD_BYTES];
	struct rrec_tap_rec t;
	uint32_t changes = 0, recs = 0;
	uint8_t pl[6] = { 0 };
	uint8_t st;
	int n;

	/* state changes: every step that changed the state has its record, from and to as the step says */
	rt_fresh(NULL);
	rt_long();
	rt_long();
	rt_vbus(true);
	rt_usb_configured();
	{
		uint8_t prev = RC_ST_BOOT;

		for (uint32_t i = 0; i < rt_steps(); i++) {
			struct rt_step s = rt_step_get(i);

			if (s.state != prev) {
				changes++;
				prev = s.state;
			}
		}
	}
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_STATE_CHANGE) {
			recs++;
		}
	}
	TC_PRINT("state changes %u, STATE_CHANGE records %u\n", changes, recs);
	zassert_true(changes >= 5, "BOOT, STANDBY, RECORDING, STANDBY, CHARGING, TRANSFER");
	zassert_equal(recs, changes, "one record per state change");
	/* a transfer command: code 0x0100 | opcode with its status */
	sys_put_le16(1, &pl[4]);
	n = rt_usb(RREC_OP_GET_LOG, pl, 6, resp, sizeof(resp), &st);
	zassert_equal(st, RREC_ST_OK, "GET_LOG answers");
	zassert_true(n > RREC_MSG_HEADER_BYTES + 2, "one record read back from the card");
	zassert_equal(sys_get_le32(&resp[RREC_MSG_HEADER_BYTES + 2 + RREC_LG_OFF_MAGIC]), RREC_LOG_MAGIC, "RRLG (FW l.1062)");
	zassert_equal(count_code(RREC_LOG_XFER_BASE | RREC_OP_GET_LOG), 1, "the command logged");
	/* faults: storage init (FW l.138), microphone (FW l.169), charger (FW l.176), chunk write (FW l.168) */
	zassert_equal(rt_run_row(6), 0, NULL);
	zassert_equal(count_code(RREC_LOG_FAULT_STORAGE_INIT), 1, "storage init fault");
	zassert_equal(rt_run_row(37), 0, NULL);
	zassert_equal(count_code(RREC_LOG_FAULT_MIC), 1, "microphone fault");
	zassert_equal(rt_run_row(44), 0, NULL);
	zassert_equal(count_code(RREC_LOG_FAULT_CHARGER), 1, "charger fault");
	zassert_equal(rt_run_row(36), 0, NULL);
	zassert_true(count_code(RREC_LOG_FAULT_CHUNK_WRITE) >= 1, "chunk write fault");
	/* a battery threshold (FW l.1062): B5 in STANDBY */
	zassert_equal(rt_run_row(22), 0, NULL);
	zassert_true(count_code(RREC_LOG_BATTERY) >= 1, "battery threshold");
	/* the sign refused (row FW l.148) */
	zassert_equal(rt_run_row(16), 0, NULL);
	rscr_test_force_down(false);
	zassert_equal(count_code(RREC_LOG_SIGN_REFUSED), 1, "sign refused");
	zassert_true(count_code(RREC_LOG_STATE_CHANGE) >= 1, "boot to STANDBY logged");
}

/* FW l.333: the pattern start time is logged (C33) */
ZTEST(recorder_log, test_pattern_start_logged)
{
	struct rrec_tap_rec t;
	bool m1 = false;
	int64_t t_open = -1;

	rt_fresh(NULL);
	rt_long();
	for (uint32_t i = 0; i < rt_acts(); i++) {
		if (rt_act_get(i).a == RC_ACT_M1) {
			t_open = rt_act_get(i).t_ms;
		}
	}
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_MOTOR_PATTERN && t.args[0] == RREC_PAT_M1) {
			m1 = true;
			int64_t tl = (int64_t)sys_get_le64(&t.args[1]);

			TC_PRINT("M1 action at %lld ms, start logged %lld ms\n", t_open, tl);
			zassert_true(tl >= t_open && tl <= t_open + 5, "the start time is that of the press (within 5 ms)");
		}
	}
	zassert_true(m1, "M1's start logged");
	rt_long();
}

/* FW l.448: at a stop the press start time is written to the event log (A10) */
ZTEST(recorder_log, test_stop_press_time_logged)
{
	struct rrec_tap_rec t;
	int64_t t_close = -1, t_press = -1;
	uint32_t id = 0;

	rt_fresh(NULL);
	rt_long();
	id = rrec_st.rec_id;
	rt_sleep(900);
	rt_long();
	for (uint32_t i = 0; i < rt_acts(); i++) {
		if (rt_act_get(i).a == RC_ACT_CLOSE) {
			t_close = rt_act_get(i).t_ms;
		}
	}
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_REC_STOP_PRESS) {
			zassert_equal(sys_get_le32(t.args), id, "the recording's id");
			t_press = (int64_t)sys_get_le64(&t.args[4]);
		}
	}
	TC_PRINT("stop press: fired at %lld ms, logged press start %lld ms\n", t_close, t_press);
	zassert_true(t_press >= 0, "logged");
	zassert_equal(t_close - t_press, 1000, "the press began 1,000 ms before the long press fired (FW l.128)");
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_log, NULL, setup, NULL, NULL, NULL);
