/* Ring control: pure logic (report map, report builder, core link). */

#include <string.h>

#include <ring_core/rc_types.h>
#include <ring_control/rctl_report.h>

/*
 * HID report map: one keyboard, one consumer control, one pointer.
 * Report ID 1, keyboard input, 8 bytes: modifier bits, reserved, six key codes.
 * Report ID 2, consumer control input, 2 bytes: one 16-bit usage (0..0x3FF), 0 = none.
 * Report ID 3, pointer input, 3 bytes: button 1, dx, dy (relative, -127..127).
 * No output report (no keyboard LEDs) and no boot protocol: the three
 * reports are one device that a boot keyboard or boot mouse could not be.
 */
const uint8_t rctl_report_map[] = {
	/* keyboard */
	0x05, 0x01,       /* Usage Page (Generic Desktop) */
	0x09, 0x06,       /* Usage (Keyboard) */
	0xA1, 0x01,       /* Collection (Application) */
	0x85, RCTL_RID_KEYBOARD,
	0x05, 0x07,       /*   Usage Page (Keyboard) */
	0x19, 0xE0,       /*   Usage Minimum (Left Control) */
	0x29, 0xE7,       /*   Usage Maximum (Right GUI) */
	0x15, 0x00,       /*   Logical Minimum (0) */
	0x25, 0x01,       /*   Logical Maximum (1) */
	0x75, 0x01,       /*   Report Size (1) */
	0x95, 0x08,       /*   Report Count (8) */
	0x81, 0x02,       /*   Input (Data, Variable, Absolute): modifier bits */
	0x95, 0x01,       /*   Report Count (1) */
	0x75, 0x08,       /*   Report Size (8) */
	0x81, 0x01,       /*   Input (Constant): reserved byte */
	0x95, 0x06,       /*   Report Count (6) */
	0x75, 0x08,       /*   Report Size (8) */
	0x15, 0x00,       /*   Logical Minimum (0) */
	0x25, 0x65,       /*   Logical Maximum (101) */
	0x05, 0x07,       /*   Usage Page (Keyboard) */
	0x19, 0x00,       /*   Usage Minimum (0) */
	0x29, 0x65,       /*   Usage Maximum (101) */
	0x81, 0x00,       /*   Input (Data, Array): six key codes */
	0xC0,             /* End Collection */
	/* consumer control */
	0x05, 0x0C,       /* Usage Page (Consumer) */
	0x09, 0x01,       /* Usage (Consumer Control) */
	0xA1, 0x01,       /* Collection (Application) */
	0x85, RCTL_RID_CONSUMER,
	0x15, 0x00,       /*   Logical Minimum (0) */
	0x26, 0xFF, 0x03, /*   Logical Maximum (0x3FF) */
	0x19, 0x00,       /*   Usage Minimum (0) */
	0x2A, 0xFF, 0x03, /*   Usage Maximum (0x3FF) */
	0x75, 0x10,       /*   Report Size (16) */
	0x95, 0x01,       /*   Report Count (1) */
	0x81, 0x00,       /*   Input (Data, Array): one usage */
	0xC0,             /* End Collection */
	/* pointer */
	0x05, 0x01,       /* Usage Page (Generic Desktop) */
	0x09, 0x02,       /* Usage (Mouse) */
	0xA1, 0x01,       /* Collection (Application) */
	0x85, RCTL_RID_POINTER,
	0x09, 0x01,       /*   Usage (Pointer) */
	0xA1, 0x00,       /*   Collection (Physical) */
	0x05, 0x09,       /*     Usage Page (Button) */
	0x19, 0x01,       /*     Usage Minimum (Button 1) */
	0x29, 0x01,       /*     Usage Maximum (Button 1) */
	0x15, 0x00,       /*     Logical Minimum (0) */
	0x25, 0x01,       /*     Logical Maximum (1) */
	0x75, 0x01,       /*     Report Size (1) */
	0x95, 0x01,       /*     Report Count (1) */
	0x81, 0x02,       /*     Input (Data, Variable, Absolute): button 1 */
	0x75, 0x07,       /*     Report Size (7) */
	0x95, 0x01,       /*     Report Count (1) */
	0x81, 0x01,       /*     Input (Constant): padding */
	0x05, 0x01,       /*     Usage Page (Generic Desktop) */
	0x09, 0x30,       /*     Usage (X) */
	0x09, 0x31,       /*     Usage (Y) */
	0x15, 0x81,       /*     Logical Minimum (-127) */
	0x25, 0x7F,       /*     Logical Maximum (127) */
	0x75, 0x08,       /*     Report Size (8) */
	0x95, 0x02,       /*     Report Count (2) */
	0x81, 0x06,       /*     Input (Data, Variable, Relative): dx, dy */
	0xC0,             /*   End Collection (Physical) */
	0xC0,             /* End Collection (Application) */
};

const size_t rctl_report_map_len = sizeof(rctl_report_map);

const struct rctl_entry *rctl_lookup(enum rctl_mode mode, enum rctl_action action,
				     const struct rctl_options *opt)
{
	if ((unsigned int)mode >= RCTL_MODE_COUNT || (unsigned int)action >= RCTL_ACTION_COUNT) {
		return NULL;
	}
	if (mode == RCTL_PRESENTER && opt != NULL && opt->presenter_pages) {
		return &rctl_presenter_pages[action];
	}
	return &rctl_map[mode][action];
}

static void put(struct rctl_report *r, uint8_t index, uint8_t id, uint8_t len)
{
	memset(r, 0, sizeof(*r));
	r->index = index;
	r->id = id;
	r->len = len;
}

size_t rctl_build(enum rctl_mode mode, enum rctl_action action,
		  const struct rctl_options *opt, struct rctl_report out[RCTL_MAX_REPORTS])
{
	const struct rctl_entry *e = rctl_lookup(mode, action, opt);

	if (e == NULL) {
		return 0;
	}
	switch (e->kind) {
	case RCTL_SEND_KEY:
		put(&out[0], RCTL_IDX_KEYBOARD, RCTL_RID_KEYBOARD, RCTL_LEN_KEYBOARD);
		out[0].data[2] = (uint8_t)e->usage;
		put(&out[1], RCTL_IDX_KEYBOARD, RCTL_RID_KEYBOARD, RCTL_LEN_KEYBOARD);
		return 2;
	case RCTL_SEND_CONSUMER:
		put(&out[0], RCTL_IDX_CONSUMER, RCTL_RID_CONSUMER, RCTL_LEN_CONSUMER);
		out[0].data[0] = (uint8_t)(e->usage & 0xFF);
		out[0].data[1] = (uint8_t)(e->usage >> 8);
		put(&out[1], RCTL_IDX_CONSUMER, RCTL_RID_CONSUMER, RCTL_LEN_CONSUMER);
		return 2;
	case RCTL_SEND_MOVE:
		put(&out[0], RCTL_IDX_POINTER, RCTL_RID_POINTER, RCTL_LEN_POINTER);
		out[0].data[1] = (uint8_t)e->dx;
		out[0].data[2] = (uint8_t)e->dy;
		return 1;
	case RCTL_SEND_CLICK:
		put(&out[0], RCTL_IDX_POINTER, RCTL_RID_POINTER, RCTL_LEN_POINTER);
		out[0].data[0] = 0x01;
		put(&out[1], RCTL_IDX_POINTER, RCTL_RID_POINTER, RCTL_LEN_POINTER);
		return 2;
	default:
		return 0;
	}
}

bool rctl_from_core(uint8_t rc_action, enum rctl_action *out)
{
	switch (rc_action) {
	case RC_ACT_OPEN:
	case RC_ACT_SCREEN_CENTRE:
		*out = RCTL_CENTRE;
		return true;
	case RC_ACT_SCREEN_UP:
		*out = RCTL_UP;
		return true;
	case RC_ACT_SCREEN_DOWN:
		*out = RCTL_DOWN;
		return true;
	case RC_ACT_SCREEN_LEFT:
		*out = RCTL_LEFT;
		return true;
	case RC_ACT_SCREEN_RIGHT:
		*out = RCTL_RIGHT;
		return true;
	default:
		return false;
	}
}

bool rctl_core_filter(bool control_active, uint8_t rc_action, enum rctl_action *out)
{
	if (!control_active) {
		return false;
	}
	return rctl_from_core(rc_action, out);
}

void rctl_wait_start(struct rctl_wait *w, int n)
{
	w->npend = n;
	w->tries = 0;
}

bool rctl_wait_admit(const struct rctl_wait *w)
{
	return w->npend == 0;
}

void rctl_wait_released(struct rctl_wait *w, int n)
{
	w->npend -= n;
	if (w->npend <= 0) {
		w->npend = 0;
		w->tries = 0;
	}
}

enum rctl_retry rctl_wait_retry(struct rctl_wait *w)
{
	if (w->npend == 0) {
		return RCTL_RETRY_DONE;
	}
	if (++w->tries >= RCTL_RETRY_MAX) {
		w->npend = 0;
		w->tries = 0;
		return RCTL_RETRY_GIVE_UP;
	}
	return RCTL_RETRY_AGAIN;
}

enum rctl_mode rctl_mode_next(enum rctl_mode mode)
{
	return (enum rctl_mode)(((unsigned int)mode + 1) % RCTL_MODE_COUNT);
}

const char *rctl_mode_name(enum rctl_mode mode)
{
	static const char *const n[RCTL_MODE_COUNT] = { "media", "presenter", "pointer", "agent" };

	return (unsigned int)mode < RCTL_MODE_COUNT ? n[mode] : "?";
}

const char *rctl_action_name(enum rctl_action action)
{
	static const char *const n[RCTL_ACTION_COUNT] = { "centre", "up", "down", "left", "right" };

	return (unsigned int)action < RCTL_ACTION_COUNT ? n[action] : "?";
}
