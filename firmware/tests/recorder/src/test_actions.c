/*
 * recorder_actions: the actions of the core carried out by the recorder (plan rows C4, C5, C12, C13, C19, C25, C27, A18
 * J part, P12). Orders are read from the one event log of the simulated drivers (rhw_sim.h).
 */
#include <string.h>

#include <zephyr/sys/byteorder.h>

#include <ring_store/rst.h>

#include "rt.h"

static bool in_range(int64_t lba, uint32_t lo, uint32_t hi)
{
	return lba >= lo && lba <= hi;
}

/* the first disk write at or after `from` whose LBA lies in [lo, hi] */
static int32_t find_write(uint32_t lo, uint32_t hi, uint32_t from)
{
	struct rhw_sim_ev e;

	for (uint32_t i = from; rhw_sim_log_get(i, &e); i++) {
		if (e.kind == RHW_EV_DISK_WRITE && in_range(e.a0, lo, hi)) {
			return (int32_t)i;
		}
	}
	return -1;
}

static int64_t act_time(enum rc_action a)
{
	for (uint32_t i = 0; i < rt_acts(); i++) {
		if (rt_act_get(i).a == a) {
			return rt_act_get(i).t_ms;
		}
	}
	return -1;
}

/* the frames of the closed recording against what the simulated input delivered (review finding R6-05): every kept frame
 * is the input's frame counter (left) and its inverse (right) from frame 800 on (FW l.460: the first 50 ms dropped), none
 * missing; the chunks' frames add up to the CLOSE record's duration; the last chunk is the partial one; and the duration
 * is what was captured from the start to the mark */
static void check_closed_frames(int64_t start_ms, int64_t mark_ms)
{
	static uint8_t chunk[RREC_CHUNK_BYTES];
	struct rst_mount_info mi;
	struct rst_rec_info info[8];
	uint16_t n = 0;
	uint64_t sum = 0;
	uint32_t last_frames = 0;
	uint32_t bad = 0;
	int64_t want;

	zassert_equal(rst_mount(false, &mi), 0, "mount");
	zassert_equal(rst_list(0, 8, info, &n), 0, "list");
	zassert_true(n >= 1, "the recording is listed");
	for (uint32_t c = 0; c < info[n - 1].chunk_count; c++) {
		uint32_t fr;
		const uint8_t *pl = &chunk[RREC_CHUNK_HEADER_BYTES];

		zassert_equal(rst_read_chunk(info[n - 1].recording_id, c, chunk), 0, "read chunk %u", c);
		fr = sys_get_le32(&chunk[RREC_CH_OFF_FRAMES]);
		for (uint32_t f = 0; f < fr; f++) {
			uint16_t want_l = (uint16_t)((RREC_DISCARD_FRAMES + sum + f) & 0xFFFFu);
			uint16_t l = sys_get_le16(&pl[f * 4]);
			uint16_t r = sys_get_le16(&pl[f * 4 + 2]);

			if (l != want_l || r != (uint16_t)~want_l) {
				if (bad < 3) {
					TC_PRINT("close frames: chunk %u frame %u: %u/%u, captured %u/%u\n", c, f, l, r, want_l,
						 (uint16_t)~want_l);
				}
				bad++;
			}
		}
		sum += fr;
		last_frames = fr;
	}
	(void)rst_unmount();
	/* FW l.443, l.460: 16 frames per ms; the kept frames run from the start + 50 ms to the mark */
	want = (mark_ms - start_ms) * 16 - (int64_t)RREC_DISCARD_FRAMES;
	TC_PRINT("close frames: %u chunks, %llu frames in the chunks, CLOSE duration %llu, last chunk %u frames, "
		 "captured to the mark %lld (start %lld ms, mark %lld ms), %u frames not as captured\n", info[n - 1].chunk_count,
		 sum, info[n - 1].duration_frames, last_frames, want, start_ms, mark_ms, bad);
	zassert_equal(bad, 0, "every kept frame is the captured one (%u not)", bad);
	zassert_equal(sum, info[n - 1].duration_frames, "the chunks hold the whole duration (%llu of %llu)", sum,
		      info[n - 1].duration_frames);
	zassert_true(last_frames > 0 && last_frames < RREC_CHUNK_FRAMES, "the last chunk is the partial one (%u)",
		     last_frames);
	/* one block (256 frames, FW l.443) plus one ms of each stamp: the mark and the start are ms times */
	zassert_true(sum + RREC_BLOCK_FRAMES + 32 >= (uint64_t)want && sum <= (uint64_t)want + RREC_BLOCK_FRAMES + 32,
		     "kept %llu, captured to the mark %lld", sum, want);
}

/* FW l.125: close = partial chunk, CLOSE record, superblock flag clear, stop PDM, clocks low, VDD_MIC off, VDD_SD off */
ZTEST(recorder_actions, test_close_order)
{
	int32_t i_part, i_close, i_sb, i_stop, i_sleep, i_mic, i_sd;
	int64_t start_ms, mark_ms;

	rt_fresh(NULL);
	rhw_sim_log_clear();
	rt_long();
	start_ms = rt_ev_us(rt_find(RHW_EV_MIC_START, -1, -1, 0)) / 1000;
	zassert_true(start_ms > 0, "the input started");
	rt_sleep(1300);
	/* the stop press so that its mark (1,000 ms after the press, FW l.128) falls in the middle of a chunk: a partial
	 * chunk of about half a chunk exists (8,192 frames, FW l.535) */
	for (int i = 0; i < 200; i++) {
		int64_t at_mark = (k_uptime_get() + RREC_LONG_PRESS_MS - start_ms) * 16 - (int64_t)RREC_DISCARD_FRAMES;
		int64_t in_chunk = at_mark % RREC_CHUNK_FRAMES;

		if (in_chunk >= 3000 && in_chunk <= 5000) {
			break;
		}
		rt_sleep(4);
	}
	rhw_sim_log_clear();
	rt_steps_clear();
	rt_long();
	zassert_equal(rt_state(), RC_ST_STANDBY, "stopped");
	mark_ms = act_time(RC_ACT_CLOSE);
	zassert_true(mark_ms > start_ms, "CLOSE carried out");
	i_part = find_write(RREC_LBA_CHUNK_FIRST, UINT32_MAX, 0);
	i_close = find_write(RREC_LBA_INDEX_FIRST, RREC_LBA_INDEX_LAST, 0);
	i_sb = find_write(RREC_LBA_SB_A, RREC_LBA_SB_B, i_close < 0 ? 0 : (uint32_t)i_close);
	i_stop = rt_find(RHW_EV_MIC_STOP, -1, -1, 0);
	i_sleep = rt_find(RHW_EV_MIC_PINS_SLEEP, -1, -1, i_stop < 0 ? 0 : (uint32_t)i_stop);
	i_mic = rt_find_rail(RHW_RAIL_MIC, false, 0);
	i_sd = rt_find_rail(RHW_RAIL_SD, false, 0);
	TC_PRINT("close order: chunk %d, CLOSE record %d, superblock %d, PDM stop %d, clocks low %d, VDD_MIC off %d, "
		 "VDD_SD off %d\n", i_part, i_close, i_sb, i_stop, i_sleep, i_mic, i_sd);
	zassert_true(i_part >= 0 && i_close > i_part, "partial chunk before the CLOSE record");
	zassert_true(i_sb > i_close, "superblock after the CLOSE record");
	zassert_true(i_stop > i_sb, "PDM stop after the superblock");
	zassert_true(i_sleep > i_stop, "clocks low after the stop");
	zassert_true(i_mic > i_sleep, "VDD_MIC off after the clocks are low");
	zassert_true(i_sd > i_mic, "VDD_SD off last");
	check_closed_frames(start_ms, mark_ms);
}

/* FW l.126: open = VDD_SD on, mount, superblock with the open flag, VDD_MIC on, PDM start (FW 4.5) */
ZTEST(recorder_actions, test_open_order)
{
	int32_t i_sd, i_init, i_sb, i_mic, i_cfg, i_start;

	rt_fresh(NULL);
	rhw_sim_log_clear();
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording");
	i_sd = rt_find_rail(RHW_RAIL_SD, true, 0);
	i_init = rt_find(RHW_EV_DISK_INIT, -1, -1, 0);
	i_sb = find_write(RREC_LBA_SB_A, RREC_LBA_SB_B, i_init < 0 ? 0 : (uint32_t)i_init);
	i_mic = rt_find_rail(RHW_RAIL_MIC, true, 0);
	i_cfg = rt_find(RHW_EV_MIC_CONFIGURE, -1, -1, 0);
	i_start = rt_find(RHW_EV_MIC_START, -1, -1, 0);
	TC_PRINT("open order: VDD_SD on %d, init %d, superblock %d, VDD_MIC on %d, configure %d, start %d\n", i_sd, i_init,
		 i_sb, i_mic, i_cfg, i_start);
	zassert_true(i_sd >= 0 && i_init > i_sd, "mount after VDD_SD on");
	zassert_true(i_sb > i_init, "superblock after the mount");
	zassert_true(i_mic > i_sb, "VDD_MIC on after the superblock");
	zassert_true(i_cfg > i_mic && i_start > i_cfg, "PDM configured and started after VDD_MIC on");
	rt_long();
}

/* FW l.158, l.448: a long press in RECORDING closes; M2 runs after VDD_MIC is off */
ZTEST(recorder_actions, test_stop_m2_after_mic_off)
{
	struct rhw_sim_ev e;
	int64_t t_close;
	int32_t i_off, i_first = -1;

	rt_fresh(NULL);
	rt_long();
	rt_sleep(1000);
	rhw_sim_log_clear();
	rt_steps_clear();
	rt_long();
	t_close = act_time(RC_ACT_CLOSE);
	zassert_true(t_close >= 0, "CLOSE carried out");
	i_off = rt_find_rail(RHW_RAIL_MIC, false, 0);
	for (uint32_t i = 0; rhw_sim_log_get(i, &e); i++) {
		if (e.kind == RHW_EV_MOTOR && e.a0 == 1 && e.t_us >= t_close * 1000) {
			i_first = (int32_t)i;
			break;
		}
	}
	TC_PRINT("stop: VDD_MIC off at %d (t %lld us), first MOTOR high from the press at %d (t %lld us)\n", i_off,
		 rt_ev_us(i_off), i_first, rt_ev_us(i_first));
	zassert_true(i_off >= 0 && i_first > i_off, "M2's MOTOR high comes after VDD_MIC off");
	zassert_true(rt_ev_us(i_first) >= rt_ev_us(i_off), "and not earlier in time");
}

/* FW l.144, l.447, ruling R21: M1 at the press, before storage is opened */
ZTEST(recorder_actions, test_m1_at_start)
{
	int32_t i_m1, i_sd;
	int64_t t_open;
	struct rhw_sim_ev e;

	rt_fresh(NULL);
	rhw_sim_log_clear();
	rt_long();
	t_open = act_time(RC_ACT_OPEN);
	i_sd = rt_find_rail(RHW_RAIL_SD, true, 0);
	i_m1 = -1;
	for (uint32_t i = 0; rhw_sim_log_get(i, &e); i++) {
		if (e.kind == RHW_EV_MOTOR && e.a0 == 1 && e.t_us >= t_open * 1000) {
			i_m1 = (int32_t)i;
			break;
		}
	}
	zassert_true(i_m1 >= 0 && i_m1 < i_sd, "M1's MOTOR high before VDD_SD on (%d, %d)", i_m1, i_sd);
	rt_long();
}

/* a recording's list entry after it closed (mounts the card for the read) */
static bool last_recording(struct rst_rec_info *out)
{
	struct rst_mount_info mi;
	struct rst_rec_info info[8];
	uint16_t n = 0;

	if (rst_mount(false, &mi) != 0) {
		return false;
	}
	(void)rst_list(0, 8, info, &n);
	(void)rst_unmount();
	if (n == 0) {
		return false;
	}
	*out = info[n - 1];
	return true;
}

/* FW l.159, l.161: a highlight by short press or by the Bluetooth "highlight", MH (C13) */
ZTEST(recorder_actions, test_ble_highlight_marks)
{
	struct rst_rec_info r;

	memset(&r, 0, sizeof(r));
	rt_fresh(NULL);
	rt_long();
	rt_sleep(700);
	rglue_event(RC_EV_BLE_HIGHLIGHT);
	rt_settle();
	zassert_true(rt_row_seen(29), "row 29");
	rt_sleep(600);
	rt_short();
	zassert_true(rt_row_seen(27), "row 27");
	rt_sleep(300);
	rt_long();
	zassert_true(last_recording(&r), "the recording is listed");
	zassert_equal(r.highlight_count, 2, "two highlights in the CLOSE record (%u)", r.highlight_count);
	zassert_true(rrec_tap_count_code(RREC_LOG_MOTOR_PATTERN) >= 3, "MH played");
}

/* FW l.229, l.265: a long press in CHARGING, TRANSFER, ERR_STORAGE_FULL, ERR_BATTERY_LOW: refused with M3 (C25) */
ZTEST(recorder_actions, test_refusal_plays_m3)
{
	static const int rows[] = { 45, 50, 52, 56 };

	for (size_t i = 0; i < ARRAY_SIZE(rows); i++) {
		struct rrec_tap_rec t;
		bool m3 = false;

		zassert_equal(rt_run_row(rows[i]), 0, NULL);
		zassert_true(rt_row_seen(rows[i]), "row %d", rows[i]);
		for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
			m3 |= t.code == RREC_LOG_MOTOR_PATTERN && t.args[0] == RREC_PAT_M3;
		}
		zassert_true(m3, "M3 played for row %d", rows[i]);
		zassert_false(rrec_st.recording, "no recording");
	}
}

/* FW l.191 to l.194, ruling R3: every 60 s the storage init runs and its result is reported (C19), both answers */
ZTEST(recorder_actions, test_retry_storage_reports_result)
{
	struct rt_boot b = { .init_fail = 1000 };
	struct rrec_tap_rec t;
	int fails = 0, oks = 0;

	rt_fresh(&b);
	zassert_equal(rt_state(), RC_ST_ERR_STORAGE_FAULT, "ERR_STORAGE_FAULT");
	rt_sleep(61000);
	rt_settle();
	zassert_true(rt_row_seen(59), "row 59: 60 s elapsed");
	zassert_true(rt_row_seen(62), "row 62: the failed retry reported");
	zassert_equal(rt_state(), RC_ST_ERR_STORAGE_FAULT, "stays");
	rhw_sim_disk_fail_init(0);   /* the card answers again */
	rt_sleep(60000);
	rt_settle();
	zassert_true(rt_row_seen(61), "row 61: the successful retry reported");
	zassert_equal(rt_state(), RC_ST_STANDBY, "STANDBY");
	for (uint32_t k = 0; rrec_tap_get(k, &t); k++) {
		if (t.code == RREC_LOG_STORAGE_RETRY) {
			if (sys_get_le32(t.args) == 0) {
				oks++;
			} else {
				fails++;
			}
		}
	}
	zassert_true(fails >= 1 && oks == 1, "retry results logged: %d failed, %d ok", fails, oks);
}

/* FW l.498: MW in a recording is marked like every pulse (A18, the join's part: the motor edges reach the audio part) */
ZTEST(recorder_actions, test_mw_in_recording_marked)
{
	static uint8_t chunk[RREC_CHUNK_BYTES];
	struct rst_mount_info mi;
	struct rst_rec_info info[4];
	uint16_t n = 0;
	int marked_later = 0;

	rt_fresh(NULL);
	rt_long();
	rt_sleep(1500);
	rglue_input(RC_SW_CENTRE, true);   /* held 600 ms: MW at 500 ms (FW l.241), no long press */
	rt_sleep(600);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(1500);
	rt_long();
	zassert_equal(rst_mount(false, &mi), 0, "mount");
	zassert_equal(rst_list(0, 4, info, &n), 0, "list");
	zassert_true(n >= 1, "one recording");
	for (uint32_t c = 1; c < info[n - 1].chunk_count; c++) {
		zassert_equal(rst_read_chunk(info[n - 1].recording_id, c, chunk), 0, "read chunk %u", c);
		if (sys_get_le16(&chunk[RREC_CH_OFF_FLAGS]) & RREC_CH_FLAG_MOTOR) {
			marked_later++;
		}
	}
	(void)rst_unmount();
	zassert_true(marked_later >= 1, "a chunk after the first carries a motor interval (MW, MH or M2's edge)");
}

/* FW l.936 to l.941 step 1: close everything, save settings and time, before the ship steps (P12, the join's part) */
ZTEST(recorder_actions, test_ship_closes_everything_first)
{
	int32_t i_mic, i_sd, i_cfg, i_strobe, i_ship, i_save;

	zassert_equal(rt_run_row(33), 0, NULL);   /* a recording at B2: close; ship mode */
	i_mic = rt_find_rail(RHW_RAIL_MIC, false, 0);
	i_sd = rt_find_rail(RHW_RAIL_SD, false, i_mic < 0 ? 0 : (uint32_t)i_mic);
	i_cfg = rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0);
	i_strobe = rt_find(RHW_EV_PMIC_SHPHLD_STROBE, -1, -1, 0);
	i_ship = rt_find(RHW_EV_PMIC_SHIP, -1, -1, 0);
	zassert_true(i_mic >= 0 && i_sd > i_mic && i_cfg > i_sd, "VDD_MIC off, VDD_SD off, then SHPHLDCONFIG");
	zassert_equal(rt_find(RHW_EV_PMIC_SHPHLD_CFG, RREC_SHPHLD_MS, -1, 0), i_cfg, "96 ms (FW l.938)");
	zassert_true(i_strobe > i_cfg && i_ship > i_strobe, "strobe, then the ship task");
	/* the menu's power off: settings and time saved before the ship steps */
	rt_fresh(NULL);
	rtime_set(1763000000000LL, 60, true);
	rhw_sim_log_clear();
	rglue_event(RC_EV_MENU_POWER_OFF);
	rt_settle();
	i_save = rt_find(RHW_EV_PERSIST_SAVE, -1, -1, 0);
	i_cfg = rt_find(RHW_EV_PMIC_SHPHLD_CFG, -1, -1, 0);
	zassert_true(rt_row_seen(19), "row 19");
	zassert_true(i_save >= 0 && i_cfg > i_save, "time saved before SHPHLDCONFIG (%d, %d)", i_save, i_cfg);
}

/* Review finding R6-08: an event of the kinds VBUS_OUT, MIC_NO_BLOCK, CHUNK_WRITE_FAILED that finds the recorder's queue
 * full is latched and reaches the core when the queue has room (rows 40, 37, 36 of FW 1.2) */
static int fill_queue_then_post(enum rc_event ev)
{
	int r;
	int n = 0;

	k_sched_lock();
	while (n < 100 && rrec_post(RREC_JOB_EVENT, RC_EV_INIT_DONE) == 0) {   /* no row outside BOOT: dropped by the core */
		n++;
	}
	r = rrec_post(RREC_JOB_EVENT, ev);
	k_sched_unlock();
	TC_PRINT("latch: %d jobs filled the queue, the post of event %d answered %d\n", n, ev, r);
	return r;
}

ZTEST(recorder_actions, test_latched_events_not_lost)
{
	rt_fresh(NULL);
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording");
	rt_steps_clear();
	zassert_not_equal(fill_queue_then_post(RC_EV_MIC_NO_BLOCK), 0, "the queue was full");
	rt_settle();
	zassert_true(rt_row_seen(37), "row 37: no block reached the core (FW l.169)");
	zassert_equal(rt_state(), RC_ST_ERR_MIC_FAULT, "ERR_MIC_FAULT");

	rt_fresh(NULL);
	rt_long();
	zassert_equal(rt_state(), RC_ST_RECORDING, "recording");
	rt_steps_clear();
	zassert_not_equal(fill_queue_then_post(RC_EV_CHUNK_WRITE_FAILED), 0, "the queue was full");
	rt_settle();
	zassert_true(rt_row_seen(36), "row 36: the write fault reached the core (FW l.168)");
	zassert_equal(rt_state(), RC_ST_ERR_STORAGE_FAULT, "ERR_STORAGE_FAULT");
}

/* Review 2, R2-06: a latched VBUS job is queued with the event of the VBUS level read when it is queued: VBUS out is
 * latched (full queue), then VBUS comes back (its event finds the queue still full); the core must end with VBUS present
 * (CHARGING, FW l.152), never with a late "VBUS removed" (row 40, FW l.172) while VBUS is there */
ZTEST(recorder_actions, test_latched_vbus_follows_the_level)
{
	int r_in;

	rt_fresh(NULL);
	rt_vbus(true);
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING");
	rt_steps_clear();
	zassert_not_equal(fill_queue_then_post(RC_EV_VBUS_OUT), 0, "the queue was full: VBUS out latched");
	k_sched_lock();
	r_in = rrec_post(RREC_JOB_EVENT, RC_EV_VBUS_IN);   /* VBUS is back (it never left the simulated chip) */
	k_sched_unlock();
	rt_settle();
	TC_PRINT("latched VBUS: VBUS in posted %d, row 40 seen %d, state %s, VBUS present %d\n", r_in, rt_row_seen(40),
		 rc_state_name(rt_state()), rhw_pmic()->vbus_present());
	zassert_true(rhw_pmic()->vbus_present(), "VBUS present");
	zassert_false(rt_row_seen(40), "no late VBUS removed (row 40)");
	zassert_equal(rt_state(), RC_ST_CHARGING, "CHARGING with VBUS present");
}

/* FW l.218, l.1065 (C23, the join's part): during a recording the audio and storage threads report progress through the
 * join, so the watchdog is fed; the feed rule itself is the system unit's (sys_wdt.test_feed_only_with_progress) */
ZTEST(recorder_actions, test_watchdog_fed_while_recording)
{
	uint32_t f0, f1;

	rt_fresh(NULL);
	zassert_true(rhw_sim_wdt_started(), "the watchdog runs (8 s, FW l.1065)");
	rt_long();
	f0 = rhw_sim_wdt_feeds();
	rt_sleep(12000);   /* longer than the 8 s timeout */
	f1 = rhw_sim_wdt_feeds();
	TC_PRINT("watchdog feeds during 12 s of recording: %u\n", f1 - f0);
	zassert_true(f1 - f0 >= 10, "fed about once a second while recording (%u)", f1 - f0);
	zassert_false(rhw_sim_wdt_would_reset(), "never 8 s without a feed");
	rt_long();
}

static void *setup(void)
{
	rt_setup();
	return NULL;
}

ZTEST_SUITE(recorder_actions, NULL, setup, NULL, NULL, NULL);
