/*
 * ring_control logic tests (native_sim, no radio).
 * The expected values are written here as literals, apart from the tables in
 * rctl_modes.h, so a wrong key in the header fails a test.
 */

#include <string.h>

#include <zephyr/ztest.h>

#include <ring_core/rc_types.h>
#include <ring_control/rctl_report.h>

enum { N, K, C, M, B }; /* nothing, key, consumer, move, click(button) */

struct expect {
	uint8_t kind;
	uint16_t usage;
	int8_t dx, dy;
};

/* [mode][action]: centre, up, down, left, right */
static const struct expect want[RCTL_MODE_COUNT][RCTL_ACTION_COUNT] = {
	[RCTL_MEDIA] = {
		{ C, 0xCD, 0, 0 },   /* centre: play or pause */
		{ C, 0xE9, 0, 0 },   /* up: volume up */
		{ C, 0xEA, 0, 0 },   /* down: volume down */
		{ C, 0xB6, 0, 0 },   /* left: previous */
		{ C, 0xB5, 0, 0 },   /* right: next */
	},
	[RCTL_PRESENTER] = {
		{ N, 0, 0, 0 },
		{ K, 0x50, 0, 0 },   /* up: previous slide, Left Arrow */
		{ K, 0x4F, 0, 0 },   /* down: next slide, Right Arrow */
		{ K, 0x50, 0, 0 },   /* left: previous slide */
		{ K, 0x4F, 0, 0 },   /* right: next slide */
	},
	[RCTL_POINTER] = {
		{ B, 0, 0, 0 },      /* centre: click */
		{ M, 0, 0, -16 },
		{ M, 0, 0, 16 },
		{ M, 0, -16, 0 },
		{ M, 0, 16, 0 },
	},
	[RCTL_AGENT] = {
		{ K, 0x28, 0, 0 },   /* centre: Return */
		{ K, 0x52, 0, 0 },   /* up: Up Arrow */
		{ K, 0x51, 0, 0 },   /* down: Down Arrow */
		{ K, 0x29, 0, 0 },   /* left: Escape */
		{ K, 0x28, 0, 0 },   /* right: Return (accept) */
	},
};

static const struct expect want_pages[RCTL_ACTION_COUNT] = {
	{ N, 0, 0, 0 },
	{ K, 0x4B, 0, 0 },       /* Page Up */
	{ K, 0x4E, 0, 0 },       /* Page Down */
	{ K, 0x4B, 0, 0 },
	{ K, 0x4E, 0, 0 },
};

static void check_row(enum rctl_mode m, enum rctl_action a, const struct expect *e,
		      const struct rctl_options *opt)
{
	struct rctl_report r[RCTL_MAX_REPORTS];
	size_t n;
	uint8_t zero[8] = { 0 };

	memset(r, 0xEE, sizeof(r));
	n = rctl_build(m, a, opt, r);
	switch (e->kind) {
	case N:
		zassert_equal(n, 0, "%s %s: nothing to send, got %zu", rctl_mode_name(m), rctl_action_name(a), n);
		break;
	case K:
		zassert_equal(n, 2, "%s %s: press and release", rctl_mode_name(m), rctl_action_name(a));
		zassert_equal(r[0].id, RCTL_RID_KEYBOARD);
		zassert_equal(r[0].index, RCTL_IDX_KEYBOARD);
		zassert_equal(r[0].len, 8);
		zassert_equal(r[0].data[0], 0, "no modifier");
		zassert_equal(r[0].data[1], 0, "reserved");
		zassert_equal(r[0].data[2], e->usage, "%s %s: key 0x%02x got 0x%02x", rctl_mode_name(m),
			      rctl_action_name(a), e->usage, r[0].data[2]);
		zassert_mem_equal(&r[0].data[3], zero, 5, "one key only");
		zassert_equal(r[1].id, RCTL_RID_KEYBOARD);
		zassert_equal(r[1].len, 8);
		zassert_mem_equal(r[1].data, zero, 8, "release: all keys up");
		break;
	case C:
		zassert_equal(n, 2, "%s %s: press and release", rctl_mode_name(m), rctl_action_name(a));
		zassert_equal(r[0].id, RCTL_RID_CONSUMER);
		zassert_equal(r[0].index, RCTL_IDX_CONSUMER);
		zassert_equal(r[0].len, 2);
		zassert_equal(r[0].data[0], e->usage & 0xFF, "%s %s: usage 0x%04x", rctl_mode_name(m),
			      rctl_action_name(a), e->usage);
		zassert_equal(r[0].data[1], e->usage >> 8);
		zassert_equal(r[1].id, RCTL_RID_CONSUMER);
		zassert_equal(r[1].len, 2);
		zassert_mem_equal(r[1].data, zero, 2, "release: usage 0");
		break;
	case M:
		zassert_equal(n, 1, "%s %s: one move report", rctl_mode_name(m), rctl_action_name(a));
		zassert_equal(r[0].id, RCTL_RID_POINTER);
		zassert_equal(r[0].index, RCTL_IDX_POINTER);
		zassert_equal(r[0].len, 3);
		zassert_equal(r[0].data[0], 0, "no button");
		zassert_equal((int8_t)r[0].data[1], e->dx);
		zassert_equal((int8_t)r[0].data[2], e->dy);
		break;
	case B:
		zassert_equal(n, 2, "click: down and up");
		zassert_equal(r[0].id, RCTL_RID_POINTER);
		zassert_equal(r[0].index, RCTL_IDX_POINTER);
		zassert_equal(r[1].index, RCTL_IDX_POINTER);
		zassert_equal(r[0].len, 3);
		zassert_equal(r[0].data[0], 1, "button 1 down");
		zassert_equal(r[0].data[1], 0);
		zassert_equal(r[0].data[2], 0);
		zassert_equal(r[1].id, RCTL_RID_POINTER);
		zassert_mem_equal(r[1].data, zero, 3, "button up");
		break;
	}
}

ZTEST(ring_control, test_mode_tables)
{
	struct rctl_options arrows = { .presenter_pages = false };

	for (int m = 0; m < RCTL_MODE_COUNT; m++) {
		for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
			check_row(m, a, &want[m][a], &arrows);
			check_row(m, a, &want[m][a], NULL); /* no options: the defaults */
		}
	}
}

ZTEST(ring_control, test_presenter_page_keys_option)
{
	struct rctl_options pages = { .presenter_pages = true };

	for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
		check_row(RCTL_PRESENTER, a, &want_pages[a], &pages);
	}
	/* the option changes the presenter only */
	for (int m = 0; m < RCTL_MODE_COUNT; m++) {
		if (m == RCTL_PRESENTER) {
			continue;
		}
		for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
			check_row(m, a, &want[m][a], &pages);
		}
	}
}

/* Every report that presses is followed by its release; a move has no press. */
ZTEST(ring_control, test_press_then_release)
{
	for (int m = 0; m < RCTL_MODE_COUNT; m++) {
		for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
			struct rctl_report r[RCTL_MAX_REPORTS];
			size_t n = rctl_build(m, a, NULL, r);
			const struct rctl_entry *e = rctl_lookup(m, a, NULL);

			zassert_not_null(e);
			if (e->kind == RCTL_SEND_KEY || e->kind == RCTL_SEND_CONSUMER || e->kind == RCTL_SEND_CLICK) {
				bool all_zero = true;

				zassert_equal(n, 2);
				zassert_equal(r[0].index, r[1].index, "release on the same report");
				for (int i = 0; i < r[1].len; i++) {
					all_zero = all_zero && r[1].data[i] == 0;
				}
				zassert_true(all_zero, "second report is the release");
			}
		}
	}
}

/* Out-of-range input sends nothing. */
ZTEST(ring_control, test_out_of_range)
{
	struct rctl_report r[RCTL_MAX_REPORTS];

	zassert_is_null(rctl_lookup(RCTL_MODE_COUNT, RCTL_UP, NULL));
	zassert_is_null(rctl_lookup(RCTL_MEDIA, RCTL_ACTION_COUNT, NULL));
	zassert_equal(rctl_build(RCTL_MODE_COUNT, RCTL_UP, NULL, r), 0);
	zassert_equal(rctl_build(RCTL_MEDIA, RCTL_ACTION_COUNT, NULL, r), 0);
}

/* Only the five joystick actions of the screen shown give a key. The rest of the
 * core's actions (open, close, motors, rails, screen requests) never do, and no action of
 * the core's centre long press (OPEN, CLOSE) maps to anything. */
ZTEST(ring_control, test_only_joystick_actions_map)
{
	static const struct {
		uint8_t rc;
		enum rctl_action act;
	} yes[] = {
		{ RC_ACT_SCREEN_CENTRE, RCTL_CENTRE }, { RC_ACT_SCREEN_UP, RCTL_UP },
		{ RC_ACT_SCREEN_DOWN, RCTL_DOWN },     { RC_ACT_SCREEN_LEFT, RCTL_LEFT },
		{ RC_ACT_SCREEN_RIGHT, RCTL_RIGHT },
	};
	int mapped = 0;

	for (unsigned int rc = 0; rc < RC_ACT_COUNT + 8; rc++) {
		enum rctl_action act = RCTL_ACTION_COUNT;
		bool got = rctl_from_core((uint8_t)rc, &act);
		bool expected = false;

		for (size_t i = 0; i < ARRAY_SIZE(yes); i++) {
			if (yes[i].rc == rc) {
				expected = true;
				zassert_equal(act, yes[i].act, "action %u", rc);
			}
		}
		zassert_equal(got, expected, "core action %u (%s)", rc,
			      rc < RC_ACT_COUNT ? rc_action_name((enum rc_action)rc) : "out of range");
		mapped += got ? 1 : 0;
	}
	zassert_equal(mapped, 5);
	zassert_false(rctl_from_core(RC_ACT_OPEN, &(enum rctl_action){ 0 }), "OPEN is recording");
	zassert_false(rctl_from_core(RC_ACT_CLOSE, &(enum rctl_action){ 0 }), "CLOSE is recording");
	zassert_false(rctl_from_core(RC_ACT_SCREEN_ON, &(enum rctl_action){ 0 }),
		      "a wake of the screen is not a key (Apple's rule)");
}

/* The report map declares the three input reports with the sizes the builder uses. */
ZTEST(ring_control, test_report_map_matches_builder)
{
	uint32_t bits[8] = { 0 };
	uint32_t arr_lmax[8] = { 0 }, arr_umax[8] = { 0 }; /* array inputs: Logical and Usage Maximum */
	uint32_t lmax = 0, umax = 0;
	uint32_t size = 0, count = 0, rid = 0;
	int depth = 0, apps = 0;
	size_t i = 0;

	while (i < rctl_report_map_len) {
		uint8_t pre = rctl_report_map[i];
		unsigned int sz = pre & 3U, type = (pre >> 2) & 3U, tag = pre >> 4;
		uint32_t v = 0;

		if (sz == 3) {
			sz = 4;
		}
		zassert_true(i + 1 + sz <= rctl_report_map_len, "item runs past the end");
		for (unsigned int k = 0; k < sz; k++) {
			v |= (uint32_t)rctl_report_map[i + 1 + k] << (8 * k);
		}
		if (type == 1) { /* global */
			if (tag == 7) {
				size = v;
			} else if (tag == 9) {
				count = v;
			} else if (tag == 8) {
				rid = v;
			} else if (tag == 2) {
				lmax = v;
			}
		} else if (type == 2 && tag == 2) { /* local: Usage Maximum */
			umax = v;
		} else if (type == 0) { /* main */
			if (tag == 8) { /* Input */
				zassert_true(rid > 0 && rid < 8);
				bits[rid] += size * count;
				if ((v & 0x03) == 0) { /* Data, Array */
					arr_lmax[rid] = lmax;
					arr_umax[rid] = umax;
				}
			} else if (tag == 10) { /* Collection */
				depth++;
				if (depth == 1) {
					apps++;
				}
			} else if (tag == 12) { /* End Collection */
				depth--;
			}
		}
		i += 1 + sz;
	}
	zassert_equal(depth, 0, "collections balanced");
	zassert_equal(apps, 3, "keyboard, consumer control, pointer");
	zassert_equal(bits[RCTL_RID_KEYBOARD], RCTL_LEN_KEYBOARD * 8U);
	zassert_equal(bits[RCTL_RID_CONSUMER], RCTL_LEN_CONSUMER * 8U);
	zassert_equal(bits[RCTL_RID_POINTER], RCTL_LEN_POINTER * 8U);
	/* the arrays must cover every code the tables send, or a host rejects the report */
	{
		uint32_t top_key = 0, top_cons = 0;

		for (int m = 0; m <= RCTL_MODE_COUNT; m++) {
			for (int a = 0; a < RCTL_ACTION_COUNT; a++) {
				const struct rctl_entry *e = m < RCTL_MODE_COUNT ? &rctl_map[m][a] : &rctl_presenter_pages[a];

				if (e->kind == RCTL_SEND_KEY && e->usage > top_key) {
					top_key = e->usage;
				}
				if (e->kind == RCTL_SEND_CONSUMER && e->usage > top_cons) {
					top_cons = e->usage;
				}
			}
		}
		zassert_true(arr_lmax[RCTL_RID_KEYBOARD] >= top_key && arr_umax[RCTL_RID_KEYBOARD] >= top_key,
			     "keyboard maximum 0x%x/0x%x below key 0x%x", arr_lmax[RCTL_RID_KEYBOARD],
			     arr_umax[RCTL_RID_KEYBOARD], top_key);
		zassert_true(arr_lmax[RCTL_RID_CONSUMER] >= top_cons && arr_umax[RCTL_RID_CONSUMER] >= top_cons,
			     "consumer maximum below usage 0x%x", top_cons);
	}
	zassert_equal(bits[0] + bits[4] + bits[5] + bits[6] + bits[7], 0, "no other report");
}

/* The release wait, from the wearer's side: while a key's release waits to be sent, the next action
 * is refused; once the release is out, the next action passes; after RCTL_RETRY_MAX tries the wait
 * ends and the wearer is not blocked for ever (at most RCTL_RETRY_MAX x RCTL_RETRY_MS = 1 s). */
ZTEST(ring_control, test_release_wait_wearer_side)
{
	struct rctl_wait w = { 0 };

	zassert_true(rctl_wait_admit(&w), "no wait: an action passes");
	rctl_wait_start(&w, 1); /* a press went out, its release failed */
	zassert_false(rctl_wait_admit(&w), "an action during the wait is refused");
	zassert_equal(rctl_wait_retry(&w), RCTL_RETRY_AGAIN);
	zassert_false(rctl_wait_admit(&w), "still refused while the release waits");
	rctl_wait_released(&w, 1); /* the retry sent it */
	zassert_true(rctl_wait_admit(&w), "the next action after the release passes");
	zassert_equal(rctl_wait_retry(&w), RCTL_RETRY_DONE);

	/* the release never goes out: the wait ends after RCTL_RETRY_MAX tries */
	rctl_wait_start(&w, 1);
	for (int i = 1; i < RCTL_RETRY_MAX; i++) {
		zassert_equal(rctl_wait_retry(&w), RCTL_RETRY_AGAIN, "try %d", i);
		zassert_false(rctl_wait_admit(&w));
	}
	zassert_equal(rctl_wait_retry(&w), RCTL_RETRY_GIVE_UP);
	zassert_true(rctl_wait_admit(&w), "the wearer is not blocked for ever");
	zassert_true(RCTL_RETRY_MAX * RCTL_RETRY_MS <= 1000, "the wait is at most 1 s");
}

/* Control not active: no core action becomes a key, the five screen actions included. */
ZTEST(ring_control, test_gate_control_active)
{
	int mapped = 0;

	for (unsigned int rc = 0; rc < RC_ACT_COUNT + 8; rc++) {
		enum rctl_action act = RCTL_ACTION_COUNT;
		bool off = rctl_core_filter(false, (uint8_t)rc, &act);
		bool on = rctl_core_filter(true, (uint8_t)rc, &act);
		bool five = rc == RC_ACT_SCREEN_CENTRE || rc == RC_ACT_SCREEN_UP || rc == RC_ACT_SCREEN_DOWN ||
			    rc == RC_ACT_SCREEN_LEFT || rc == RC_ACT_SCREEN_RIGHT;

		zassert_false(off, "control not active: action %u must not type", rc);
		zassert_equal(on, five, "control active: action %u", rc);
		mapped += on ? 1 : 0;
	}
	zassert_equal(mapped, 5);
}

ZTEST(ring_control, test_mode_order_and_names)
{
	enum rctl_mode m = RCTL_MEDIA;

	zassert_equal(RCTL_MODE_COUNT, 4, "four modes");
	m = rctl_mode_next(m);
	zassert_equal(m, RCTL_PRESENTER);
	m = rctl_mode_next(m);
	zassert_equal(m, RCTL_POINTER);
	m = rctl_mode_next(m);
	zassert_equal(m, RCTL_AGENT);
	m = rctl_mode_next(m);
	zassert_equal(m, RCTL_MEDIA, "wraps");
	zassert_str_equal(rctl_mode_name(RCTL_AGENT), "agent");
	zassert_str_equal(rctl_action_name(RCTL_CENTRE), "centre");
}

ZTEST_SUITE(ring_control, NULL, NULL, NULL, NULL, NULL);
