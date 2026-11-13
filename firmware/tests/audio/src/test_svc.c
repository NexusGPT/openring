/* Suite audio_svc (software step 6, unit U3): the thin part on the simulated microphone input, with a stand-in for
 * the store's hand-off. Time is the kernel's simulated time. A block of 1,024 bytes arrives every 16 ms, the first
 * 16 ms after the start; the PDM start is at uptime `t0` (returned by svc_begin). Expected values are literals written
 * from design/firmware.md (lines cited), never computed by the code under test. */
#include "common.h"

static void before(void *f)
{
	ARG_UNUSED(f);
	svc_setup();
}

static void after(void *f)
{
	ARG_UNUSED(f);
	svc_cleanup();
}

ZTEST_SUITE(audio_svc, NULL, NULL, before, after, NULL);

static uint32_t reads_so_far(void)
{
	return rhw_sim_log_count_kind(RHW_EV_MIC_READ);
}

/* time of the successful read of block n, in ms (from the event log), or -1 */
static int64_t good_read_ms(int64_t n)
{
	struct rhw_sim_ev e;

	for (uint32_t i = 0; i < rhw_sim_log_count(); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		if (e.kind == RHW_EV_MIC_READ && e.res == 0 && e.a0 == n) {
			return e.t_us / 1000;
		}
	}
	return -1;
}

/* A6, FW l.428, l.429: HFXO requested and running before the microphones start (configure, then trigger). The crystal
 * takes 5 ms to run; the join's 1 ms wait is shorter, so only waiting for it keeps the order. */
ZTEST(audio_svc, test_hfxo_before_trigger)
{
	rhw_sim_hfxo_delay_ms(5);
	(void)svc_begin(true, false);
	int32_t req = ev_find(RHW_EV_HFXO_REQUEST, 0);
	int32_t run = ev_find(RHW_EV_HFXO_RUNNING, 0);
	int32_t cfg = ev_find(RHW_EV_MIC_CONFIGURE, 0);
	int32_t trg = ev_find(RHW_EV_MIC_START, 0);

	zassert_true(req >= 0, "HFXO requested");
	zassert_true(run > req, "HFXO running after its request (%d, %d)", req, run);
	zassert_true(cfg > run, "configure after HFXO runs (running %d, configure %d)", run, cfg);
	zassert_true(trg > cfg, "trigger after configure (%d, %d)", cfg, trg);
}

/* A6: a crystal that never runs: prepare gives up and releases its request. */
ZTEST(audio_svc, test_hfxo_prepare_timeout)
{
	rhw_sim_hfxo_never(true);
	zassert_equal(rau_prepare(10), -ETIMEDOUT);
	zassert_equal(rhw_sim_hfxo_requests(), 0, "the request is released");
	zassert_equal(ev_find(RHW_EV_MIC_START, 0), -1, "nothing started");
}

/* A6, FW l.463: HFXO released after the microphones stop (and after VDD_MIC is off, which is the join's order);
 * never while they run. */
ZTEST(audio_svc, test_hfxo_released_after_stop)
{
	(void)svc_begin(true, false);
	k_sleep(K_MSEC(200));
	zassert_true(rhw_hfxo()->running());
	zassert_equal(rau_release(), -EBUSY, "not while the microphones run");
	zassert_equal(rhw_sim_hfxo_requests(), 1);
	zassert_ok(rau_halt());
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, false, "test_join"));
	zassert_ok(rau_release());
	int32_t stop = ev_find(RHW_EV_MIC_STOP, 0);
	int32_t rel = ev_find(RHW_EV_HFXO_RELEASE, 0);
	int32_t off = ev_find(RHW_EV_PMIC_RAIL, ev_find(RHW_EV_PMIC_RAIL, 0) + 1);

	zassert_true(stop >= 0 && rel > stop, "release after stop (%d, %d)", stop, rel);
	zassert_true(off >= 0 && rel > off, "release after VDD_MIC off (%d, %d)", off, rel);
	zassert_equal(rhw_sim_hfxo_requests(), 0);
	zassert_false(rhw_hfxo()->running());
}

/* One recording of 1,000 ms with one block lost; checks the chunk 0 copy. Mark at 1,000 ms: (1,000 - 50) x 16 = 15,200
 * kept frames = 8,192 + 7,008. Block 5 holds raw frames 1,280 to 1,535 = kept 480 to 735. */
static void check_one_lost_block(void)
{
	struct rau_cut_result r;
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(1000));
	zassert_ok(rau_cut(t0 + 1000, &r));
	zassert_equal(si_puts(), 1);
	const struct rst_chunk *c0 = si_copy(0);

	zassert_not_null(r.last);
	zassert_equal(r.close.duration_frames, 15200, "the recording keeps its length");
	zassert_equal(r.last->hdr.frames, 7008);
	zassert_equal(svc_ev.dropouts, 1, "logged once, got %d", svc_ev.dropouts);
	zassert_equal(svc_ev.dr_rec, 7);
	zassert_equal(svc_ev.dr_chunk, 0);
	zassert_equal(svc_ev.dr_block, 1, "at frame 480 of the chunk = block position 1");
	zassert_equal(c0->hdr.flags, 0x81, "first and dropout");
	zassert_equal(c0->hdr.dropout_blocks, 1);
	zassert_equal(r.last->hdr.flags, 0x02, "last only");
	zassert_equal(r.last->hdr.dropout_blocks, 0);
	zassert_equal(t_left(c0, 479), 1279);
	for (uint32_t i = 480; i < 736; i++) {
		zassert_equal(t_left(c0, i), 0, "frame %u zero", i);
		zassert_equal(t_right(c0, i), 0, "frame %u zero", i);
	}
	zassert_equal(t_left(c0, 736), 1536, "the stream goes on in place");
	zassert_ok(rau_halt());
}

/* A7, FW l.430: the input never delivers block 5; the 16 ms gap is filled with zeros and logged. */
ZTEST(audio_svc, test_dropout_logged)
{
	rhw_sim_mic_drop_block(5);
	check_one_lost_block();
}

/* A7: the input's read of block 5 fails: same result. */
ZTEST(audio_svc, test_dropout_on_read_error)
{
	rhw_sim_mic_read_error(5);
	check_one_lost_block();
}

/* A7: a thread that is late (the store held every chunk) is not mistaken for a lost block: no dropout, no zeros. */
ZTEST(audio_svc, test_late_thread_is_not_a_dropout)
{
	struct rau_cut_result r;

	si_hold(true);
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(2000));       /* the ring is full from about 1,600 ms: the thread waits */
	si_hold(false);
	k_sleep(K_MSEC(1000));
	zassert_ok(rau_cut(t0 + 3000, &r));
	zassert_equal(svc_ev.dropouts, 0, "late is not lost");
	zassert_equal(r.close.duration_frames, 47200);
	for (int i = 0; i < si_puts(); i++) {
		zassert_equal(si_copy(i)->hdr.flags & RREC_CH_FLAG_DROPOUT, 0);
	}
	zassert_equal(t_left(si_copy(4), 8191), (int16_t)((5 * 8192 + 800 - 1) & 0xFFFF), "no frame lost");
	zassert_ok(rau_halt());
}

/* A8, FW l.440, l.441: a ring of 3 chunks. The store never reports a chunk written: after 3 chunks are handed over a
 * fourth cannot start and nothing is overwritten. */
ZTEST(audio_svc, test_ring_of_three)
{
	si_hold(true);
	(void)svc_begin(true, false);
	k_sleep(K_MSEC(2000));
	uint32_t reads = reads_so_far();

	k_sleep(K_MSEC(500));
	zassert_equal(si_puts(), 3, "three chunks handed over, no fourth");
	zassert_equal(reads_so_far(), reads, "the audio thread waits for a free chunk: it reads nothing more");
	for (int i = 0; i < 3; i++) {
		zassert_equal(memcmp(si_live(i), si_copy(i), sizeof(struct rst_chunk)), 0, "chunk %d not overwritten", i);
		zassert_equal(si_copy(i)->hdr.chunk_in_recording, (uint32_t)i);
	}
	/* chunk 0 is reported written: its buffer is free, the fourth chunk fills it */
	si_complete(0);
	k_sleep(K_MSEC(100));
	zassert_equal(si_puts(), 4, "the fourth chunk waited for a free buffer");
	zassert_equal(si_copy(3)->hdr.first_frame_index, 24576);
	zassert_equal(t_left(si_copy(3), 0), 25376, "24,576 + 800: the frames did not skip");
	zassert_equal(si_copy(3)->hdr.dropout_blocks, 0);
	for (int i = 1; i < 3; i++) {
		zassert_equal(memcmp(si_live(i), si_copy(i), sizeof(struct rst_chunk)), 0, "chunk %d still intact", i);
	}
	zassert_equal(svc_ev.dropouts, 0);
	zassert_equal(sizeof(((struct rst_chunk *)0)->bytes), 33280);
}

/* A store that answers "full" (-ENOBUFS) for a while: the chunk waits and goes over when the store takes it. */
ZTEST(audio_svc, test_put_waits_on_enobufs)
{
	si_enobufs_after(1);
	(void)svc_begin(true, false);
	k_sleep(K_MSEC(1500));
	zassert_equal(si_puts(), 1, "the second chunk waits");
	si_enobufs_after(-1);
	k_sleep(K_MSEC(100));
	zassert_true(si_puts() >= 2, "the second chunk went over when the store took it");
	zassert_equal(si_copy(1)->hdr.chunk_in_recording, 1);
	zassert_equal(t_left(si_copy(1), 0), 8992, "8,192 + 800: nothing lost");
}

/* A10, FW l.448: the long press fires at the 1,000 ms mark; the frames up to the mark are kept. Mark 3,000 ms after
 * the start: (3,000 - 50) x 16 = 47,200 frames = 5 chunks of 8,192 + 6,240. */
ZTEST(audio_svc, test_stop_keeps_frames_to_mark)
{
	struct rau_cut_result r;
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(3000));
	zassert_ok(rau_cut(t0 + 3000, &r));
	zassert_equal(r.close.duration_frames, 47200);
	zassert_equal(si_puts(), 5, "five full chunks went to the store");
	zassert_not_null(r.last);
	zassert_equal(r.last->hdr.frames, 6240);
	zassert_equal(r.last->hdr.flags, 0x02);
	zassert_equal(r.last->hdr.chunk_in_recording, 5);
	zassert_equal(t_left(r.last, 6239), (int16_t)47999, "the last kept frame: raw frame 47,999");
	zassert_equal(t_left(r.last, 6240), 0, "nothing after the mark");
	zassert_true(t_tail_zero(r.last, 6240));
	/* the PDM runs on until the halt: later frames are dropped, the chunk does not change */
	static struct rst_chunk snap;

	memcpy(&snap, r.last, sizeof(snap));
	k_sleep(K_MSEC(200));
	zassert_equal(memcmp(&snap, r.last, sizeof(snap)), 0);
	zassert_equal(si_puts(), 5);
	zassert_true(rau_capturing(), "capturing until the halt");
	zassert_ok(rau_halt());
	zassert_false(rau_capturing());
}

/* A11, FW l.449: no microphone read outside an open recording: not after boot, not while HFXO and the rail come up,
 * not after the stop; and the second recording starts with its own first frame (nothing kept from before). */
ZTEST(audio_svc, test_no_read_outside_recording)
{
	struct rau_cut_result r;

	k_sleep(K_MSEC(500));
	zassert_equal(reads_so_far(), 0, "no read after boot, %u", reads_so_far());
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "test_join"));
	zassert_ok(rau_prepare(100));
	k_sleep(K_MSEC(500));
	zassert_equal(reads_so_far(), 0, "no read before the start");
	rhw_pmic()->rail_set(RHW_RAIL_MIC, false, "test_join");
	zassert_ok(rau_release());

	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(300));
	zassert_true(reads_so_far() > 0);
	zassert_ok(rau_cut(t0 + 300, &r));
	zassert_ok(rau_halt());
	uint32_t n = reads_so_far();

	k_sleep(K_MSEC(500));
	zassert_equal(reads_so_far(), n, "no read after the stop");
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, false, "test_join"));
	zassert_ok(rau_release());

	/* the second recording */
	t0 = svc_begin(true, false);
	k_sleep(K_MSEC(300));
	zassert_ok(rau_cut(t0 + 300, &r));
	zassert_not_null(r.last);
	zassert_equal(t_left(r.last, 0), 800, "the first kept frame of the new recording");
	zassert_equal(r.last->hdr.chunk_in_recording, 0);
	zassert_equal(r.last->hdr.flags, 0x03);
	zassert_ok(rau_halt());
}

/* C15, FW l.169: no block for 100 ms: reported once. The input stops after 10 blocks. */
ZTEST(audio_svc, test_no_block_100ms_reports)
{
	rhw_sim_mic_stop_after(10);
	(void)svc_begin(true, false);
	k_sleep(K_MSEC(400));
	zassert_equal(svc_ev.no_block, 1, "reported once");
	int64_t last = good_read_ms(9);

	zassert_true(last > 0);
	int64_t d = svc_ev.no_block_ms - last;

	zassert_true(d >= 100 && d <= 101, "reported %lld ms after the last block (100 expected)", d);
	zassert_ok(rau_halt());
}

/* C15, FW l.169, l.125: after "no block" the join cuts: the frames there are come back with -EIO, so the recording can
 * still be closed. 10 blocks = 2,560 raw frames = 1,760 kept. */
ZTEST(audio_svc, test_cut_after_no_block)
{
	struct rau_cut_result r;

	rhw_sim_mic_stop_after(10);
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(400));
	zassert_equal(rau_cut(t0 + 400, &r), -EIO);
	zassert_not_null(r.last);
	zassert_equal(r.last->hdr.frames, 1760, "frames %u", r.last->hdr.frames);
	zassert_equal(r.close.duration_frames, 1760);
	zassert_ok(rau_halt());
}

/* A14, FW l.465: the clock pins are in their sleep state at boot before VDD_MIC is ever on, in the default state
 * while the microphones run, and back in the sleep state before VDD_MIC goes off. */
ZTEST(audio_svc, test_clock_low_whenever_rail_off)
{
	struct rau_cut_result r;

	zassert_true(rhw_sim_mic_pins_asleep(), "asleep after boot");
	int32_t boot = ev_find(RHW_EV_MIC_PINS_SLEEP, 0);

	zassert_equal(boot, 0, "the sleep state is the first thing done");
	int64_t t0 = svc_begin(true, false);
	int32_t on = ev_find(RHW_EV_PMIC_RAIL, 0);

	zassert_true(on > boot, "VDD_MIC on after the sleep state");
	zassert_false(rhw_sim_mic_pins_asleep(), "default state while capturing");
	k_sleep(K_MSEC(200));
	zassert_ok(rau_cut(t0 + 200, &r));
	zassert_ok(rau_halt());
	zassert_true(rhw_sim_mic_pins_asleep(), "asleep when rau_halt returns, before the rail goes off");
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, false, "test_join"));
	int32_t stop = ev_find(RHW_EV_MIC_STOP, 0);
	int32_t sleep2 = ev_find(RHW_EV_MIC_PINS_SLEEP, (uint32_t)boot + 1);
	int32_t off = ev_find(RHW_EV_PMIC_RAIL, (uint32_t)on + 1);

	zassert_true(stop > 0 && sleep2 > stop, "sleep state after the stop (%d, %d)", stop, sleep2);
	zassert_true(off > sleep2, "rail off after the sleep state (%d, %d)", sleep2, off);
}

/* FW l.457, l.463: the audio part never switches a rail: a whole recording with no call of the test's own. */
ZTEST(audio_svc, test_unit_never_switches_rail)
{
	struct rau_cut_result r;

	zassert_ok(rau_prepare(100));
	k_sleep(K_MSEC(RREC_MIC_RAIL_WAIT_MS));
	struct rau_start_args a = { .recording_id = 1, .recording_type = RREC_REC_TYPE_RECORDING, .time_set = true };

	zassert_ok(rau_start(&a));
	int64_t t0 = rhw_clock()->now_ms();

	k_sleep(K_MSEC(600));
	zassert_ok(rau_cut(t0 + 600, &r));
	zassert_ok(rau_halt());
	zassert_ok(rau_release());
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_PMIC_RAIL), 0, "no rail call by the audio part");
}

/* S13, FW l.567 to l.571: battery and die temperature of the simulated power chip, boot count and recording id from
 * the start arguments, fw_version from the caller; time of the first kept frame. */
ZTEST(audio_svc, test_chunk_facts_from_power_chip)
{
	struct rhw_pmic_sample sc[2] = {
		{ .mv = 3790, .ua = 0, .temp_c_x10 = 250, .die_c_x10 = 312 },
		{ .mv = 3788, .ua = 0, .temp_c_x10 = 250, .die_c_x10 = 315 },
	};
	struct rau_cut_result r;

	rhw_sim_pmic_script(sc, 2);
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(1000));
	zassert_ok(rau_cut(t0 + 1000, &r));
	const struct rst_chunk *c0 = si_copy(0);

	zassert_equal(c0->hdr.battery_mv, 3790, "first sample");
	zassert_equal(c0->hdr.temp_c_x10, 312);
	zassert_equal(r.last->hdr.battery_mv, 3788, "second sample, taken at the start of chunk 1");
	zassert_equal(r.last->hdr.temp_c_x10, 315);
	zassert_equal(c0->hdr.fw_version, 0x01020003);
	zassert_equal(c0->hdr.boot_count, 4);
	zassert_equal(c0->hdr.recording_id, 7);
	zassert_equal(c0->hdr.recording_type, 1);
	zassert_equal(c0->hdr.cycle_hz, 1000000, "the simulated counter's rate");
	zassert_true(c0->hdr.uptime_ns >= (uint64_t)(t0 + 50) * 1000000ULL &&
		     c0->hdr.uptime_ns < (uint64_t)(t0 + 51) * 1000000ULL, "first kept frame: start + 50 ms (%llu)",
		     c0->hdr.uptime_ns);
	zassert_true(c0->hdr.utc_ms >= 1700000000000LL + t0 + 50 && c0->hdr.utc_ms < 1700000000000LL + t0 + 51,
		     "utc = offset + uptime of the first kept frame (%lld)", c0->hdr.utc_ms);
	zassert_ok(rau_halt());
}

/* FW l.547 bit 6: the battery fact B15 reaches the chunks that start after it. */
ZTEST(audio_svc, test_b15_follows)
{
	struct rau_cut_result r;
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(300));
	rau_set_b15(true);
	k_sleep(K_MSEC(900));
	zassert_ok(rau_cut(t0 + 1200, &r));
	zassert_equal(si_copy(0)->hdr.flags, 0x01, "chunk 0 started before: first only");
	zassert_equal(si_copy(1)->hdr.flags, 0x40, "chunk 1 started after: bit 6 only");
	zassert_equal(r.last->hdr.flags, 0x42, "chunk 2: last and bit 6");
	zassert_ok(rau_halt());
}

/* C13, FW l.244, l.263, l.566, l.582 (ruling R24): the highlight carries the time of CENTRE_DOWN. Pressed at 1,200 ms
 * after the start (frame (1,200 - 50) x 16 = 18,400), delivered at 1,500 ms into chunk 2, which is being filled. One before the start and one after the
 * stop are ignored. */
ZTEST(audio_svc, test_highlight_marks_down_time)
{
	struct rau_cut_result r;

	rau_highlight(5);                               /* outside a capture */
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(1500));
	rau_highlight(t0 + 1200);
	k_sleep(K_MSEC(50));
	zassert_ok(rau_cut(t0 + 1550, &r));
	rau_highlight(t0 + 1500);                       /* after the cut */
	zassert_not_null(r.last);
	zassert_equal(r.last->hdr.chunk_in_recording, 2);
	zassert_equal(r.last->hdr.highlight_count, 1);
	zassert_equal(r.last->hdr.highlight_frame[0], 18400, "frame number of CENTRE_DOWN");
	zassert_equal(r.close.highlight_count, 1);
	zassert_equal(r.close.highlight_ms[0], 1150);
	zassert_ok(rau_halt());
	rau_highlight(t0 + 1);                          /* after the halt */
}

/* Ruling R24: a highlight delivered after the chunk of its frame went to the store (a press of 40 to 450 ms and a 400 ms
 * window put the delivery 440 to 850 ms after CENTRE_DOWN, more than a chunk of 512 ms) is written in the chunk being
 * filled, with the frame number of CENTRE_DOWN. CENTRE_DOWN at 700 ms (frame 10,400, chunk 1), delivered at 1,300 ms,
 * when chunk 1 is already with the store and chunk 2 is being filled. */
ZTEST(audio_svc, test_late_highlight_in_next_chunk)
{
	struct rau_cut_result r;
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(1300));
	rau_highlight(t0 + 700);
	k_sleep(K_MSEC(100));
	zassert_ok(rau_cut(t0 + 1400, &r));
	zassert_equal(si_copy(1)->hdr.highlight_count, 0);
	zassert_equal(r.last->hdr.chunk_in_recording, 2);
	zassert_equal(r.last->hdr.highlight_count, 1);
	zassert_equal(r.last->hdr.highlight_frame[0], 10400, "(700 - 50) x 16");
	zassert_equal(r.close.highlight_count, 1);
	zassert_equal(r.close.highlight_ms[0], 650);
	zassert_ok(rau_halt());
}

/* The stop comes while the highlight's chunk is still being filled: the marker is in the last (partial) chunk. */
ZTEST(audio_svc, test_highlight_in_partial_last_chunk)
{
	struct rau_cut_result r;
	int64_t t0 = svc_begin(true, false);

	k_sleep(K_MSEC(300));
	rau_highlight(t0 + 100);
	k_sleep(K_MSEC(100));
	zassert_ok(rau_cut(t0 + 400, &r));
	zassert_equal(si_puts(), 0);
	zassert_not_null(r.last);
	zassert_equal(r.last->hdr.highlight_count, 1);
	zassert_equal(r.last->hdr.highlight_frame[0], 800, "100 x 16 - 800");
	zassert_ok(rau_halt());
}

/* A18, FW l.497, l.498: M1 starts before the PDM and ends 20 ms after the start; the rest plus 50 ms is marked in the
 * first chunk: {0; 320}. MW in the recording (300 to 340 ms after the start): frames 4,000 to 5,440. Edges are given
 * with the cycle count they happened at (the simulated counter runs 1,000,000 per second: 1 cycle = 1 us). */
ZTEST(audio_svc, test_motor_edges_marked)
{
	struct rau_cut_result r;

	rau_motor_edge(true, rhw_clock()->cycles());    /* M1 high, before the start */
	k_sleep(K_MSEC(40));
	int64_t t0 = svc_begin(true, false);
	int32_t st = ev_find(RHW_EV_MIC_START, 0);
	uint64_t start_us = (uint64_t)ev_t_us(st);

	rau_motor_edge(false, start_us + 20000);        /* M1 low, 20 ms after the PDM start */
	k_sleep(K_MSEC(300));
	rau_motor_edge(true, start_us + 300000);        /* MW */
	rau_motor_edge(false, start_us + 340000);
	k_sleep(K_MSEC(200));
	zassert_ok(rau_cut(t0 + 500, &r));
	zassert_not_null(r.last);
	zassert_true(r.last->hdr.flags & RREC_CH_FLAG_MOTOR);
	zassert_equal(r.last->hdr.motor_count, 2);
	zassert_equal(r.last->hdr.motor_frames[0][0], 0);
	zassert_equal(r.last->hdr.motor_frames[0][1], 320);
	zassert_equal(r.last->hdr.motor_frames[1][0], 4000);
	zassert_equal(r.last->hdr.motor_frames[1][1], 5440);
	zassert_ok(rau_halt());
}

/* rau_start while capturing is refused; a stop with nothing running is harmless. */
ZTEST(audio_svc, test_start_twice_refused)
{
	struct rau_start_args a = { .recording_id = 9, .recording_type = RREC_REC_TYPE_RECORDING, .time_set = true };

	zassert_ok(rau_halt(), "halt with nothing running");
	(void)svc_begin(true, false);
	zassert_equal(rau_start(&a), -EBUSY);
	zassert_ok(rau_halt());
}
