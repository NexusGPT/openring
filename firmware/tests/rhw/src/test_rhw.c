/* Suite rhw_sim (software step 6, unit U0): each fault and value of the simulated drivers fires at the named call and
 * only there, the event log keeps order and time, rhw_sim_reboot() keeps exactly the three kept stores, and kit fact
 * K14 (the real clock on the target). native_sim and nrf54lm20bsim/nrf54lm20a/cpuapp.
 *
 * Every expected value is a literal written here from firmware/docs/step6-plan.md section 5 and design/firmware.md, not
 * produced by the code under test. */

#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/ztest.h>

#include <ring_rhw/rhw.h>
#include <ring_rhw/rhw_sim.h>

static void before(void *f)
{
	ARG_UNUSED(f);
	rhw_sim_reset();
}

ZTEST_SUITE(rhw_sim, NULL, NULL, before, NULL, NULL);

static uint8_t buf[RREC_CHUNK_SECTORS * RREC_SECTOR_BYTES];
static uint8_t rd[RREC_CHUNK_SECTORS * RREC_SECTOR_BYTES];

static void fill_pattern(uint8_t *b, uint32_t sectors, uint8_t seed)
{
	for (uint32_t i = 0; i < sectors * RREC_SECTOR_BYTES; i++) {
		b[i] = (uint8_t)(seed + i / RREC_SECTOR_BYTES);
	}
}

static void card_on(void)
{
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, true, "test"));
	zassert_ok(rhw_disk()->init());
}

static bool all_zero(const uint8_t *b, size_t n)
{
	for (size_t i = 0; i < n; i++) {
		if (b[i] != 0) {
			return false;
		}
	}
	return true;
}

/* ================================================================== card */

/* fault: the sector count; unwritten sectors read as zero; one write call for many sectors */
ZTEST(rhw_sim, test_disk_sector_count)
{
	uint32_t n = 0;

	card_on();
	zassert_ok(rhw_disk()->sector_count(&n));
	zassert_equal(n, 7812500, "devicetree sector-count of app.overlay");
	rhw_sim_disk_set_sectors(81920 + 3 * 65);
	zassert_ok(rhw_disk()->sector_count(&n));
	zassert_equal(n, 82115);
	zassert_ok(rhw_disk()->read(82114, rd, 1));
	zassert_true(all_zero(rd, 512), "an unwritten sector reads as zero");
	zassert_equal(rhw_disk()->read(82115, rd, 1), -EINVAL, "past the end");
	fill_pattern(buf, 65, 1);
	zassert_ok(rhw_disk()->write(81920, buf, 65));
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_WRITE), 1, "65 sectors in one call");
	zassert_ok(rhw_disk()->read(81920, rd, 65));
	zassert_mem_equal(rd, buf, 65 * 512);
	zassert_equal(rhw_disk()->write(82100, buf, 16), -EINVAL, "a write past the end");
}

/* fault: init fails n times */
ZTEST(rhw_sim, test_disk_init_fails_n)
{
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, true, "test"));
	rhw_sim_disk_fail_init(2);
	zassert_equal(rhw_disk()->init(), -EIO);
	zassert_equal(rhw_disk()->init(), -EIO);
	zassert_ok(rhw_disk()->init(), "the third init works");
	zassert_ok(rhw_disk()->init());
}

/* fault: write fails at call n, k times (the named case of the broken copy disk_fault_late) */
ZTEST(rhw_sim, test_disk_write_fault_at_n)
{
	card_on();
	fill_pattern(buf, 1, 7);
	zassert_ok(rhw_disk()->write(100, buf, 1), "a call before the fault is set");
	rhw_sim_disk_fail_write(3, 2);
	zassert_ok(rhw_disk()->write(101, buf, 1), "call 1");
	zassert_ok(rhw_disk()->write(102, buf, 1), "call 2");
	zassert_equal(rhw_disk()->write(103, buf, 1), -EIO, "call 3 fails");
	zassert_equal(rhw_disk()->write(104, buf, 1), -EIO, "call 4 fails");
	zassert_ok(rhw_disk()->write(105, buf, 1), "call 5 works again");
	rhw_sim_disk_peek(103, rd);
	zassert_true(all_zero(rd, 512), "a failed write stores nothing");
	rhw_sim_disk_peek(105, rd);
	zassert_mem_equal(rd, buf, 512);
}

/* fault: read error at an LBA */
ZTEST(rhw_sim, test_disk_read_error_at_lba)
{
	card_on();
	rhw_sim_disk_read_error_at(500);
	zassert_ok(rhw_disk()->read(499, rd, 1));
	zassert_equal(rhw_disk()->read(498, rd, 3), -EIO, "a read that covers LBA 500");
	zassert_equal(rhw_disk()->read(500, rd, 1), -EIO);
	zassert_ok(rhw_disk()->read(501, rd, 4));
	rhw_sim_disk_read_error_at(UINT32_MAX);
	zassert_ok(rhw_disk()->read(500, rd, 1));
}

/* fault: cut after sector k of a multi-sector write; the rest and every later write lost (named case of
 * cut_keeps_tail) */
ZTEST(rhw_sim, test_disk_cut_after_sector)
{
	card_on();
	fill_pattern(buf, 65, 0x40);
	rhw_sim_disk_cut(2, 33);
	zassert_ok(rhw_disk()->write(81920, buf, 65), "call 1 whole");
	zassert_false(rhw_sim_disk_was_cut());
	zassert_ok(rhw_disk()->write(81985, buf, 65), "call 2 is cut (the caller sees no error)");
	zassert_true(rhw_sim_disk_was_cut());
	zassert_ok(rhw_disk()->write(82050, buf, 65), "call 3 lost");
	rhw_sim_disk_peek(81985 + 32, rd);
	zassert_mem_equal(rd, buf + 32 * 512, 512, "sector 33 of the cut write kept");
	rhw_sim_disk_peek(81985 + 33, rd);
	zassert_true(all_zero(rd, 512), "sector 34 of the cut write lost");
	rhw_sim_disk_peek(81985 + 64, rd);
	zassert_true(all_zero(rd, 512), "the last sector of the cut write lost");
	rhw_sim_disk_peek(82050, rd);
	zassert_true(all_zero(rd, 512), "a later write lost");
	rhw_sim_disk_peek(81920 + 64, rd);
	zassert_mem_equal(rd, buf + 64 * 512, 512, "the write before the cut kept");
	rhw_sim_reboot();
	zassert_false(rhw_sim_disk_was_cut(), "the cut ends at the reboot");
	card_on();
	zassert_ok(rhw_disk()->write(82050, buf, 1));
	rhw_sim_disk_peek(82050, rd);
	zassert_mem_equal(rd, buf, 512, "writes work after the reboot");
}

/* fault: a stall of t ms per write */
ZTEST(rhw_sim, test_disk_stall_per_write)
{
	card_on();
	fill_pattern(buf, 1, 3);
	rhw_sim_disk_stall_ms(40);
	int64_t t0 = k_uptime_get();

	zassert_ok(rhw_disk()->write(10, buf, 1));
	zassert_ok(rhw_disk()->write(11, buf, 1));
	int64_t dt = k_uptime_get() - t0;

	zassert_true(dt >= 80 && dt <= 90, "two writes of a 40 ms stall took %lld ms", dt);
	t0 = k_uptime_get();
	zassert_ok(rhw_disk()->read(10, rd, 2));
	zassert_true(k_uptime_get() - t0 < 5, "a read does not stall");
}

/* fault: any call while VDD_SD is off is refused and counted (and the card loses its init with the rail) */
ZTEST(rhw_sim, test_disk_refused_rail_off)
{
	uint32_t n;

	zassert_equal(rhw_disk()->init(), -EIO, "init with VDD_SD off");
	zassert_equal(rhw_disk()->read(0, rd, 1), -EIO);
	zassert_equal(rhw_disk()->write(0, buf, 1), -EIO);
	zassert_equal(rhw_disk()->sector_count(&n), -EIO);
	zassert_equal(rhw_disk()->deinit(), -EIO);
	zassert_equal(rhw_sim_disk_refused(), 5);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_DISK_REFUSED), 5);
	card_on();
	zassert_ok(rhw_disk()->read(0, rd, 1));
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, false, "test"));
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, true, "test"));
	zassert_equal(rhw_disk()->read(0, rd, 1), -EIO, "after a rail cycle the card needs init again");
	zassert_equal(rhw_sim_disk_refused(), 6);
}

/* ================================================================== microphone input */

static const struct rhw_mic_cfg cfg = {
	.pcm_rate = 16000, .pcm_width = 16, .channels = 2, .chan_map_lo = 0x10, .min_pdm_clk_hz = 1200000,
	.max_pdm_clk_hz = 1650000, .gain_db = 0, .block_size = 1024, .block_count = 8,
};

static int16_t *read_block(int32_t timeout, int *res)
{
	void *b = NULL;
	size_t sz = 0;

	*res = rhw_mic()->read(&b, &sz, timeout);
	if (*res == 0) {
		zassert_equal(sz, 1024);
	}
	return b;
}

/* value: the frame counter source; a block every 16 ms; the configuration recorded */
ZTEST(rhw_sim, test_mic_counter_and_timing)
{
	struct rhw_mic_cfg got;
	int res;

	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_true(rhw_sim_mic_last_cfg(&got));
	zassert_equal(got.pcm_rate, 16000);
	zassert_equal(got.min_pdm_clk_hz, 1200000);
	zassert_equal(got.max_pdm_clk_hz, 1650000);
	zassert_equal(got.chan_map_lo, 0x10);
	zassert_equal(got.block_count, 8);
	zassert_ok(rhw_mic()->start());
	int64_t t0 = k_uptime_get();

	for (int i = 0; i < 3; i++) {
		int16_t *b = read_block(100, &res);

		zassert_ok(res);
		zassert_within(k_uptime_get() - t0, 16 * (i + 1), 1, "block %d at %d ms", i, 16 * (i + 1));
		zassert_equal(b[0], (int16_t)(256 * i), "left = frame number");
		zassert_equal(b[1], (int16_t)~(uint16_t)(256 * i), "right = its inverse");
		zassert_equal(b[2 * 255], (int16_t)(256 * i + 255));
		rhw_mic()->free_block(b);
	}
	zassert_equal(rhw_sim_mic_delivered(), 3);
	zassert_equal(rhw_sim_mic_held(), 0);
	struct rhw_mic_cfg bad = cfg;

	bad.pcm_rate = 8000;
	zassert_equal(rhw_mic()->configure(&bad), -ENOTSUP, "only the configuration of FW 4.1");
}

/* value: a sine of a set level in dBFS */
ZTEST(rhw_sim, test_mic_sine_level)
{
	int res;

	rhw_sim_mic_source(RHW_SIM_MIC_SINE, -6);
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	int16_t *b = read_block(100, &res);

	zassert_ok(res);
	/* peak of -6 dBFS: 32767 x 10^(-6/20) = 16422.7; six steps of 58409/65536 give 16422 (within 0.01 %) */
	int16_t peak = 0;

	for (int j = 0; j < 256; j++) {
		peak = MAX(peak, b[2 * j]);
		zassert_equal(b[2 * j], b[2 * j + 1], "both channels carry the sine");
	}
	zassert_within(peak, 16423, 3, "peak %d", peak);
	zassert_equal(b[0], 0, "phase 0 at frame 0");
	zassert_equal(b[2 * 4], peak, "quarter period at frame 4 (1 kHz at 16 kHz)");
	rhw_mic()->free_block(b);
}

/* fault: one channel stuck at a value */
ZTEST(rhw_sim, test_mic_stuck_channel)
{
	int res;

	rhw_sim_mic_stuck(1, 1234);
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	int16_t *b = read_block(100, &res);

	zassert_ok(res);
	for (int j = 0; j < 256; j++) {
		zassert_equal(b[2 * j + 1], 1234);
		zassert_equal(b[2 * j], (int16_t)j, "the other channel is untouched");
	}
	rhw_mic()->free_block(b);
}

/* fault: clipped samples at -32768 and 32767 in block n only */
ZTEST(rhw_sim, test_mic_clipped)
{
	int res;

	rhw_sim_mic_clip_block(1);
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	int16_t *b = read_block(100, &res);

	zassert_ok(res);
	zassert_equal(b[0], 0, "block 0 has no clipped sample");
	rhw_mic()->free_block(b);
	b = read_block(100, &res);
	zassert_ok(res);
	zassert_equal(b[0], -32768);
	zassert_equal(b[3], 32767);
	zassert_equal(b[2], (int16_t)257, "frame 1 left untouched");
	rhw_mic()->free_block(b);
}

/* fault: stop delivering after block n (named case of mic_no_block_ignored) */
ZTEST(rhw_sim, test_mic_stop_delivering)
{
	int res;

	rhw_sim_mic_stop_after(2);
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	for (int i = 0; i < 2; i++) {
		int16_t *b = read_block(100, &res);

		zassert_ok(res, "block %d delivered", i);
		rhw_mic()->free_block(b);
	}
	int64_t t0 = k_uptime_get();

	read_block(100, &res);
	zassert_equal(res, -EAGAIN, "no third block");
	zassert_within(k_uptime_get() - t0, 100, 1, "the read waited its whole timeout");
	read_block(100, &res);
	zassert_equal(res, -EAGAIN, "and none later");
	zassert_equal(rhw_sim_mic_delivered(), 2);
}

/* fault: drop block n */
ZTEST(rhw_sim, test_mic_drop_block)
{
	int res;

	rhw_sim_mic_drop_block(1);
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	int64_t t0 = k_uptime_get();
	int16_t *b = read_block(100, &res);

	zassert_ok(res);
	zassert_equal(b[0], 0);
	rhw_mic()->free_block(b);
	b = read_block(100, &res);
	zassert_ok(res);
	zassert_equal(b[0], (int16_t)512, "block 2 follows block 0");
	zassert_within(k_uptime_get() - t0, 48, 1, "at its own time");
	rhw_mic()->free_block(b);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_MIC_DROP), 1);
}

/* fault: a read error at block n, once */
ZTEST(rhw_sim, test_mic_read_error)
{
	int res;

	rhw_sim_mic_read_error(0);
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	read_block(100, &res);
	zassert_equal(res, -EIO);
	int16_t *b = read_block(100, &res);

	zassert_ok(res, "the next read works");
	zassert_equal(b[0], (int16_t)256, "block 0 is lost");
	rhw_mic()->free_block(b);
}

/* value: stop releases the filled blocks then reads fail; the pin states and the slab of 8 */
ZTEST(rhw_sim, test_mic_stop_and_slab)
{
	int res;
	int16_t *held[8];

	zassert_ok(rhw_mic()->pins_sleep());
	zassert_true(rhw_sim_mic_pins_asleep());
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->pins_default());
	zassert_false(rhw_sim_mic_pins_asleep());
	zassert_ok(rhw_mic()->start());
	for (int i = 0; i < 8; i++) {
		held[i] = read_block(100, &res);
		zassert_ok(res);
	}
	read_block(100, &res);
	zassert_equal(res, -ENOMEM, "all 8 blocks of the slab held");
	for (int i = 0; i < 8; i++) {
		rhw_mic()->free_block(held[i]);
	}
	k_sleep(K_MSEC(40));
	zassert_ok(rhw_mic()->stop());
	int got = 0;

	while (true) {
		int16_t *b = read_block(100, &res);

		if (res != 0) {
			break;
		}
		rhw_mic()->free_block(b);
		got++;
	}
	zassert_equal(res, -EIO, "after the filled blocks: an error");
	zassert_true(got >= 2, "blocks filled before the stop were delivered (%d)", got);
}

/* ================================================================== power chip */

static int vbus_calls;
static bool vbus_last;
static int chg_err_calls;
static int usb_ev[8];
static int usb_ev_n;

static void cb_vbus(bool p)
{
	vbus_calls++;
	vbus_last = p;
}

static void cb_chg_err(void)
{
	chg_err_calls++;
}

static void cb_usb_ev(enum rhw_usb_event ev)
{
	if (usb_ev_n < 8) {
		usb_ev[usb_ev_n++] = ev;
	}
}

static const struct rhw_pmic_cb pcb = { .vbus = cb_vbus, .charge_error = cb_chg_err };
static const struct rhw_usb_cb ucb = { .event = cb_usb_ev };

/* fault: VBUS in and out, now and at a time; the USB transport sees VBUS_READY and VBUS_REMOVED */
ZTEST(rhw_sim, test_pmic_vbus_now_and_at)
{
	vbus_calls = 0;
	usb_ev_n = 0;
	rhw_pmic()->set_callbacks(&pcb);
	rhw_usb()->set_callbacks(&ucb);
	zassert_false(rhw_pmic()->vbus_present());
	rhw_sim_vbus(true);
	zassert_true(rhw_pmic()->vbus_present());
	zassert_equal(vbus_calls, 1);
	zassert_true(vbus_last);
	zassert_equal(usb_ev_n, 1);
	zassert_equal(usb_ev[0], RHW_USB_VBUS_READY);
	int64_t t = k_uptime_get() + 250;

	rhw_sim_vbus_at(t, false);
	k_sleep(K_MSEC(249));
	zassert_true(rhw_pmic()->vbus_present(), "not before its time");
	k_sleep(K_MSEC(2));
	zassert_false(rhw_pmic()->vbus_present(), "removed at its time");
	zassert_equal(vbus_calls, 2);
	zassert_false(vbus_last);
	zassert_equal(usb_ev[1], RHW_USB_VBUS_REMOVED);
	int32_t i = rhw_sim_log_find(RHW_EV_PMIC_VBUS, 1);

	zassert_true(i >= 0);
	struct rhw_sim_ev e;

	rhw_sim_log_get(i, &e);
	zassert_within(e.t_us / 1000, t, 1, "logged at %lld ms", e.t_us / 1000);
}

/* fault: a charge error */
ZTEST(rhw_sim, test_pmic_charge_error)
{
	struct rhw_pmic_charge st;

	chg_err_calls = 0;
	rhw_pmic()->set_callbacks(&pcb);
	rhw_sim_vbus(true);
	zassert_ok(rhw_pmic()->charger_enable(true));
	zassert_ok(rhw_pmic()->charge_status(&st));
	zassert_equal(st.state, RREC_CHG_CC);
	zassert_equal(st.err_reason, 0);
	rhw_sim_pmic_charge_error(0x04, 0x02);
	zassert_equal(chg_err_calls, 1);
	zassert_ok(rhw_pmic()->charge_status(&st));
	zassert_equal(st.state, RREC_CHG_ERROR);
	zassert_equal(st.err_reason, 0x04);
	zassert_equal(st.err_sensor, 0x02);
}

/* fault: the current-limit bit at a sample */
ZTEST(rhw_sim, test_pmic_ilim_at_sample)
{
	struct rhw_pmic_sample s;

	rhw_sim_pmic_ilim_at_sample(3);
	for (int n = 1; n <= 5; n++) {
		zassert_ok(rhw_pmic()->sample(&s));
		zassert_equal(rhw_pmic()->ilim_active(), n == 3 ? 1 : 0, "sample %d", n);
	}
}

/* fault: any reset cause bits; read then cleared by TASKCLRERRLOG */
ZTEST(rhw_sim, test_pmic_reset_causes)
{
	uint8_t rc, er, es;

	rhw_sim_pmic_set_reset_causes(RREC_RST_SHIPMODEEXIT | RREC_RST_VSYSLOW, 0x11, 0x22);
	zassert_ok(rhw_pmic()->reset_causes(&rc, &er, &es));
	zassert_equal(rc, 0x21, "bits 0 (SHIPMODEEXIT) and 5 (VSYSLOW)");
	zassert_equal(er, 0x11);
	zassert_equal(es, 0x22);
	zassert_ok(rhw_pmic()->reset_causes_clear());
	zassert_ok(rhw_pmic()->reset_causes(&rc, &er, &es));
	zassert_equal(rc, 0);
	zassert_equal(er, 0);
	zassert_equal(es, 0);
}

/* fault: a voltage dip while MOTOR is high (T-MOTOR) */
ZTEST(rhw_sim, test_pmic_motor_dip)
{
	struct rhw_pmic_sample s;

	rhw_sim_pmic_motor_dip(25);
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3900);
	zassert_ok(rhw_motor()->set(true));
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3875);
	zassert_ok(rhw_motor()->set(false));
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3900);
}

/* value: samples from a script and from a simple cell */
ZTEST(rhw_sim, test_pmic_script_and_cell)
{
	struct rhw_pmic_sample s;
	static const struct rhw_pmic_sample scr[2] = {
		{ .mv = 3600, .ua = 4100, .temp_c_x10 = 300, .die_c_x10 = 310 },
		{ .mv = 3440, .ua = 4200, .temp_c_x10 = 301, .die_c_x10 = 311 },
	};

	rhw_sim_pmic_script(scr, 2);
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3600);
	zassert_equal(s.ua, 4100);
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3440);
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3440, "the last entry repeats");
	/* cell of 17,600 µAh half full: 3,300 + 1,050 / 2 = 3,825 mV; 1,000 µA base + 4,000 µA with VDD_MIC on */
	rhw_sim_pmic_cell(17600, 8800, 1000, 4000, 2000);
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.mv, 3825);
	zassert_equal(s.ua, 1000);
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "test"));
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, true, "test"));
	k_sleep(K_SECONDS(36));
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.ua, 7000, "base + mic + sd");
	/* the interval since the last sample is counted at the current of the rails at this sample: 7,000 µA for 36 s
	 * = 70 µAh: 8,730 / 17,600 x 1,050 = 520.8 -> 3,820 mV (run 2 expected 3,824 from 1,000 µA: my arithmetic, wrong) */
	zassert_equal(s.mv, 3820);
	rhw_sim_vbus(true);
	zassert_ok(rhw_pmic()->charger_current(15000));
	zassert_ok(rhw_pmic()->charger_enable(true));
	zassert_ok(rhw_pmic()->sample(&s));
	zassert_equal(s.ua, -15000, "charging: minus the charger current");
}

/* value: rails with the caller's name, the charger writes in order */
ZTEST(rhw_sim, test_pmic_rails_and_charger)
{
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "rec_mics_on"));
	zassert_true(rhw_pmic()->rail_get(RHW_RAIL_MIC));
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD));
	zassert_str_equal(rhw_sim_pmic_rail_caller(RHW_RAIL_MIC), "rec_mics_on");
	zassert_ok(rhw_pmic()->charger_enable(false));
	zassert_ok(rhw_pmic()->charger_current(15000));
	zassert_ok(rhw_pmic()->charger_enable(true));
	zassert_true(rhw_sim_pmic_charger_on());
	zassert_equal(rhw_sim_pmic_charger_ua(), 15000);
	int32_t a = rhw_sim_log_find(RHW_EV_PMIC_CHG_ENABLE, 0);
	int32_t b = rhw_sim_log_find(RHW_EV_PMIC_CHG_CURRENT, 0);
	int32_t c = rhw_sim_log_find(RHW_EV_PMIC_CHG_ENABLE, a + 1);

	zassert_true(a >= 0 && a < b && b < c, "disable, write, enable in order (%d %d %d)", a, b, c);
	struct rhw_sim_ev e;

	rhw_sim_log_get(rhw_sim_log_find(RHW_EV_PMIC_RAIL, 0), &e);
	zassert_str_equal(e.caller, "rec_mics_on");
	zassert_equal(e.a0, RHW_RAIL_MIC);
	zassert_equal(e.a1, 1);
}

/* value: after the ship task (no VBUS) every later call is refused and counted; SHPHLD before it */
ZTEST(rhw_sim, test_pmic_ship_refuses_later_calls)
{
	zassert_ok(rhw_pmic()->shphld_config(96));
	zassert_ok(rhw_pmic()->shphld_strobe());
	rhw_sim_vbus(true);
	zassert_ok(rhw_pmic()->ship_task());
	zassert_false(rhw_sim_shipped(), "with VBUS the chip does not enter ship mode");
	rhw_sim_vbus(false);
	zassert_ok(rhw_pmic()->ship_task());
	zassert_true(rhw_sim_shipped());
	zassert_equal(rhw_pmic()->rail_set(RHW_RAIL_SD, true, "x"), -ESHUTDOWN);
	zassert_equal(rhw_motor()->set(true), -ESHUTDOWN);
	zassert_equal(rhw_disk()->init(), -ESHUTDOWN);
	zassert_equal(rhw_sim_ship_refused(), 3);
	zassert_false(rhw_sim_motor_pin());
	rhw_sim_reboot();
	zassert_false(rhw_sim_shipped(), "a wake ends it");
	zassert_ok(rhw_motor()->set(true));
}

/* ================================================================== gauge */

/* value: the start SoC (also the power chip's "gauge's SoC"); fault: a set error */
ZTEST(rhw_sim, test_gauge_start_soc_and_error)
{
	struct rhw_pmic_sample s = { .mv = 3800, .ua = 17600, .temp_c_x10 = 250 };
	struct rhw_gauge_out o;

	rhw_sim_gauge_start_soc(500);
	zassert_ok(rhw_gauge()->start(&s));
	/* 17,600 µA for 360 s = 1,760 µAh = 10 % of 17,600 µAh: 50.0 % -> 40.0 % */
	zassert_ok(rhw_gauge()->process(&s, 360000, &o));
	zassert_equal(o.soc_x10, 400);
	zassert_equal(o.tte_s, 1440, "7,040 µAh left at 17,600 µA = 0.4 h");
	zassert_equal(o.ttf_s, UINT32_MAX);
	rhw_sim_gauge_error(-EIO);
	zassert_equal(rhw_gauge()->process(&s, 1000, &o), -EIO);
	rhw_sim_gauge_error(0);
	zassert_ok(rhw_gauge()->process(&s, 0, &o));
}

/* ================================================================== HFXO */

static volatile int hfxo_cb_calls;
static int64_t hfxo_cb_ms;

static void hfxo_cb(void)
{
	hfxo_cb_calls++;
	hfxo_cb_ms = k_uptime_get();
}

/* value: the delay before "running" */
ZTEST(rhw_sim, test_hfxo_delay)
{
	hfxo_cb_calls = 0;
	rhw_sim_hfxo_delay_ms(5);
	int64_t t0 = k_uptime_get();

	zassert_ok(rhw_hfxo()->request(hfxo_cb));
	zassert_false(rhw_hfxo()->running());
	k_sleep(K_MSEC(10));
	zassert_true(rhw_hfxo()->running());
	zassert_equal(hfxo_cb_calls, 1);
	zassert_within(hfxo_cb_ms - t0, 5, 1);
	zassert_equal(rhw_sim_hfxo_requests(), 1);
	zassert_ok(rhw_hfxo()->release());
	zassert_false(rhw_hfxo()->running());
	zassert_equal(rhw_hfxo()->release(), -EALREADY);
}

/* fault: never running */
ZTEST(rhw_sim, test_hfxo_never)
{
	hfxo_cb_calls = 0;
	rhw_sim_hfxo_never(true);
	zassert_ok(rhw_hfxo()->request(hfxo_cb));
	k_sleep(K_MSEC(500));
	zassert_false(rhw_hfxo()->running());
	zassert_equal(hfxo_cb_calls, 0);
}

/* ================================================================== USB transport */

static uint8_t rx_got[64];
static size_t rx_n;

static void cb_rx(const uint8_t *d, size_t n)
{
	memcpy(rx_got, d, MIN(n, sizeof(rx_got)));
	rx_n = n;
}

/* value: the bus speed sets the packet size; no zero-length packet; requests reach the class */
ZTEST(rhw_sim, test_usb_speed_packets)
{
	static const struct rhw_usb_cb cb = { .rx = cb_rx };
	static uint8_t out[1100];
	static uint8_t back[1300];

	for (int i = 0; i < 1100; i++) {
		out[i] = (uint8_t)i;
	}
	rhw_usb()->set_callbacks(&cb);
	zassert_equal(rhw_usb()->send(out, 16, 10), -ENODEV, "stack off");
	zassert_equal(rhw_sim_usb_host_write(out, 16), -ENODEV);
	zassert_ok(rhw_usb()->enable());
	zassert_ok(rhw_sim_usb_host_write(out, 16));
	zassert_equal(rx_n, 16);
	zassert_mem_equal(rx_got, out, 16);
	zassert_equal(rhw_usb()->speed(), RHW_USB_FS);
	rhw_sim_log_clear();
	zassert_ok(rhw_usb()->send(out, 128, 10));
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_PACKET), 2, "128 bytes = 2 packets of 64, no zero-length one");
	rhw_sim_usb_speed(RHW_USB_HS);
	rhw_sim_log_clear();
	zassert_ok(rhw_usb()->send(out, 1100, 10));
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_PACKET), 3, "1,100 bytes = 512 + 512 + 76");
	struct rhw_sim_ev e;

	rhw_sim_log_get(2, &e);
	zassert_equal(e.a0, 76);
	zassert_equal(e.a1, 512);
	zassert_equal(rhw_sim_usb_host_read(back, sizeof(back)), 128 + 1100);
	zassert_mem_equal(back + 128, out, 1100 - 128);
}

/* fault: a host that stops reading */
ZTEST(rhw_sim, test_usb_host_stops_reading)
{
	static uint8_t out[64];

	zassert_ok(rhw_usb()->enable());
	rhw_sim_usb_host_stop(true);
	int64_t t0 = k_uptime_get();

	zassert_equal(rhw_usb()->send(out, 64, 30), -EAGAIN);
	zassert_within(k_uptime_get() - t0, 30, 1, "waited its timeout");
	rhw_sim_usb_host_stop(false);
	zassert_ok(rhw_usb()->send(out, 64, 30));
}

/* ================================================================== image store */

/* fault: a write error at write call n */
ZTEST(rhw_sim, test_image_write_error)
{
	static uint8_t d[16] = { 1, 2, 3 };
	uint8_t back[16];

	zassert_ok(rhw_image()->erase_slot1());
	rhw_sim_image_write_error(2);
	zassert_ok(rhw_image()->write(0, d, 16));
	zassert_equal(rhw_image()->write(16, d, 16), -EIO);
	zassert_ok(rhw_image()->write(32, d, 16));
	rhw_sim_image_peek(16, back, 16);
	zassert_equal(back[0], 0xFF, "the failed write left the erased value");
	zassert_equal(rhw_image()->write(RREC_IMAGE_MAX_BYTES - 15, d, 16), -EINVAL, "past 999,424 bytes");
	zassert_ok(rhw_image()->write(RREC_IMAGE_MAX_BYTES - 16, d, 16), "ends at 999,424");
}

/* value: the image confirmed or not */
ZTEST(rhw_sim, test_image_confirmed_flag)
{
	zassert_equal(rhw_image()->is_confirmed(), 1);
	rhw_sim_image_set_confirmed(false);
	zassert_equal(rhw_image()->is_confirmed(), 0);
	zassert_ok(rhw_image()->confirm());
	zassert_equal(rhw_image()->is_confirmed(), 1);
	zassert_ok(rhw_image()->request_test_upgrade());
	zassert_true(rhw_sim_image_upgrade_requested());
	zassert_ok(rhw_image()->reboot(RHW_REBOOT_UPDATE));
	zassert_equal(rhw_sim_image_reboots(), 1);
	zassert_equal(rhw_sim_image_last_reboot(), RHW_REBOOT_UPDATE);
}

/* ================================================================== settings, retained memory */

/* value: the start values of the persistent settings */
ZTEST(rhw_sim, test_persist_start_values)
{
	struct rhw_persist v = { .factory_flag = 1, .time_saved = true, .saved_utc_ms = 1762992000000LL,
				 .saved_tz_min = 60, .saved_zone_known = true };
	struct rhw_persist got;

	zassert_ok(rhw_persist()->load(&got));
	zassert_equal(got.factory_flag, 0, "nothing saved after a reset");
	rhw_sim_persist_set(&v);
	zassert_ok(rhw_persist()->load(&got));
	zassert_equal(got.factory_flag, 1);
	zassert_equal(got.saved_utc_ms, 1762992000000LL);
	zassert_equal(got.saved_tz_min, 60);
	got.factory_flag = 0;
	zassert_ok(rhw_persist()->save(&got));
	rhw_sim_persist_get(&v);
	zassert_equal(v.factory_flag, 0);
}

/* value: a valid or a corrupt crash block, as the test writes it; gpregret1 */
ZTEST(rhw_sim, test_retained_valid_or_corrupt)
{
	uint8_t blk[64], back[64];
	uint8_t g;

	for (int i = 0; i < 64; i++) {
		blk[i] = (uint8_t)(0xA0 + i);
	}
	rhw_sim_retained_set(blk, sizeof(blk));
	zassert_ok(rhw_retained()->read(back, sizeof(back)));
	zassert_mem_equal(back, blk, 64);
	blk[5] ^= 0xFF;   /* a corrupt copy: the bytes the test wrote, unchanged by the store */
	rhw_sim_retained_set(blk, sizeof(blk));
	zassert_ok(rhw_retained()->read(back, sizeof(back)));
	zassert_equal(back[5], (uint8_t)(0xA5 ^ 0xFF));
	zassert_ok(rhw_retained()->clear());
	zassert_ok(rhw_retained()->read(back, sizeof(back)));
	zassert_true(all_zero(back, 64));
	zassert_equal(rhw_retained()->read(back, RREC_RETAINED_BYTES + 1), -EINVAL);
	zassert_ok(rhw_retained()->gpregret1_set(0x5A));
	zassert_ok(rhw_retained()->gpregret1_get(&g));
	zassert_equal(g, 0x5A);
}

/* ================================================================== clock, watchdog, beacon, motor, bus */

/* value: the cycle rate */
ZTEST(rhw_sim, test_clock_cycle_rate)
{
	uint64_t id;

	zassert_equal(rhw_clock()->cycles_per_sec(), 1000000);
	rhw_sim_clock_rate(32768);
	zassert_equal(rhw_clock()->cycles_per_sec(), 32768);
	uint64_t c0 = rhw_clock()->cycles();

	k_sleep(K_MSEC(1000));
	uint64_t c1 = rhw_clock()->cycles();

	zassert_within((int64_t)(c1 - c0), 32768, 330, "one second = %lld cycles (1 %% allowed for the sleep's rounding)", (long long)(c1 - c0));
	zassert_ok(rhw_clock()->device_id(&id));
	zassert_equal(id, 0x0123456789ABCDEFull);
	rhw_sim_clock_device_id(0x1111222233334444ull);
	zassert_ok(rhw_clock()->device_id(&id));
	zassert_equal(id, 0x1111222233334444ull);
}

/* value: the watchdog's "would reset" flag */
ZTEST(rhw_sim, test_wdt_would_reset)
{
	zassert_ok(rhw_wdt()->start(8000));
	zassert_equal(rhw_wdt()->start(8000), -EALREADY);
	for (int i = 0; i < 9; i++) {
		k_sleep(K_MSEC(1000));
		zassert_ok(rhw_wdt()->feed());
	}
	zassert_false(rhw_sim_wdt_would_reset(), "fed every 1 s");
	k_sleep(K_MSEC(8001));
	zassert_true(rhw_sim_wdt_would_reset(), "8,001 ms without a feed");
	zassert_ok(rhw_wdt()->feed());
	zassert_true(rhw_sim_wdt_would_reset(), "the miss stays recorded");
	zassert_equal(rhw_sim_wdt_feeds(), 10);
}

/* value: the beacon's start and stop with name, interval, power and connectable flag */
ZTEST(rhw_sim, test_beacon_recorded)
{
	struct rhw_sim_beacon b;

	zassert_ok(rhw_beacon()->start("RingCDEF", 100, 0, false));
	rhw_sim_beacon_get(&b);
	zassert_true(b.running);
	zassert_str_equal(b.name, "RingCDEF");
	zassert_equal(b.interval_ms, 100);
	zassert_equal(b.tx_dbm, 0);
	zassert_false(b.connectable);
	zassert_ok(rhw_beacon()->stop());
	rhw_sim_beacon_get(&b);
	zassert_false(b.running);
	zassert_equal(b.starts, 1);
	zassert_equal(b.stops, 1);
	zassert_ok(rhw_beacon()->start("x", 100, 0, true));
	rhw_sim_beacon_get(&b);
	zassert_true(b.connectable, "what the caller asked is recorded");
}

/* value: the motor pin and the storage bus are recorded with their times */
ZTEST(rhw_sim, test_motor_and_sdbus_recorded)
{
	struct rhw_sim_ev e;

	zassert_ok(rhw_motor()->set(true));
	k_sleep(K_MSEC(80));
	zassert_ok(rhw_motor()->set(false));
	zassert_ok(rhw_sdbus()->suspend());
	zassert_true(rhw_sim_sdbus_suspended());
	zassert_ok(rhw_sdbus()->resume());
	zassert_false(rhw_sim_sdbus_suspended());
	rhw_sim_log_get(0, &e);
	int64_t t_on = e.t_us;

	zassert_equal(e.kind, RHW_EV_MOTOR);
	zassert_equal(e.a0, 1);
	rhw_sim_log_get(1, &e);
	zassert_equal(e.a0, 0);
	zassert_within(e.t_us - t_on, 80000, 200, "MOTOR high for 80 ms");
	rhw_sim_log_get(2, &e);
	zassert_equal(e.kind, RHW_EV_SDBUS_SUSPEND);
	rhw_sim_log_get(3, &e);
	zassert_equal(e.kind, RHW_EV_SDBUS_RESUME);
}

/* ================================================================== the event log and the resets */

/* the log keeps the order of the calls and their times */
ZTEST(rhw_sim, test_event_log_order_and_time)
{
	struct rhw_sim_ev e;
	int64_t t0 = k_ticks_to_us_floor64(k_uptime_ticks());

	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, true, "rst_mount"));
	k_sleep(K_MSEC(1));
	zassert_ok(rhw_sdbus()->resume());
	zassert_ok(rhw_disk()->init());
	k_sleep(K_MSEC(5));
	zassert_ok(rhw_disk()->deinit());
	zassert_ok(rhw_sdbus()->suspend());
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_SD, false, "rst_unmount"));
	static const uint16_t want[] = {
		RHW_EV_PMIC_RAIL, RHW_EV_SDBUS_RESUME, RHW_EV_DISK_INIT, RHW_EV_DISK_DEINIT, RHW_EV_SDBUS_SUSPEND,
		RHW_EV_PMIC_RAIL,
	};
	static const int64_t at_us[] = { 0, 1000, 1000, 6000, 6000, 6000 };

	zassert_equal(rhw_sim_log_count(), ARRAY_SIZE(want));
	for (uint32_t i = 0; i < ARRAY_SIZE(want); i++) {
		zassert_true(rhw_sim_log_get(i, &e));
		zassert_equal(e.seq, i, "seq");
		zassert_equal(e.kind, want[i], "entry %u kind %u", i, e.kind);
		zassert_within(e.t_us - t0, at_us[i], 200, "entry %u at %lld us", i, (long long)(e.t_us - t0));
	}
	rhw_sim_log_get(0, &e);
	zassert_str_equal(e.caller, "rst_mount");
	rhw_sim_log_get(5, &e);
	zassert_str_equal(e.caller, "rst_unmount");
	zassert_false(rhw_sim_log_get(6, &e));
	zassert_equal(rhw_sim_log_overflow(), 0);
	/* a full log counts what it could not keep */
	for (int i = 0; i < CONFIG_RING_RHW_SIM_LOG_SIZE; i++) {
		(void)rhw_motor()->set(false);
	}
	zassert_equal(rhw_sim_log_count(), CONFIG_RING_RHW_SIM_LOG_SIZE);
	zassert_equal(rhw_sim_log_overflow(), ARRAY_SIZE(want));
}

static int hook_calls;

static void hook(void)
{
	hook_calls++;
}

/* rhw_sim_reboot() keeps exactly the card, the settings and the retained memory (named case of reboot_wipes_card) */
ZTEST(rhw_sim, test_reboot_keeps_card_settings_retained)
{
	struct rhw_persist v = { .factory_flag = 1, .time_saved = true, .saved_utc_ms = 42 };
	struct rhw_persist got;
	uint8_t blk[32];
	uint8_t back[32];
	int res;

	hook_calls = 0;
	zassert_ok(rhw_sim_add_reboot_hook(hook));
	zassert_ok(rhw_sim_add_reboot_hook(hook), "twice counts once");
	/* the three kept stores */
	card_on();
	fill_pattern(buf, 2, 0x77);
	zassert_ok(rhw_disk()->write(81920, buf, 2));
	rhw_sim_persist_set(&v);
	memset(blk, 0x3C, sizeof(blk));
	rhw_sim_retained_set(blk, sizeof(blk));
	rhw_sim_gpregret1_set(0x42);
	/* ring state that must go */
	zassert_ok(rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "rec_mics_on"));
	zassert_ok(rhw_pmic()->charger_enable(true));
	zassert_ok(rhw_hfxo()->request(NULL));
	zassert_ok(rhw_motor()->set(true));
	zassert_ok(rhw_usb()->enable());
	zassert_ok(rhw_wdt()->start(8000));
	zassert_ok(rhw_beacon()->start("RingCDEF", 100, 0, false));
	zassert_ok(rhw_image()->erase_slot1());
	zassert_ok(rhw_image()->write(0, buf, 16));
	zassert_ok(rhw_image()->request_test_upgrade());
	zassert_ok(rhw_mic()->configure(&cfg));
	zassert_ok(rhw_mic()->start());
	read_block(100, &res);
	zassert_ok(res);

	rhw_sim_reboot();

	zassert_equal(hook_calls, 1, "each hook once");
	zassert_equal(rhw_sim_reboots(), 1);
	/* kept */
	rhw_sim_disk_peek(81920, rd);
	zassert_mem_equal(rd, buf, 512, "card sector 81,920 kept");
	rhw_sim_disk_peek(81921, rd);
	zassert_mem_equal(rd, buf + 512, 512, "card sector 81,921 kept");
	zassert_equal(rhw_sim_disk_stored(), 2);
	rhw_sim_persist_get(&got);
	zassert_equal(got.factory_flag, 1, "settings kept");
	zassert_equal(got.saved_utc_ms, 42);
	rhw_sim_retained_get(back, sizeof(back));
	zassert_mem_equal(back, blk, sizeof(blk), "retained memory kept");
	zassert_equal(rhw_sim_gpregret1_get(), 0x42, "gpregret1 kept");
	/* cleared */
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_MIC));
	zassert_false(rhw_pmic()->rail_get(RHW_RAIL_SD));
	zassert_false(rhw_sim_pmic_charger_on());
	zassert_false(rhw_hfxo()->running());
	zassert_equal(rhw_sim_hfxo_requests(), 0);
	zassert_false(rhw_sim_motor_pin());
	zassert_false(rhw_sim_usb_enabled());
	zassert_false(rhw_sim_wdt_started());
	struct rhw_sim_beacon b;

	rhw_sim_beacon_get(&b);
	zassert_false(b.running);
	zassert_false(rhw_sim_image_upgrade_requested());
	uint8_t im[4];

	rhw_sim_image_peek(0, im, 4);
	zassert_equal(im[0], 0xFF, "slot 1 not kept (MCUboot is not simulated)");
	zassert_equal(rhw_sim_mic_held(), 0, "no block held");
	read_block(10, &res);
	zassert_equal(res, -EIO, "the input is stopped");
	zassert_equal(rhw_disk()->read(81920, rd, 1), -EIO, "the card needs VDD_SD and init again");
	int32_t r = rhw_sim_log_find(RHW_EV_SIM_REBOOT, 0);

	zassert_true(r >= 0, "the log is kept and holds the reboot");
	/* rhw_sim_reset, unlike the reboot, empties the stores */
	rhw_sim_reset();
	rhw_sim_disk_peek(81920, rd);
	zassert_true(all_zero(rd, 512));
	rhw_sim_persist_get(&got);
	zassert_equal(got.factory_flag, 0);
	zassert_equal(rhw_sim_gpregret1_get(), 0);
}

/* the active instances are the simulated ones and a real one cannot be registered in a simulated build */
ZTEST(rhw_sim, test_registration_refused_in_sim)
{
	zassert_equal(rhw_register_disk(rhw_disk()), -EPERM);
	zassert_equal(rhw_register_pmic(NULL), -EINVAL);
	zassert_equal(rhw_register_beacon(rhw_beacon()), -EPERM);
	zassert_not_null(rhw_clock());
	zassert_true(rhw_clock() != &rhw_clock_real, "the simulated clock is active");
}

/* ================================================================== kit facts */

/* K14: sys_clock_hw_cycles_per_sec() and k_cycle_get_32() on the target (through the real clock of rhw) */
ZTEST(rhw_sim, test_k14_real_clock)
{
	uint32_t hz = rhw_clock_real.cycles_per_sec();
	uint32_t c32a = k_cycle_get_32();
	uint64_t ca = rhw_clock_real.cycles();
	int64_t ma = rhw_clock_real.now_ms();

	k_sleep(K_MSEC(100));
	uint32_t c32b = k_cycle_get_32();
	uint64_t cb = rhw_clock_real.cycles();
	int64_t mb = rhw_clock_real.now_ms();

	printk("K14: sys_clock_hw_cycles_per_sec %u; k_cycle_get_32 advanced %u in 100 ms; rhw cycles advanced %llu; ms %lld\n",
	       hz, c32b - c32a, (unsigned long long)(cb - ca), (long long)(mb - ma));
	zassert_true(hz > 0);
	zassert_within(mb - ma, 100, 1);
	zassert_within((int64_t)(c32b - c32a), (int64_t)hz / 10, (int64_t)hz / 100 + 2, "k_cycle_get_32 over 100 ms");
	zassert_within((int64_t)(cb - ca), (int64_t)hz / 10, (int64_t)hz / 100 + 2, "rhw cycles over 100 ms");
}

/* K15: the target holds the sparse card store at its full pool and three chunk buffers of 33,280 bytes */
ZTEST(rhw_sim, test_k15_ram)
{
	static uint8_t ring[3][RREC_CHUNK_BYTES];

	card_on();
	for (int c = 0; c < 3; c++) {
		memset(ring[c], 0x10 + c, sizeof(ring[c]));
	}
	uint32_t lba = 81920;

	while (rhw_sim_disk_stored() + 65 <= CONFIG_RING_RHW_SIM_DISK_POOL) {
		zassert_ok(rhw_disk()->write(lba, ring[(lba / 65) % 3], 65));
		lba += 65;
	}
	zassert_equal(rhw_disk()->write(lba, ring[0], 65), -ENOSPC, "the pool is full");
	zassert_ok(rhw_disk()->read(81920 + 65, rd, 65));
	zassert_mem_equal(rd, ring[((81920 + 65) / 65) % 3], 65 * 512);
	printk("K15: pool %d sectors (%d bytes) and 3 x %u chunk bytes held on this target\n",
	       CONFIG_RING_RHW_SIM_DISK_POOL, CONFIG_RING_RHW_SIM_DISK_POOL * 512, RREC_CHUNK_BYTES);
}

/* ================================================================== the public headers */

int hdr_rrec_spec_compiled(void);
int hdr_rhw_compiled(void);
int hdr_rhw_sim_compiled(void);
int hdr_rst_compiled(void);
int hdr_rau_compiled(void);
int hdr_rxf_compiled(void);
int hdr_rpw_compiled(void);
int hdr_rmo_compiled(void);
int hdr_rsy_compiled(void);
int hdr_rfa_compiled(void);
int hdr_rrec_compiled(void);

/* each public header compiled alone in its own file (src/hdr_*.c) and linked here */
ZTEST(rhw_sim, test_headers_compiled)
{
	int n = hdr_rrec_spec_compiled() + hdr_rhw_compiled() + hdr_rhw_sim_compiled() + hdr_rst_compiled() +
		hdr_rau_compiled() + hdr_rxf_compiled() + hdr_rpw_compiled() + hdr_rmo_compiled() +
		hdr_rsy_compiled() + hdr_rfa_compiled() + hdr_rrec_compiled();

	zassert_equal(n, 11);
}
