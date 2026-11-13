/*
 * Ring screens, drawing part. LVGL draws in a 240 x 120 frame; the flush function turns every area a quarter turn
 * for the 120 x 240 panel and hands it to the display driver (Zephyr display API).
 * Look: the screens the owner accepted in the film (video/screens/screens-notes.md): white text on black, grey for the
 * second line, red for the recording dot, green for charging, amber for warnings, content inside an 18 px margin,
 * no status bar. Fonts: the kit's Montserrat 14, 16, 28 and 32 (built in; no font file is added).
 */

#include <errno.h>
#include <stdio.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/drivers/display.h>
#include <zephyr/kernel.h>
#include <lvgl.h>

#include <ring_screens/rscr.h>

#define MARGIN 18

#define C_WHITE  lv_color_make(240, 240, 238)
#define C_GREY   lv_color_make(140, 140, 138)
#define C_DIM    lv_color_make(80, 80, 78)
#define C_RED    lv_color_make(255, 59, 48)
#define C_GREEN  lv_color_make(48, 209, 88)
#define C_AMBER  lv_color_make(255, 176, 0)
#define C_PILL   lv_color_make(38, 38, 36)
#define C_PILL_ON lv_color_make(236, 230, 218)
#define C_BLACK  lv_color_black()

#define F14 (&lv_font_montserrat_14)
#define F16 (&lv_font_montserrat_16)
#define F28 (&lv_font_montserrat_28)
#define F32 (&lv_font_montserrat_32)

static const struct device *disp_dev;
static lv_display_t *disp;
static int flush_err;
static uint8_t vdb[RSCR_W * 24 * 2] __aligned(64);
static uint16_t rot[RSCR_W * 24];

static void flush_cb(lv_display_t *d, const lv_area_t *area, uint8_t *px_map)
{
	const uint16_t *src = (const uint16_t *)px_map;
	int w = lv_area_get_width(area);
	int h = lv_area_get_height(area);
	int px, py;
	struct display_buffer_descriptor desc;

	/* one quarter turn: panel column c of row r holds frame pixel (x1 + r, y2 - c) */
	for (int y = 0; y < h; y++) {
		for (int x = 0; x < w; x++) {
			rot[x * h + (h - 1 - y)] = src[y * w + x];
		}
	}
	rscr_to_panel(area->x1, area->y2, &px, &py);   /* top-left of the turned area: x from y2, y from x1 */
	desc.buf_size = (size_t)w * h * 2;
	desc.width = (uint16_t)h;
	desc.height = (uint16_t)w;
	desc.pitch = (uint16_t)h;
	desc.frame_incomplete = !lv_display_flush_is_last(d);
	if (display_write(disp_dev, (uint16_t)px, (uint16_t)py, &desc, rot) != 0) {
		flush_err++;
	}
	lv_display_flush_ready(d);
}

int rscr_draw_init(void)
{
	disp_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_display));
	if (!device_is_ready(disp_dev)) {
		return -ENODEV;
	}
	lv_init();
	lv_tick_set_cb(k_uptime_get_32);
	disp = lv_display_create(RSCR_W, RSCR_H);
	if (disp == NULL) {
		return -ENOMEM;
	}
	lv_display_set_color_format(disp, LV_COLOR_FORMAT_RGB565);
	lv_display_set_buffers(disp, vdb, NULL, sizeof(vdb), LV_DISPLAY_RENDER_MODE_PARTIAL);
	lv_display_set_flush_cb(disp, flush_cb);
	return 0;
}

int rscr_panel(bool on, uint8_t brightness)
{
	int rc = 0;

	if (on) {
		rc = display_blanking_off(disp_dev);
		(void)display_set_brightness(disp_dev, brightness);
	} else {
		rc = display_blanking_on(disp_dev);
	}
	return rc;
}

/* ---- small widgets ---- */

static lv_obj_t *scr_root(void)
{
	lv_obj_t *r = lv_screen_active();

	lv_obj_clean(r);
	lv_obj_set_style_bg_color(r, C_BLACK, 0);
	lv_obj_set_style_bg_opa(r, LV_OPA_COVER, 0);
	lv_obj_remove_flag(r, LV_OBJ_FLAG_SCROLLABLE);
	return r;
}

static lv_obj_t *text(lv_obj_t *p, const char *t, const lv_font_t *f, lv_color_t c, int x, int y)
{
	lv_obj_t *l = lv_label_create(p);

	lv_label_set_text(l, t);
	lv_obj_set_style_text_font(l, f, 0);
	lv_obj_set_style_text_color(l, c, 0);
	lv_obj_set_pos(l, x, y);
	return l;
}

/* a label with a fixed width: long text is cut with dots, or wrapped when wrap is set */
static lv_obj_t *text_w(lv_obj_t *p, const char *t, const lv_font_t *f, lv_color_t c, int x, int y, int w, bool wrap,
			lv_text_align_t al)
{
	lv_obj_t *l = text(p, t, f, c, x, y);

	lv_label_set_long_mode(l, wrap ? LV_LABEL_LONG_MODE_WRAP : LV_LABEL_LONG_MODE_DOTS);
	lv_obj_set_width(l, w);
	if (!wrap) {
		lv_obj_set_height(l, lv_font_get_line_height(f));   /* one line: a long text is cut with dots */
	}
	lv_obj_set_style_text_align(l, al, 0);
	return l;
}

static lv_obj_t *box(lv_obj_t *p, int x, int y, int w, int h, int radius, lv_color_t c)
{
	lv_obj_t *o = lv_obj_create(p);

	lv_obj_remove_flag(o, LV_OBJ_FLAG_SCROLLABLE);
	lv_obj_set_pos(o, x, y);
	lv_obj_set_size(o, w, h);
	lv_obj_set_style_radius(o, radius, 0);
	lv_obj_set_style_bg_color(o, c, 0);
	lv_obj_set_style_bg_opa(o, LV_OPA_COVER, 0);
	lv_obj_set_style_border_width(o, 0, 0);
	lv_obj_set_style_pad_all(o, 0, 0);
	return o;
}

static void ring_outline(lv_obj_t *o, lv_color_t c)
{
	lv_obj_set_style_border_width(o, 2, 0);
	lv_obj_set_style_border_color(o, c, 0);
}

static void red_dot(lv_obj_t *p, int x, int y, bool dim)
{
	/* the recording sign: a red dot of radius 4.5 with a dark red halo (the accepted design) */
	if (!dim) {
		box(p, x - 3, y - 3, 15, 15, LV_RADIUS_CIRCLE, lv_color_make(90, 20, 18));
	}
	box(p, x, y, 9, 9, LV_RADIUS_CIRCLE, C_RED);
}

static void hms(char *o, size_t n, uint32_t s)
{
	snprintf(o, n, "%02u:%02u:%02u", (unsigned)(s / 3600), (unsigned)((s / 60) % 60), (unsigned)(s % 60));
}

/* waveform: a few strands that swell off centre, drawn as polylines (a simple drawn line set: there is no live
 * microphone level yet, so the shape moves with the elapsed seconds only) */
static void waveform(lv_obj_t *p, uint32_t phase)
{
	static lv_point_precise_t pts[5][57];
	const int x0 = MARGIN, x1 = RSCR_W - MARGIN, cy = 36, amp = 17;

	for (int k = 0; k < 5; k++) {
		for (int i = 0; i < 57; i++) {
			int x = x0 + (x1 - x0) * i / 56;
			/* envelope: a swell that tapers to a needle at both ends */
			int t = i * 180 / 56;
			int env = lv_trigo_sin((int16_t)t) / 32;              /* 0..1023 */
			int w = lv_trigo_sin((int16_t)((i * (25 + 10 * k) + (int)phase * (40 + 13 * k)) % 360));
			int y = cy - (int)((int64_t)w * env * amp * (5 - k) / (32768LL * 1024 * 5));

			pts[k][i].x = x;
			pts[k][i].y = y;
		}
		lv_obj_t *ln = lv_line_create(p);

		lv_line_set_points(ln, pts[k], 57);
		lv_obj_set_style_line_width(ln, 1, 0);
		lv_obj_set_style_line_color(ln, k < 2 ? lv_color_make(235, 205, 160) : lv_color_make(190, 140, 100), 0);
	}
}

/* ---- screens ---- */

static void time_text(const struct rscr_frame *f, char *o, size_t n)
{
	if (!f->time_set) {
		snprintf(o, n, "--:--");
	} else if (f->s.fmt12) {
		unsigned h = f->hh % 12 == 0 ? 12 : f->hh % 12;

		snprintf(o, n, "%u:%02u", h, f->mm);
	} else {
		snprintf(o, n, "%02u:%02u", f->hh, f->mm);
	}
}

static void draw_status(lv_obj_t *r, const struct rscr_frame *f)
{
	char b[16];

	time_text(f, b, sizeof(b));
	text(r, b, F32, C_WHITE, MARGIN, 12);
	text(r, f->s.fmt12 ? (f->hh >= 12 ? "PM  Ready" : "AM  Ready") : "Ready", F16, C_GREY, MARGIN, 56);
}

static void draw_recording(lv_obj_t *r, const struct rscr_frame *f, bool dim)
{
	char b[16];

	hms(b, sizeof(b), f->elapsed_s);
	if (dim) {
		red_dot(r, MARGIN, 88, true);
		text_w(r, b, F16, C_DIM, RSCR_W - MARGIN - 100, 82, 100, false, LV_TEXT_ALIGN_RIGHT);
		return;
	}
	waveform(r, f->elapsed_s);
	red_dot(r, MARGIN, 88, false);
	text(r, "Recording", F16, C_WHITE, MARGIN + 20, 82);
	text_w(r, b, F16, C_GREY, RSCR_W - MARGIN - 100, 82, 100, false, LV_TEXT_ALIGN_RIGHT);
	if (f->s.session || f->s.highlights > 0) {
		char x[48];
		int n = 0;

		if (f->s.session) {
			n = snprintf(x, sizeof(x), "%s", f->s.mode == RCTL_MEDIA ? "Media" : f->s.mode == RCTL_PRESENTER ? "Presenter"
								  : f->s.mode == RCTL_POINTER ? "Pointer" : "Agent");
		}
		if (f->s.highlights > 0) {
			snprintf(x + n, sizeof(x) - n, "%s%u marked", n ? "  " : "", (unsigned)f->s.highlights);
		}
		text_w(r, x, F14, C_GREY, MARGIN, 62, RSCR_W - 2 * MARGIN, false, LV_TEXT_ALIGN_RIGHT);
	}
}

/* a list of up to three visible rows with the selected one on a light pill */
static void draw_list(lv_obj_t *r, const char *const *items, const char *const *vals, uint8_t n, uint8_t sel,
		      const char *title)
{
	int top = 0, y0 = title != NULL ? 30 : 14;
	int vis = title != NULL ? 3 : 3;

	if (title != NULL) {
		text(r, title, F14, C_GREY, MARGIN, 10);
	}
	if (sel > 0) {
		top = sel - 1;
	}
	if (top + vis > n) {
		top = n > vis ? n - vis : 0;
	}
	for (int i = 0; i < vis && top + i < n; i++) {
		int y = y0 + i * (title != NULL ? 25 : 30);
		bool on = top + i == sel;
		int h = title != NULL ? 23 : 27;

		if (on) {
			box(r, MARGIN - 6, y, RSCR_W - 2 * MARGIN + 12, h, 12, C_PILL_ON);
		}
		text_w(r, items[top + i], F16, on ? C_BLACK : C_WHITE, MARGIN + 4, y + (h - 18) / 2 + 1,
		       vals != NULL ? 130 : RSCR_W - 2 * MARGIN - 8, false, LV_TEXT_ALIGN_LEFT);
		if (vals != NULL) {
			text_w(r, vals[top + i], F16, on ? C_DIM : C_GREY, 150, y + (h - 18) / 2 + 1, 66, false,
			       LV_TEXT_ALIGN_RIGHT);
		}
	}
}

static const char *mode_name(unsigned m)
{
	static const char *const n[] = { "Media", "Presenter", "Pointer", "Agent" };

	return m < 4 ? n[m] : "?";
}

static void dev_label(const struct rscr_frame *f, uint8_t slot, char *o, size_t n)
{
	if (slot < RDEV_SLOTS && f->dev_name[slot][0] != '\0') {
		snprintf(o, n, "%s", f->dev_name[slot]);
	} else {
		snprintf(o, n, "Device %u", (unsigned)slot + 1);
	}
}

static void draw_control(lv_obj_t *r, const struct rscr_frame *f)
{
	char dn[20];
	unsigned m = f->s.mode;

	text(r, mode_name(m), F16, C_WHITE, MARGIN, 10);
	if (f->v.active_slot != RDEV_NONE) {
		dev_label(f, f->v.active_slot, dn, sizeof(dn));
		text_w(r, dn, F14, C_GREY, 120, 12, RSCR_W - MARGIN - 120, false, LV_TEXT_ALIGN_RIGHT);
	}
	if (!f->v.link_up) {
		text(r, "Not connected", F14, C_AMBER, MARGIN, 34);
	}
	switch (m) {
	case RCTL_MEDIA: {
		bool playing = f->media.state == RIPL_PLAYER_PLAYING;
		if (f->v.link_up || f->media.title[0] != '\0') {
			text_w(r, f->media.title[0] != '\0' ? f->media.title : "No track", F16, C_WHITE, MARGIN, 34,
			       RSCR_W - 2 * MARGIN, false, LV_TEXT_ALIGN_LEFT);
		}
		text(r, LV_SYMBOL_PREV, F16, C_GREY, 130, 66);
		box(r, 160, 60, 28, 28, LV_RADIUS_CIRCLE, C_PILL_ON);
		text(r, playing ? LV_SYMBOL_PAUSE : LV_SYMBOL_PLAY, F16, C_BLACK, 168, 66);
		text(r, LV_SYMBOL_NEXT, F16, C_GREY, 200, 66);
		break;
	}
	case RCTL_PRESENTER:
		text(r, "Slides", F16, C_WHITE, MARGIN, 34);
		text(r, LV_SYMBOL_LEFT, F16, C_GREY, 130, 66);
		box(r, 160, 60, 28, 28, LV_RADIUS_CIRCLE, C_PILL_ON);
		text(r, LV_SYMBOL_RIGHT, F16, C_BLACK, 168, 66);
		break;
	case RCTL_POINTER:
		text(r, "Move and click", F16, C_WHITE, MARGIN, 34);
		text(r, LV_SYMBOL_LEFT "  " LV_SYMBOL_UP "  " LV_SYMBOL_DOWN "  " LV_SYMBOL_RIGHT, F16, C_GREY, 100, 66);
		break;
	default:
		text(r, "Answer a request", F16, C_WHITE, MARGIN, 34);
		text(r, "Decline", F16, C_RED, MARGIN, 66);
		text_w(r, "Accept", F16, C_GREEN, 130, 66, RSCR_W - MARGIN - 130, false, LV_TEXT_ALIGN_RIGHT);
		break;
	}
	text(r, "Press twice to leave", F14, C_DIM, MARGIN, 88);
}

static void draw_devices(lv_obj_t *r, const struct rscr_frame *f)
{
	char nm[20];

	text(r, "Devices", F14, C_GREY, MARGIN, 14);
	if (f->v.paired_mask == 0) {
		text(r, "No device", F16, C_WHITE, MARGIN, 50);
		return;
	}
	int x = MARGIN - 4;

	for (uint8_t i = 0; i < rscr_paired_count(f->v.paired_mask); i++) {
		uint8_t slot = rscr_paired_slot(f->v.paired_mask, i);
		bool act = slot == f->v.active_slot;
		lv_obj_t *p;

		dev_label(f, slot, nm, sizeof(nm));
		p = box(r, x, 50, 68, 28, 14, act ? C_PILL_ON : C_PILL);
		if (i == f->s.dev_sel) {
			ring_outline(p, C_WHITE);
		}
		text_w(r, nm, F14, act ? C_BLACK : C_WHITE, x + 3, 56, 62, false, LV_TEXT_ALIGN_CENTER);
		x += 72;
	}
}

static void draw_device(lv_obj_t *r, const struct rscr_frame *f)
{
	char nm[20];
	const char *items[2] = { "Use", "Remove" };

	dev_label(f, f->s.dev_slot, nm, sizeof(nm));
	text_w(r, nm, F16, C_WHITE, MARGIN, 10, RSCR_W - 2 * MARGIN, false, LV_TEXT_ALIGN_LEFT);
	for (int i = 0; i < 2; i++) {
		bool on = i == f->s.dev_item;

		if (on) {
			box(r, MARGIN - 6, 40 + i * 30, RSCR_W - 2 * MARGIN + 12, 27, 12, C_PILL_ON);
		}
		text(r, items[i], F16, on ? C_BLACK : C_WHITE, MARGIN + 4, 44 + i * 30);
	}
}

static void draw_confirm(lv_obj_t *r, const struct rscr_frame *f)
{
	char q[40];

	if (f->s.confirm_kind == CONFIRM_REMOVE) {
		char nm[20];

		dev_label(f, f->s.confirm_slot, nm, sizeof(nm));
		snprintf(q, sizeof(q), "Remove %s?", nm);
	} else {
		snprintf(q, sizeof(q), "Power off?");
	}
	text_w(r, q, F16, C_WHITE, MARGIN, 12, RSCR_W - 2 * MARGIN, false, LV_TEXT_ALIGN_LEFT);
	text(r, "Yes: short press centre", F14, C_GREEN, MARGIN, 56);
	text(r, "No: left", F14, C_GREY, MARGIN, 80);
}

static void draw_pair(lv_obj_t *r, const struct rscr_frame *f, rc_ms_t now)
{
	char b[24];

	text(r, "Pair", F14, C_GREY, MARGIN, 12);
	if (f->s.pair_has_key) {
		snprintf(b, sizeof(b), "%03u %03u", (unsigned)(f->s.passkey / 1000), (unsigned)(f->s.passkey % 1000));
	} else {
		snprintf(b, sizeof(b), "--- ---");
	}
	text(r, b, F32, C_WHITE, MARGIN, 36);
	if (f->s.pair_until != RC_NO_TICK) {
		int64_t left = (f->s.pair_until - now + 999) / 1000;

		snprintf(b, sizeof(b), "%d s", (int)(left < 0 ? 0 : left));
		text_w(r, b, F14, C_GREY, MARGIN, 88, RSCR_W - 2 * MARGIN, false, LV_TEXT_ALIGN_RIGHT);
	}
}

static void draw_message(lv_obj_t *r, const struct rscr_frame *f)
{
	bool warn = f->s.msg == MSG_BATTERY_LOW || f->s.msg == MSG_STORAGE_FULL || f->s.msg == MSG_30_MIN;

	text_w(r, rscr_msg_text((enum rscr_msg)f->s.msg), F16, warn ? C_AMBER : C_WHITE, MARGIN, 30,
	       RSCR_W - 2 * MARGIN, true, LV_TEXT_ALIGN_LEFT);
	if (f->v.core_state == RC_ST_RECORDING) {
		char b[16];

		hms(b, sizeof(b), f->elapsed_s);
		red_dot(r, MARGIN, 88, false);
		text_w(r, b, F16, C_GREY, RSCR_W - MARGIN - 100, 82, 100, false, LV_TEXT_ALIGN_RIGHT);
	}
}

static void draw_charging(lv_obj_t *r, const struct rscr_frame *f)
{
	char b[24];

	snprintf(b, sizeof(b), "%u%%", f->batt_pct);
	text(r, b, F28, C_WHITE, MARGIN, 10);
	text(r, f->full ? "Full" : "Charging", F16, C_GREY, MARGIN, 50);
	box(r, MARGIN, 88, 24, 12, 3, C_GREEN);
	box(r, MARGIN + 24, 91, 3, 6, 1, C_GREEN);
	if (!f->full && f->to_full_min > 0) {
		snprintf(b, sizeof(b), "%u min", f->to_full_min);
		text(r, b, F14, C_GREY, MARGIN + 36, 86);
	}
}

static void draw_notifs(lv_obj_t *r, const struct rscr_frame *f)
{
	if (f->v.inbox_n == 0) {
		text(r, "Notifications", F14, C_GREY, MARGIN, 14);
		text(r, "None", F16, C_WHITE, MARGIN, 50);
		return;
	}
	char head[24];
	int top = f->s.notif_sel > 0 ? f->s.notif_sel - 1 : 0;

	if (top + 3 > f->v.inbox_n) {
		top = f->v.inbox_n > 3 ? f->v.inbox_n - 3 : 0;
	}
	snprintf(head, sizeof(head), "Notifications %u", f->v.inbox_n);
	text(r, head, F14, C_GREY, MARGIN, 10);
	for (int i = 0; i < 3 && top + i < f->v.inbox_n; i++) {
		const struct rinbox_item *it = &f->inbox[top + i];
		bool on = top + i == f->s.notif_sel;
		int y = 30 + i * 25;
		const char *t = it->title[0] != '\0' ? it->title : "Notification";   /* never the app identifier */

		if (on) {
			box(r, MARGIN - 6, y, RSCR_W - 2 * MARGIN + 12, 23, 11, C_PILL_ON);
		}
		if (!it->read) {
			box(r, MARGIN - 1, y + 9, 5, 5, LV_RADIUS_CIRCLE, C_GREEN);
		}
		text_w(r, t, F16, on ? C_BLACK : C_WHITE, MARGIN + 10, y + 3, RSCR_W - 2 * MARGIN - 14, false,
		       LV_TEXT_ALIGN_LEFT);
	}
}

static void draw_notif(lv_obj_t *r, const struct rscr_frame *f)
{
	const struct rinbox_item *it = NULL;

	for (uint8_t i = 0; i < f->v.inbox_n; i++) {
		if (f->inbox[i].uid == f->s.notif_uid) {
			it = &f->inbox[i];
		}
	}
	if (it == NULL) {
		text(r, "Gone", F16, C_GREY, MARGIN, 40);
		return;
	}
	box(r, MARGIN, 12, 18, 18, 5, C_GREEN);   /* a generic icon square (no app artwork is drawn) */
	text_w(r, it->title[0] != '\0' ? it->title : "Notification", F16, C_WHITE, MARGIN + 26, 11, RSCR_W - 2 * MARGIN - 26,
	       false, LV_TEXT_ALIGN_LEFT);
	text_w(r, it->msg, F14, C_GREY, MARGIN, 36, RSCR_W - 2 * MARGIN, true, LV_TEXT_ALIGN_LEFT);
	/* the two actions at the edges, as in the accepted design: dismiss left, the positive action right */
	if ((it->flags & RINBOX_F_NEGATIVE) != 0) {
		text(r, LV_SYMBOL_LEFT, F14, C_GREY, MARGIN, 82);
		box(r, MARGIN + 14, 78, 24, 24, LV_RADIUS_CIRCLE, C_PILL);
		text(r, LV_SYMBOL_CLOSE, F14, C_WHITE, MARGIN + 20, 82);
	}
	if ((it->flags & RINBOX_F_POSITIVE) != 0) {
		box(r, RSCR_W - MARGIN - 38, 78, 24, 24, LV_RADIUS_CIRCLE, C_PILL);
		text(r, LV_SYMBOL_OK, F14, C_WHITE, RSCR_W - MARGIN - 32, 82);
		text(r, LV_SYMBOL_RIGHT, F14, C_GREY, RSCR_W - MARGIN - 10, 82);
	}
}

static void draw_plain(lv_obj_t *r, const char *title, const char *line, lv_color_t lc)
{
	text(r, title, F16, C_WHITE, MARGIN, 24);
	if (line != NULL) {
		text_w(r, line, F14, lc, MARGIN, 56, RSCR_W - 2 * MARGIN, true, LV_TEXT_ALIGN_LEFT);
	}
}

/* The factory test T-SCREEN (design/firmware.md 9.3): a whole frame in one colour, or the grid. The colours are the pure
 * RGB values the jig's camera expects. */
static void draw_factory_frame(lv_obj_t *r, uint8_t frame)
{
	switch (frame) {
	case FAC_RED:
		lv_obj_set_style_bg_color(r, lv_color_make(255, 0, 0), 0);
		break;
	case FAC_GREEN:
		lv_obj_set_style_bg_color(r, lv_color_make(0, 255, 0), 0);
		break;
	case FAC_BLUE:
		lv_obj_set_style_bg_color(r, lv_color_make(0, 0, 255), 0);
		break;
	case FAC_WHITE:
		lv_obj_set_style_bg_color(r, lv_color_make(255, 255, 255), 0);
		break;
	case FAC_GRID:
		/* white lines, one pixel wide, every 20 pixels from 0, and the last column and the last row, on black */
		for (int x = 0; x < RSCR_W; x += 20) {
			box(r, x, 0, 1, RSCR_H, 0, lv_color_make(255, 255, 255));
		}
		box(r, RSCR_W - 1, 0, 1, RSCR_H, 0, lv_color_make(255, 255, 255));
		for (int y = 0; y < RSCR_H; y += 20) {
			box(r, 0, y, RSCR_W, 1, 0, lv_color_make(255, 255, 255));
		}
		box(r, 0, RSCR_H - 1, RSCR_W, 1, 0, lv_color_make(255, 255, 255));
		break;
	default:   /* FAC_BLACK: the root is black already */
		break;
	}
}

int rscr_draw(const struct rscr_frame *f)
{
	lv_obj_t *r = scr_root();
	rc_ms_t now = f->now;
	char b[48];
	const char *items[MENU_COUNT];
	const char *vals[SET_COUNT];
	const struct rscr *s = &f->s;

	flush_err = 0;
	switch (s->screen) {
	case SCR_STATUS:
		draw_status(r, f);
		break;
	case SCR_RECORDING:
		draw_recording(r, f, false);
		break;
	case SCR_REC_DIM:
		draw_recording(r, f, true);
		break;
	case SCR_MENU:
		for (int i = 0; i < MENU_COUNT; i++) {
			items[i] = rscr_menu_name((enum rscr_menu_item)i);
		}
		draw_list(r, items, NULL, rscr_menu_count((enum rc_state)f->v.core_state), s->menu_sel, NULL);
		break;
	case SCR_MODES:
		for (int i = 0; i < RCTL_MODE_COUNT; i++) {
			items[i] = mode_name((unsigned)i);
		}
		draw_list(r, items, NULL, RCTL_MODE_COUNT, s->mode_sel, "Control");
		break;
	case SCR_SETTINGS: {
		static char vb[3][12];

		items[0] = "Brightness";
		items[1] = "Vibration";
		items[2] = "Time format";
		items[3] = "About";
		snprintf(vb[0], sizeof(vb[0]), "%u of 3", s->brightness + 1);
		snprintf(vb[1], sizeof(vb[1]), "%s", s->vibration ? "On" : "Off");
		snprintf(vb[2], sizeof(vb[2]), "%s", s->fmt12 ? "12 h" : "24 h");
		vals[0] = vb[0];
		vals[1] = vb[1];
		vals[2] = vb[2];
		vals[3] = "0.1";
		draw_list(r, items, vals, SET_COUNT, s->set_sel, "Settings");
		break;
	}
	case SCR_CONTROL:
		draw_control(r, f);
		break;
	case SCR_DEVICES:
		draw_devices(r, f);
		break;
	case SCR_DEVICE:
		draw_device(r, f);
		break;
	case SCR_CONFIRM:
		draw_confirm(r, f);
		break;
	case SCR_PAIR:
		draw_pair(r, f, now);
		break;
	case SCR_MESSAGE:
		draw_message(r, f);
		break;
	case SCR_CHARGING:
		draw_charging(r, f);
		break;
	case SCR_NOTIFS:
		draw_notifs(r, f);
		break;
	case SCR_NOTIF:
		draw_notif(r, f);
		break;
	case SCR_TRANSFER:
		draw_plain(r, "Transfer", "In the case", C_GREY);
		break;
	case SCR_RECOVERY:
		draw_plain(r, "Recovering", NULL, C_GREY);
		break;
	case SCR_FACTORY:
		if (s->fac_frame == FAC_NONE) {
			draw_plain(r, "Factory test", NULL, C_GREY);
		} else {
			draw_factory_frame(r, s->fac_frame);
		}
		break;
	case SCR_ERROR:
		snprintf(b, sizeof(b), "Error %u", f->err_code);
		draw_plain(r, f->v.core_state == RC_ST_ERR_MIC_FAULT ? "Microphone fault"
			   : f->v.core_state == RC_ST_ERR_CHARGER   ? "Charger fault"
								    : "Storage fault",
			   f->v.core_state == RC_ST_ERR_MIC_FAULT ? b : "Put in case", C_AMBER);
		break;
	case SCR_RECORDINGS:
		draw_plain(r, "Recordings", f->v.rec_n == 0 ? "None" : NULL, C_GREY);
		break;
	case SCR_RECORDING_INFO:
		draw_plain(r, "Recording", NULL, C_GREY);
		break;
	default:
		break;
	}
	lv_refr_now(disp);
	return flush_err == 0 ? 0 : -EIO;
}

#if IS_ENABLED(CONFIG_RING_SCREENS_CAPTURE)
/* Test hook: draw one text alone, with the same helpers and fonts as the screens, on a flat background, so a test can compare
 * the region of a scene's frame with the same text drawn alone. align: 0 left, 1 centre, 2 right; w = 0 for a plain label. */
void rscr_ref_text(const char *txt, int font_px, uint32_t fg, uint32_t bg, int x, int y, int w, int align, bool wrap)
{
	const lv_font_t *fn = font_px == 14 ? F14 : font_px == 16 ? F16 : font_px == 28 ? F28 : F32;
	lv_obj_t *r;

	rscr_draw_lock();
	r = scr_root();
	lv_obj_set_style_bg_color(r, lv_color_hex(bg), 0);
	if (w == 0) {
		(void)text(r, txt, fn, lv_color_hex(fg), x, y);
	} else {
		(void)text_w(r, txt, fn, lv_color_hex(fg), x, y, w, wrap,
			     align == 2 ? LV_TEXT_ALIGN_RIGHT : align == 1 ? LV_TEXT_ALIGN_CENTER : LV_TEXT_ALIGN_LEFT);
	}
	lv_refr_now(disp);
	rscr_draw_unlock();
}

/* Test hook: the peak use of LVGL's memory pool so far, in bytes (0 when the pool does not report it) */
uint32_t rscr_draw_pool_peak(void)
{
	lv_mem_monitor_t mon;

	rscr_draw_lock();
	lv_mem_monitor(&mon);
	rscr_draw_unlock();
	return (uint32_t)mon.max_used;
}
#endif
