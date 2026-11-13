/* Ring screens: the real other modules (ring_devices, ring_control, ring_iphone, ring_glue) behind struct rscr_ops. */

#include <zephyr/kernel.h>

#include <ring_control/rctl.h>
#include <ring_devices/rdev.h>
#include <ring_glue/rglue.h>
#include <ring_iphone/rip.h>
#include <ring_screens/rscr.h>

static uint8_t r_inbox_count(void)
{
	return rip_inbox_count();
}

static bool r_inbox_get(uint8_t i, struct rinbox_item *o)
{
	return rip_inbox_get(i, o);
}

static void r_media_get(struct ripl_media *o)
{
	rip_media_get(o);
}

static bool r_ams_ready(void)
{
	return rip_ams_ready();
}

static uint8_t r_paired_mask(void)
{
	return rdev_paired_mask();
}

static uint8_t r_active(void)
{
	return rdev_active();
}

static bool r_link_up(void)
{
	return rdev_link_up();
}

static int r_dismiss(uint32_t uid)
{
	return rip_dismiss(uid);
}

static int r_positive(uint32_t uid)
{
	return rip_action(uid, RIP_ACTION_POSITIVE);
}

static int r_mark_read(uint32_t uid)
{
	return rip_inbox_mark_read(uid);
}

static int r_pair_open(uint8_t slot)
{
	return rdev_pair_open(slot, RDEV_PAIR_WINDOW_MS);
}

static void r_pair_cancel(void)
{
	rdev_pair_cancel();
}

static int r_dev_use(uint8_t slot)
{
	return rdev_switch(slot);
}

static int r_dev_remove(uint8_t slot)
{
	return rdev_remove(slot);
}

static void r_control_active(bool a)
{
	rctl_set_active(a);
}

static void r_set_mode(enum rctl_mode m)
{
	rctl_set_mode(m);
}

static int r_power_off(void)
{
	/* never block the screens thread on the glue's lock: a core step that holds it may be waiting for rscr_sign_start */
	return rglue_event_try(RC_EV_MENU_POWER_OFF);
}

static void r_vibration(bool on)
{
	rglue_set_vibration(on);
}

const struct rscr_ops rscr_real_ops = {
	.inbox_count = r_inbox_count,
	.inbox_get = r_inbox_get,
	.media_get = r_media_get,
	.ams_ready = r_ams_ready,
	.paired_mask = r_paired_mask,
	.active = r_active,
	.link_up = r_link_up,
	.dismiss = r_dismiss,
	.positive = r_positive,
	.mark_read = r_mark_read,
	.pair_open = r_pair_open,
	.pair_cancel = r_pair_cancel,
	.dev_use = r_dev_use,
	.dev_remove = r_dev_remove,
	.control_active = r_control_active,
	.set_mode = r_set_mode,
	.power_off = r_power_off,
	.vibration = r_vibration,
};

/* the devices part's callbacks, for the product to pass to rdev_init() (or to chain) */
static void cb_passkey(uint8_t slot, uint32_t key)
{
	rscr_on_passkey(slot, key);
}

static void cb_hide(uint8_t slot)
{
	ARG_UNUSED(slot);
}

static void cb_paired(uint8_t slot)
{
	rscr_on_paired(slot);
}

static void cb_window_closed(void)
{
	rscr_on_window_closed();
}

static void cb_removed(uint8_t slot)
{
	rscr_on_removed(slot);
}

static void cb_active(uint8_t slot)
{
	rscr_on_active_changed(slot);
}

static void cb_link(uint8_t slot, bool up)
{
	ARG_UNUSED(slot);
	ARG_UNUSED(up);
	rscr_poke();
}

static const struct rdev_callbacks dev_cbs = {
	.passkey_show = cb_passkey,
	.passkey_hide = cb_hide,
	.paired = cb_paired,
	.window_closed = cb_window_closed,
	.removed = cb_removed,
	.active_changed = cb_active,
	.link = cb_link,
};

const struct rdev_callbacks *rscr_dev_callbacks(void)
{
	return &dev_cbs;
}
