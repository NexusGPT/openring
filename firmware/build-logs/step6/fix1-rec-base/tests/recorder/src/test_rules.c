/*
 * recorder_rules: only a long press starts or stops a recording (design/firmware.md l.209; plan row C21). Every USB
 * opcode, and every factory sub-command, in every state where USB answers, with a check after each.
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#if defined(CONFIG_RING_FACTORY)
#include <ring_factory/rfa.h>
#endif

#include "rt.h"

static int bad;

/* after a command: no gesture reached the core, no recording started or stopped, VDD_MIC off */
static void check_after(const char *what, enum rc_state before)
{
	for (uint32_t i = 0; i < rt_steps(); i++) {
		struct rt_step s = rt_step_get(i);

		if (s.ev == RC_EV_LONG_PRESS || s.ev == RC_EV_SHORT_PRESS || s.ev == RC_EV_DOUBLE_PRESS) {
			TC_PRINT("RULES %s in %s: a press reached the core (row %d)\n", what, rc_state_name(before), s.row);
			bad++;
		}
	}
	for (uint32_t i = 0; i < rt_acts(); i++) {
		uint8_t a = rt_act_get(i).a;

		if (a == RC_ACT_OPEN || a == RC_ACT_CLOSE) {
			TC_PRINT("RULES %s in %s: action %s\n", what, rc_state_name(before), rc_action_name(a));
			bad++;
		}
	}
	if (rrec_st.recording || rt_state() == RC_ST_RECORDING || rt_mic()) {
		TC_PRINT("RULES %s in %s: a recording runs\n", what, rc_state_name(before));
		bad++;
	}
}

/* one valid request per opcode of FW 6.3 (l.696 to l.708) */
static void each_opcode(enum rc_state st)
{
	static uint8_t resp[RREC_MSG_HEADER_BYTES + 2 + RREC_GET_LOG_MAX_MAX * RREC_LOG_RECORD_BYTES];
	uint8_t pl[16];
	uint32_t len;
	uint8_t s;

	for (uint8_t op = RREC_OP_FIRST; op <= RREC_OP_LAST; op++) {
		memset(pl, 0, sizeof(pl));
		switch (op) {
		case RREC_OP_LIST_RECORDINGS:
		case RREC_OP_GET_LOG:
			sys_put_le16(1, &pl[4]);   /* first 0, max 1 */
			len = 6;
			break;
		case RREC_OP_READ_RANGE:
			sys_put_le32(1, &pl[8]);   /* recording 0, chunk 0, count 1 */
			len = 12;
			break;
		case RREC_OP_CONFIRM:
		case RREC_OP_FW_BEGIN:
			len = 8;
			break;
		case RREC_OP_DELETE:
			len = 4;
			break;
		case RREC_OP_SET_TIME:
			len = 10;
			break;
		case RREC_OP_FW_DATA:
			len = 5;
			break;
		case RREC_OP_FACTORY:
			pl[0] = RREC_FAC_SCREEN;
			len = 1;
			break;
		default:
			len = 0;
			break;
		}
		rt_steps_clear();
		(void)rt_usb(op, pl, len, resp, sizeof(resp), &s);
		TC_PRINT("RULES opcode 0x%02x in %s: status %u\n", op, rc_state_name(st), s);
		check_after("opcode", st);
		if (rt_state() != st && op != RREC_OP_REBOOT) {
			TC_PRINT("RULES opcode 0x%02x: state %s -> %s\n", op, rc_state_name(st), rc_state_name(rt_state()));
			bad++;
		}
	}
}

ZTEST(recorder_rules, test_no_command_starts_or_stops)
{
	bad = 0;
	/* CHARGING */
	rt_fresh(NULL);
	rt_vbus(true);
	zassert_equal(rt_state(), RC_ST_CHARGING, NULL);
	each_opcode(RC_ST_CHARGING);
	/* TRANSFER */
	rt_usb_configured();
	zassert_equal(rt_state(), RC_ST_TRANSFER, NULL);
	each_opcode(RC_ST_TRANSFER);
#if defined(CONFIG_RING_FACTORY)
	{
		/* FACTORY_TEST: every sub-command of FW 9.3 but EXIT and the two ship commands (they leave the state) */
		static const uint8_t subs[] = { RREC_FAC_MIC, RREC_FAC_SKEW_REMOVED, RREC_FAC_SCREEN, RREC_FAC_JOY,
						RREC_FAC_CENTRE, RREC_FAC_MOTOR, RREC_FAC_SIGN, RREC_FAC_STORE,
						RREC_FAC_RADIO, RREC_FAC_CHARGE, RREC_FAC_XTAL };
		static uint8_t resp[600];
		struct rt_boot b = { .factory_flag = true };
		uint8_t s;

		rt_fresh(&b);
		rt_vbus(true);
		rt_usb_configured();
		{
			uint8_t e = RREC_FAC_ENTER;

			(void)rt_usb(RREC_OP_FACTORY, &e, 1, resp, sizeof(resp), &s);
		}
		zassert_equal(rt_state(), RC_ST_FACTORY_TEST, NULL);
		for (size_t i = 0; i < ARRAY_SIZE(subs); i++) {
			/* T-MIC takes the microphone (1); T-JOY and T-CENTRE a window of 1,000 ms (u16) */
			uint8_t pl[3] = { subs[i], 0, 0 };
			uint32_t len = 1;

			if (subs[i] == RREC_FAC_MIC) {
				pl[1] = 1;
				len = 2;
			} else if (subs[i] == RREC_FAC_JOY || subs[i] == RREC_FAC_CENTRE) {
				sys_put_le16(1000, &pl[1]);
				len = 3;
			}
			rt_steps_clear();
			(void)rt_usb(RREC_OP_FACTORY, pl, len, resp, sizeof(resp), &s);
			TC_PRINT("RULES factory 0x%02x: status %u\n", subs[i], s);
			check_after("factory", RC_ST_FACTORY_TEST);
		}
		each_opcode(RC_ST_FACTORY_TEST);
	}
#endif
	/* RECORDING: the USB stack does not run without VBUS: the case cannot reach the ring at all */
	rt_fresh(NULL);
	rt_long();
	zassert_true(rhw_sim_usb_host_write((const uint8_t *)"RR", 2) != 0, "no USB in RECORDING without VBUS");
	zassert_equal(rt_state(), RC_ST_RECORDING, "the recording goes on");
	rt_long();
	zassert_equal(bad, 0, "%d faults: a command started or stopped a recording or made a press", bad);
}

/* T-CENTRE (FW l.1027) through the join: in FACTORY_TEST a centre hold and a short press reach the jig as events of the
 * core's own recogniser (lead's ruling 5), never a recording */
ZTEST(recorder_rules, test_factory_gestures_reach_the_jig)
{
#if defined(CONFIG_RING_FACTORY)
	static uint8_t resp[600];
	struct rt_boot b = { .factory_flag = true };
	uint8_t pl[3] = { RREC_FAC_CENTRE, 0, 0 };
	uint8_t e = RREC_FAC_ENTER, s;
	bool seen[16] = { false };
	int n;

	rt_fresh(&b);
	rt_vbus(true);
	rt_usb_configured();
	(void)rt_usb(RREC_OP_FACTORY, &e, 1, resp, sizeof(resp), &s);
	zassert_equal(rt_state(), RC_ST_FACTORY_TEST, NULL);
	rt_steps_clear();
	sys_put_le16(4000, &pl[1]);
	zassert_ok(rt_usb_send(RREC_OP_FACTORY, pl, 3), "T-CENTRE sent");
	rt_sleep(200);
	rglue_input(RC_SW_CENTRE, true);   /* held 1,100 ms: MW at 500, long at 1,000 (FW l.241, l.128) */
	rt_sleep(1100);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(300);
	rglue_input(RC_SW_CENTRE, true);   /* a short press */
	rt_sleep(100);
	rglue_input(RC_SW_CENTRE, false);
	n = rt_usb_recv(resp, sizeof(resp), &s, 8000);
	zassert_equal(s, RREC_ST_OK, "answered");
	zassert_true(n >= RREC_MSG_HEADER_BYTES + 3, "result, dropped, count");
	for (uint8_t i = 0; i < resp[RREC_MSG_HEADER_BYTES + 2]; i++) {
		uint8_t ev = resp[RREC_MSG_HEADER_BYTES + 3 + 5 * i];

		if (ev < ARRAY_SIZE(seen)) {
			seen[ev] = true;
		}
	}
	TC_PRINT("T-CENTRE: result %u, %u events\n", resp[RREC_MSG_HEADER_BYTES], resp[RREC_MSG_HEADER_BYTES + 2]);
	zassert_equal(resp[RREC_MSG_HEADER_BYTES], RREC_FAC_RESULT_PASS, "pass (FW l.1020)");
	zassert_true(seen[RFA_IN_CENTRE_DOWN] && seen[RFA_IN_CENTRE_UP], "centre down and up");
	zassert_true(seen[RFA_IN_LONG], "the long press");
	zassert_true(seen[RFA_IN_SINGLE], "the single press");
	zassert_equal(rt_state(), RC_ST_FACTORY_TEST, "still FACTORY_TEST");
	zassert_false(rrec_st.recording || rt_mic(), "no recording (FW l.1027)");
	rt_vbus(false);
#else
	ztest_test_skip();
#endif
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_rules, NULL, setup, NULL, NULL, NULL);
