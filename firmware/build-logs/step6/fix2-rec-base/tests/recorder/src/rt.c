/* rt.c: the harness of the recorder's suites (see rt.h). */
#include <errno.h>
#include <string.h>

#include <zephyr/sys/byteorder.h>
#include <zephyr/sys/crc.h>

#include <ring_devices/rdev_logic.h>
#include <ring_inbox/rinbox.h>
#include <ring_iphone/ripl.h>
#include <ring_core/rc_sm.h>

#include "rt.h"

/* ------------------------------------------------------------------ logs of the wrappers */
#define STEPS_MAX 512
#define ACTS_MAX 1024
static struct rt_step steps[STEPS_MAX];
static uint32_t n_steps;
static struct rt_act acts[ACTS_MAX];
static uint32_t n_acts;
static uint32_t mic_at_screens;
static uint32_t screens_told;

uint32_t rt_steps(void)
{
	return MIN(n_steps, STEPS_MAX);
}

struct rt_step rt_step_get(uint32_t i)
{
	return steps[i];
}

bool rt_row_seen(int row)
{
	for (uint32_t i = 0; i < rt_steps(); i++) {
		if (steps[i].row == row) {
			return true;
		}
	}
	return false;
}

void rt_steps_clear(void)
{
	n_steps = 0;
	n_acts = 0;
	mic_at_screens = 0;
	screens_told = 0;
}

uint32_t rt_acts(void)
{
	return MIN(n_acts, ACTS_MAX);
}

struct rt_act rt_act_get(uint32_t i)
{
	return acts[i];
}

uint32_t rt_mic_at_screens(void)
{
	return mic_at_screens;
}

uint32_t rt_screens_told(void)
{
	return screens_told;
}

/* the product's glue ops (app/src/main.c), each wrapped to keep a log */
static void w_action(enum rc_action a, rc_ms_t t)
{
	if (n_acts < ACTS_MAX) {
		acts[n_acts].a = (uint8_t)a;
		acts[n_acts].t_ms = t;   /* the time of the core step the glue gives */
	}
	n_acts++;
	rrec_action(a, t);
}

static bool w_after(const struct rc_actions *a, enum rc_event ev, enum rc_state st, rc_ms_t t)
{
	if (n_steps < STEPS_MAX) {
		steps[n_steps].row = a->last_row;
		steps[n_steps].ev = (uint8_t)ev;
		steps[n_steps].state = (uint8_t)st;
		steps[n_steps].t_ms = k_uptime_get();
	}
	n_steps++;
	return rrec_glue_after(a, ev, st, t);
}

static const struct rglue_ops gops = {
	.action = w_action,
	.after = w_after,
	.screen_fact = rrec_glue_screen_fact,
	.sign_start = rrec_sign_hook,
	.factory_gesture = rrec_factory_gesture,
};

/* ------------------------------------------------------------------ stand-in reads of the screens (no inbox, no devices) */
static uint8_t o_inbox_count(void)
{
	return 0;
}

static bool o_inbox_get(uint8_t i, struct rinbox_item *o)
{
	ARG_UNUSED(i);
	ARG_UNUSED(o);
	return false;
}

static void o_media_get(struct ripl_media *o)
{
	ripl_media_init(o);
}

static bool o_ams_ready(void)
{
	return false;
}

/* called inside rscr_glue_after (load_view): the moment the screens learn of a core state */
static uint8_t o_paired(void)
{
	k_tid_t me = k_current_get();
	const char *nm = k_thread_name_get(me);

	if (me != rscr_thread_id() && (nm == NULL || strcmp(nm, "rpw") != 0)) {
		screens_told++;
		if (rc_core_state(rglue_core()) != RC_ST_RECORDING && rhw_pmic()->rail_get(RHW_RAIL_MIC) &&
		    atomic_get(&rrec_st.test_recording) == 0) {
			mic_at_screens++;
		}
	}
	return 0;
}

static uint8_t o_active(void)
{
	return RDEV_NONE;
}

static bool o_link(void)
{
	return false;
}

static int o_uid(uint32_t uid)
{
	ARG_UNUSED(uid);
	return 0;
}

static int o_slot(uint8_t slot)
{
	ARG_UNUSED(slot);
	return 0;
}

static void o_void(void)
{
}

static void o_bool(bool on)
{
	ARG_UNUSED(on);
}

static void o_mode(enum rctl_mode m)
{
	ARG_UNUSED(m);
}

static int o_power_off(void)
{
	return rglue_event_try(RC_EV_MENU_POWER_OFF);   /* the product's rule: -EBUSY when the glue is busy */
}

static const struct rscr_ops sops = {
	.inbox_count = o_inbox_count, .inbox_get = o_inbox_get, .media_get = o_media_get, .ams_ready = o_ams_ready,
	.paired_mask = o_paired, .active = o_active, .link_up = o_link, .dismiss = o_uid, .positive = o_uid,
	.mark_read = o_uid, .pair_open = o_slot, .pair_cancel = o_void, .dev_use = o_slot, .dev_remove = o_slot,
	.control_active = o_bool, .set_mode = o_mode, .power_off = o_power_off, .vibration = o_bool, .now_ms = NULL,
};

/* ------------------------------------------------------------------ world */
void rt_sleep(int32_t ms)
{
	k_sleep(K_MSEC(ms));
}

void rt_settle(void)
{
	int quiet = 0;

	for (int i = 0; i < 1000 && quiet < 3; i++) {
		k_sleep(K_MSEC(20));
		quiet = rrec_idle() ? quiet + 1 : 0;
	}
}

static bool glue_started;
bool rt_screens_started;

void rt_setup(void)
{
	if (!rt_screens_started) {
		rt_screens_started = true;
		zassert_equal(rscr_start(&sops), 0, "screens start on the memory display");
	}
	if (!glue_started) {
		glue_started = true;
		rglue_init(&gops, RC_ST_BOOT);
	}
}

void rt_setup_no_screens(void)
{
	if (!glue_started) {
		glue_started = true;
		rglue_init(&gops, RC_ST_BOOT);
	}
}

void rt_core_at(enum rc_state s)
{
	rc_core_init(rglue_core(), RC_CENTRE_SW2, s, k_uptime_get());
	rc_core_set_sign_hook(rglue_core(), rrec_sign_hook, NULL);
	rrec_st.core_state = (uint8_t)s;
}

static void apply(const struct rt_boot *b)
{
	static struct rhw_pmic_sample sc[2];
	struct rhw_persist p;

	if (b == NULL) {
		return;
	}
	if (b->chunks != 0) {
		rhw_sim_disk_set_sectors(RREC_LBA_CHUNK_FIRST + b->chunks * RREC_CHUNK_SECTORS);
	}
	if (b->init_fail != 0) {
		rhw_sim_disk_fail_init(b->init_fail);
	}
	if (b->mv != 0) {
		for (int i = 0; i < 2; i++) {
			sc[i].mv = i == 0 ? b->mv : (b->mv_next != 0 ? b->mv_next : b->mv);
			sc[i].ua = b->ua != 0 ? b->ua : 3000;
			sc[i].temp_c_x10 = 250;
			sc[i].die_c_x10 = 300;
		}
		rhw_sim_pmic_script(sc, 2);
	}
	if (b->chg_forced != 0) {
		rhw_sim_pmic_charge_state((int)b->chg_forced - 1);
	}
	if (b->gauge_uah != 0) {
		rhw_sim_gauge_capacity(b->gauge_uah);
	}
	if (b->soc_x10 != 0) {
		rhw_sim_gauge_start_soc(b->soc_x10);
	}
	if (b->factory_flag) {
		memset(&p, 0, sizeof(p));
		p.factory_flag = 1;
		rhw_sim_persist_set(&p);
	}
	if (b->vbus) {
		rhw_sim_pmic_vbus(true);
	}
	if (b->unconfirmed) {
		rhw_sim_image_set_confirmed(false);
	}
}

static void boot_now(const struct rt_boot *b)
{
	rhw_sim_log_clear();
	rrec_tap_clear();
	rt_steps_clear();
	rt_core_at(RC_ST_BOOT);
	(void)rrec_boot();
	if (b != NULL && b->vbus) {
		rhw_sim_usb_event(RHW_USB_VBUS_READY);   /* the controller reports VBUS at its start (the class enables the stack) */
	}
	rt_settle();
}

void rt_fresh(const struct rt_boot *b)
{
	rt_settle();
	rmd_inject_fail(0);
	rscr_test_force_down(false);
	rt_sleep(50);
	rhw_sim_reset();
	rhw_sim_reboot();   /* every unit's RAM state back to reset values (the audio part waits for its capture loop, F1) */
	apply(b);
	boot_now(b);
}

void rt_reboot(const struct rt_boot *b)
{
	rt_sleep(100);
	rhw_sim_reboot();   /* the audio part waits for its capture loop (finding F1): no sleep after it */
	apply(b);
	boot_now(b);
}

void rt_long(void)
{
	rglue_input(RC_SW_CENTRE, true);
	rt_sleep(1100);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(100);
	rt_settle();
}

void rt_short(void)
{
	rglue_input(RC_SW_CENTRE, true);
	rt_sleep(100);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(500);
	rt_settle();
}

void rt_double(void)
{
	rglue_input(RC_SW_CENTRE, true);
	rt_sleep(100);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(150);
	rglue_input(RC_SW_CENTRE, true);
	rt_sleep(100);
	rglue_input(RC_SW_CENTRE, false);
	rt_sleep(500);
	rt_settle();
}

void rt_vbus(bool on)
{
	rhw_sim_vbus(on);
	rt_sleep(50);
	rt_settle();
}

void rt_usb_ready(void)
{
	rhw_sim_usb_event(RHW_USB_VBUS_READY);
	rt_settle();
}

void rt_usb_configured(void)
{
	rhw_sim_usb_event(RHW_USB_CONFIGURED);
	rt_sleep(20);
	rt_settle();
}

int rt_usb_send(uint8_t op, const uint8_t *pl, uint32_t len)
{
	static uint8_t req[RREC_MSG_HEADER_BYTES + RREC_FW_DATA_MAX + 16];
	static uint32_t tag = 0x1000;
	static uint8_t junk[256];

	while (rhw_sim_usb_host_read(junk, sizeof(junk)) > 0) {
	}
	tag++;
	sys_put_le16(RREC_MSG_MAGIC, &req[RREC_MSG_OFF_MAGIC]);
	req[RREC_MSG_OFF_OPCODE] = op;
	req[RREC_MSG_OFF_STATUS] = 0;
	sys_put_le32(tag, &req[RREC_MSG_OFF_TAG]);
	sys_put_le32(len, &req[RREC_MSG_OFF_LENGTH]);
	sys_put_le32(len != 0 ? crc32_ieee(pl, len) : 0, &req[RREC_MSG_OFF_CRC]);
	if (len != 0) {
		memcpy(&req[RREC_MSG_HEADER_BYTES], pl, len);
	}
	return rhw_sim_usb_host_write(req, RREC_MSG_HEADER_BYTES + len);
}

int rt_usb_recv(uint8_t *resp, size_t max, uint8_t *st, int32_t timeout_ms)
{
	size_t n = 0;
	uint32_t want;

	for (int32_t w = 0; w < timeout_ms; w += 10) {
		k_sleep(K_MSEC(10));
		n += rhw_sim_usb_host_read(&resp[n], max - n);
		if (n >= RREC_MSG_HEADER_BYTES) {
			want = RREC_MSG_HEADER_BYTES + sys_get_le32(&resp[RREC_MSG_OFF_LENGTH]);
			if (n >= want || n >= max) {
				break;
			}
		}
	}
	*st = n >= RREC_MSG_HEADER_BYTES ? resp[RREC_MSG_OFF_STATUS] : 0xFE;
	return (int)n;
}

int rt_usb(uint8_t op, const uint8_t *pl, uint32_t len, uint8_t *resp, size_t max, uint8_t *st)
{
	int n;

	if (rt_usb_send(op, pl, len) != 0) {
		*st = 0xFF;
		return -ENODEV;
	}
	n = rt_usb_recv(resp, max, st, 15000);
	rt_sleep(20);
	rt_settle();
	return n;
}

void rt_samples(uint16_t mv)
{
	static struct rhw_pmic_sample s;

	s.mv = mv;
	s.ua = 3000;
	s.temp_c_x10 = 250;
	s.die_c_x10 = 300;
	rhw_sim_pmic_script(&s, 1);
}

enum rc_state rt_state(void)
{
	/* read without the glue's lock: ship mode holds the lock while it waits for VBUS removal (FW l.939) */
	return rc_core_state(rglue_core());
}

bool rt_mic(void)
{
	return rhw_pmic()->rail_get(RHW_RAIL_MIC);
}

bool rt_sd(void)
{
	return rhw_pmic()->rail_get(RHW_RAIL_SD);
}

/* ------------------------------------------------------------------ the simulated event log */
int32_t rt_find(uint16_t kind, int64_t a0, int64_t a1, uint32_t from)
{
	struct rhw_sim_ev e;

	for (uint32_t i = from; rhw_sim_log_get(i, &e); i++) {
		if (e.kind == kind && (a0 < 0 || e.a0 == a0) && (a1 < 0 || e.a1 == a1)) {
			return (int32_t)i;
		}
	}
	return -1;
}

int32_t rt_find_rail(enum rhw_rail rail, bool on, uint32_t from)
{
	return rt_find(RHW_EV_PMIC_RAIL, rail, on ? 1 : 0, from);
}

int64_t rt_ev_us(int32_t i)
{
	struct rhw_sim_ev e;

	if (i < 0 || !rhw_sim_log_get((uint32_t)i, &e)) {
		return -1;
	}
	return e.t_us;
}

uint32_t rt_count_rail(enum rhw_rail rail, bool on)
{
	uint32_t n = 0;

	for (int32_t i = rt_find_rail(rail, on, 0); i >= 0; i = rt_find_rail(rail, on, (uint32_t)i + 1)) {
		n++;
	}
	return n;
}

/* ------------------------------------------------------------------ the display */
static uint8_t pic[RSCR_W * RSCR_H * 3];

bool rt_red_dot(void)
{
	int n = 0;

	rscr_sync();
	rscr_capture_rgb(pic);
	/* the red dot of SCR_RECORDING and SCR_REC_DIM: x 14 to 30, y 84 to 100 (tests/screens, test_draw.c) */
	for (int y = 84; y <= 100; y++) {
		for (int x = 14; x <= 30; x++) {
			const uint8_t *p = &pic[(y * RSCR_W + x) * 3];

			n += (p[0] > 200 && p[1] < 100 && p[2] < 100) ? 1 : 0;
		}
	}
	return n >= 40;
}

bool rt_blanked(void)
{
	struct rmd_stats m;

	rscr_sync();
	rmd_stats_get(&m);
	return m.blanked;
}

/* ------------------------------------------------------------------ rows of FW 1.2 */
const struct rc_row *rt_row(int row)
{
	for (uint16_t i = 0; i < rc_table_rows; i++) {
		if (rc_table[i].row == row) {
			return &rc_table[i];
		}
	}
	return NULL;
}

bool rt_cut_seen;

/* a card whose superblock says a recording was open: a recording, then the power cut (later writes lost) */
static void open_flag_card(void)
{
	rt_fresh(NULL);
	rt_long();
	rt_sleep(300);
	rhw_sim_disk_cut(1, 0);
	rt_sleep(800);
	rt_cut_seen = rhw_sim_disk_was_cut();   /* read before the reboot, which ends the cut (rhw_sim.h) */
}

/* the LBA of the open recording's first chunk, from the superblock on the simulated card (FW l.594, l.597, l.606, l.531):
 * the valid copy with the higher sb_seq (magic checked; the CRC is the store's business) */
static uint32_t open_first_chunk_lba(void)
{
	static uint8_t s[2][RREC_SECTOR_BYTES];
	int pick = -1;

	rhw_sim_disk_peek(RREC_LBA_SB_A, s[0]);
	rhw_sim_disk_peek(RREC_LBA_SB_B, s[1]);
	for (int i = 0; i < 2; i++) {
		if (sys_get_le32(&s[i][RREC_SB_OFF_MAGIC]) != RREC_SB_MAGIC) {
			continue;
		}
		if (pick < 0 || sys_get_le32(&s[i][RREC_SB_OFF_SB_SEQ]) > sys_get_le32(&s[pick][RREC_SB_OFF_SB_SEQ])) {
			pick = i;
		}
	}
	if (pick < 0) {
		return RREC_LBA_CHUNK_FIRST;
	}
	return RREC_LBA_CHUNK_FIRST + (sys_get_le32(&s[pick][RREC_SB_OFF_OPEN_FIRST_CHUNK]) %
				       sys_get_le32(&s[pick][RREC_SB_OFF_CHUNK_COUNT_TOTAL])) * RREC_CHUNK_SECTORS;
}

static void to_transfer(void)
{
	rt_vbus(true);
	rt_usb_configured();
}

static void fw_end_sequence(void)
{
	static uint8_t resp[64];
	static const uint8_t img[64] = { 1, 2, 3, 4, 5, 6, 7, 8 };
	uint8_t pl[8 + sizeof(img)];
	uint8_t st;

	sys_put_le32(sizeof(img), pl);
	sys_put_le32(crc32_ieee(img, sizeof(img)), &pl[4]);
	(void)rt_usb(RREC_OP_FW_BEGIN, pl, 8, resp, sizeof(resp), &st);
	sys_put_le32(0, pl);
	memcpy(&pl[4], img, sizeof(img));
	(void)rt_usb(RREC_OP_FW_DATA, pl, 4 + sizeof(img), resp, sizeof(resp), &st);
	(void)rt_usb(RREC_OP_FW_END, NULL, 0, resp, sizeof(resp), &st);
}

#if defined(CONFIG_RING_FACTORY)
static void factory_cmd(uint8_t sub)
{
	static uint8_t resp[512];
	uint8_t st;

	(void)rt_usb(RREC_OP_FACTORY, &sub, 1, resp, sizeof(resp), &st);
}

static void to_factory(void)
{
	struct rt_boot b = { .factory_flag = true };

	rt_fresh(&b);
	to_transfer();
	factory_cmd(RREC_FAC_ENTER);
}
#endif

static void mic_fault(void)
{
	rt_fresh(NULL);
	rt_long();
	for (int i = 0; i < 3 && rt_state() == RC_ST_RECORDING; i++) {
		uint32_t d = rhw_sim_mic_delivered();

		rhw_sim_mic_stop_after((int32_t)d + 2);
		rt_sleep(600);
		rt_settle();
		TC_PRINT("mic fault: try %d, blocks delivered %u, state %s, FAULT_MIC records %u, recorder idle %d\n", i + 1, d,
			 rc_state_name(rt_state()), rrec_tap_count_code(RREC_LOG_FAULT_MIC), rrec_idle());
	}
}

static void to_charger_error(void)
{
	struct rt_boot b = { .mv = 3900, .mv_next = 3250 };

	rt_fresh(&b);
	rt_vbus(true);
	rhw_sim_pmic_charge_error(1, 2);
	rt_sleep(50);
	rt_settle();
}

int rt_run_row(int row)
{
	struct rt_boot b;

	memset(&b, 0, sizeof(b));
	switch (row) {
	case 1:  /* SHIP, VBUS appears (the core's model; on the ring the chip starts from no power) */
	case 2:  /* OFF, VBUS appears */
		rt_fresh(NULL);
		rt_core_at(row == 1 ? RC_ST_SHIP : RC_ST_OFF);
		rt_steps_clear();
		rt_vbus(true);
		break;
	case 3:
		rt_fresh(NULL);
		break;
	case 4:
	case 9:
		open_flag_card();
		rt_reboot(NULL);
		break;
	case 5:
		b.vbus = true;
		rt_fresh(&b);
		break;
	case 6:
		b.init_fail = 3;
		rt_fresh(&b);
		break;
	case 7:
		b.mv = 3250;     /* at or under 3.30 V: B2 (FW l.117) */
		rt_fresh(&b);
		break;
	case 8:
		b.mv = 3400;     /* at or under 3.45 V: B5 (FW l.116) */
		rt_fresh(&b);
		break;
	case 10:
		open_flag_card();
		b.vbus = true;
		rt_reboot(&b);
		break;
	case 11:
		open_flag_card();
		rhw_sim_disk_read_error_at(open_first_chunk_lba());   /* the first chunk the scan reads */
		TC_PRINT("row 11: read error set at LBA %u (the open recording's first chunk)\n", open_first_chunk_lba());
		rt_reboot(NULL);
		break;
	case 12:
		rt_fresh(NULL);
		rt_long();
		break;
	case 13:  /* STANDBY with the open flag set (the fact the caller owns) */
		rt_fresh(NULL);
		rrec_st.fact_open = true;
		rrec_st.fact_open_pending = true;
		rt_long();
		break;
	case 14:  /* STANDBY with the battery fact at B5 */
		rt_fresh(NULL);
		rglue_core()->facts.batt = RC_BATT_B5;
		rt_long();
		break;
	case 15:  /* STANDBY with free space at SFULL: a card of 16 chunks, the core started in STANDBY with the fact */
		b.chunks = RREC_SFULL_CHUNKS;
		rt_fresh(&b);
		rt_core_at(RC_ST_STANDBY);
		rglue_core()->facts.storage_full = true;
		rt_long();
		break;
	case 16:
		rt_fresh(NULL);
		rscr_test_force_down(true);   /* the screens refuse the sign */
		rt_long();
		break;
	case 17:
		rt_fresh(NULL);
		rt_short();
		break;
	case 18:
		rt_fresh(NULL);
		rt_double();
		break;
	case 19:
		rt_fresh(NULL);
		rglue_event(RC_EV_MENU_POWER_OFF);
		rt_settle();
		break;
	case 20:
		rt_fresh(NULL);
		rt_vbus(true);
		break;
	case 21:
		b.soc_x10 = 151;   /* just above 15 % (FW l.115) */
		b.gauge_uah = 1000;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 22:
		b.mv = 3900;
		b.mv_next = 3400;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 23:
		b.mv = 3900;
		b.mv_next = 3250;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 24:
		b.chunks = RREC_SFULL_CHUNKS;
		rt_fresh(&b);
		break;
	case 25:
		b.init_fail = 1000;
		rt_fresh(&b);
		rt_vbus(true);
		rt_vbus(false);
		break;
	case 26:
		rt_fresh(NULL);
		rt_long();
		rt_sleep(1000);
		rt_long();
		break;
	case 27:
		rt_fresh(NULL);
		rt_long();
		rt_short();
		break;
	case 28:
		rt_fresh(NULL);
		rt_long();
		rt_double();
		break;
	case 29:
		rt_fresh(NULL);
		rt_long();
		rglue_event(RC_EV_BLE_HIGHLIGHT);
		rt_settle();
		break;
	case 30:
		rt_fresh(NULL);
		rt_long();
		rt_vbus(true);
		break;
	case 31:
		b.soc_x10 = 151;
		b.gauge_uah = 1000;
		rt_fresh(&b);
		rt_long();
		rt_sleep(5000);
		rt_settle();
		break;
	case 32:
		b.mv = 3900;
		b.mv_next = 2900;   /* mean of the two (3,400 mV) at or under 3.45 V (FW l.116, l.114) */
		rt_fresh(&b);
		rt_long();
		rt_sleep(2500);
		rt_settle();
		break;
	case 33:
		b.mv = 3900;
		b.mv_next = 2500;   /* mean of the two (3,200 mV) at or under 3.30 V (FW l.117) */
		rt_fresh(&b);
		rt_long();
		rt_sleep(2500);
		rt_settle();
		break;
	case 34:
		b.chunks = RREC_S30_CHUNKS + 2;
		rt_fresh(&b);
		rt_long();
		rt_sleep(2500);
		rt_settle();
		break;
	case 35:
		b.chunks = RREC_SFULL_CHUNKS + 2;
		rt_fresh(&b);
		rt_long();
		rt_sleep(2500);
		rt_settle();
		break;
	case 36:
		rt_fresh(NULL);
		rt_long();
		rhw_sim_disk_fail_write(1, RREC_WRITE_TRIES);
		rt_sleep(1500);
		rt_settle();
		break;
	case 37:
		mic_fault();
		break;
	case 38:  /* stands for the cut: the event the core's table names */
		rt_fresh(NULL);
		rt_long();
		rglue_event(RC_EV_POWER_LOSS);
		rt_settle();
		break;
	case 39:
		rt_fresh(NULL);
		to_transfer();
		break;
	case 40:
		rt_fresh(NULL);
		rt_vbus(true);
		rt_vbus(false);
		break;
	case 41:
		b.chunks = RREC_SFULL_CHUNKS;
		b.vbus = true;
		rt_fresh(&b);
		rt_vbus(false);
		break;
	case 42:
		b.vbus = true;
		b.mv = 3250;
		rt_fresh(&b);
		rt_vbus(false);
		break;
	case 43:
		b.vbus = true;
		b.mv = 3400;
		rt_fresh(&b);
		rt_vbus(false);
		break;
	case 44:
		rt_fresh(NULL);
		rt_vbus(true);
		rhw_sim_pmic_charge_error(1, 2);
		rt_sleep(50);
		rt_settle();
		break;
	case 45:
		rt_fresh(NULL);
		rt_vbus(true);
		rt_long();
		break;
	case 46:
		rt_fresh(NULL);
		to_transfer();
		rhw_sim_usb_event(RHW_USB_UNCONFIGURED);
		rt_sleep(50);
		rt_settle();
		break;
	case 47:
		rt_fresh(NULL);
		to_transfer();
		rt_vbus(false);
		break;
	case 48:
		rt_fresh(NULL);
		to_transfer();
		fw_end_sequence();
		break;
	case 50:
		rt_fresh(NULL);
		to_transfer();
		rt_long();
		break;
	case 51:
		b.chunks = RREC_SFULL_CHUNKS;
		rt_fresh(&b);
		rt_vbus(true);
		break;
	case 52:
		b.chunks = RREC_SFULL_CHUNKS;
		rt_fresh(&b);
		rt_long();
		break;
	case 53:
		b.chunks = RREC_SFULL_CHUNKS;
		b.mv = 3900;
		b.mv_next = 3400;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 54:
		b.chunks = RREC_SFULL_CHUNKS;
		b.mv = 3900;
		b.mv_next = 3250;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 55:
		b.mv = 3400;
		rt_fresh(&b);
		rt_vbus(true);
		break;
	case 56:
		b.mv = 3400;
		rt_fresh(&b);
		rt_long();
		break;
	case 57:
		b.mv = 3400;
		b.mv_next = 3250;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 58:
		b.init_fail = 1000;
		rt_fresh(&b);
		rt_vbus(true);
		break;
	case 59:
	case 62:
		b.init_fail = 1000;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 60:
		open_flag_card();
		b.init_fail = RREC_INIT_TRIES;
		rt_reboot(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 61:
		b.init_fail = RREC_INIT_TRIES;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 63:
		b.init_fail = 1000;
		b.mv = 3900;
		b.mv_next = 3250;
		rt_fresh(&b);
		rt_sleep(61000);
		rt_settle();
		break;
	case 64:
		mic_fault();
		rt_sleep(5500);
		rt_settle();
		break;
	case 65:
		mic_fault();
		rt_vbus(true);
		break;
	case 66:  /* B2 inside the 5 s of ERR_MIC_FAULT: the level as the power part reports it (rglue_battery) */
		mic_fault();
		rglue_battery(RC_BATT_B2);
		rt_settle();
		break;
	case 67:
		to_charger_error();
		rt_vbus(false);
		break;
	case 68:
		to_charger_error();
		rt_sleep(61000);   /* the 60 s sample reads 3,250 mV: B2 with VBUS: ship mode waits for VBUS removal */
		break;
#if defined(CONFIG_RING_FACTORY)
	case 49:
		to_factory();
		break;
	case 69:
		to_factory();
		factory_cmd(RREC_FAC_EXIT);
		break;
	case 70:
		to_factory();
		factory_cmd(RREC_FAC_SHIP_ENTER);
		rt_sleep(500);
		break;
	case 71:
		to_factory();
		factory_cmd(RREC_FAC_SHIP_SAMPLE);
		rt_sleep(500);
		break;
	case 72:
		to_factory();
		rt_vbus(false);
		break;
#endif
	default:
		return -ENOTSUP;
	}
	return 0;
}

void rt_row_cleanup(int row)
{
	if (row == 68 || row == 70 || row == 71) {
		rhw_sim_vbus(false);   /* ship mode waits for VBUS removal (FW l.939) */
		rt_sleep(3000);
		rt_settle();
	}
}
