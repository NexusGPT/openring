/*
 * ring_rhw simulation: the USB transport. A byte pipe between a test (the case's host) and the class: requests in,
 * responses out in packets of the bus speed's size, bus events. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>

#include "sim_int.h"

static bool enabled;
static enum rhw_usb_speed speed;
static bool host_stopped;
static struct rhw_usb_cb cbs;
static uint8_t hostbuf[CONFIG_RING_RHW_SIM_USB_HOST_BYTES];
static size_t host_n;
static void (*sink)(const uint8_t *data, size_t len);

static int u_enable(void)
{
	if (sim_dead(RHW_EV_USB_ENABLE)) {
		return -ESHUTDOWN;
	}
	enabled = true;
	sim_log(RHW_EV_USB_ENABLE, 0, 0, 0, 0, NULL);
	return 0;
}

static int u_disable(void)
{
	if (sim_dead(RHW_EV_USB_DISABLE)) {
		return -ESHUTDOWN;
	}
	enabled = false;
	sim_log(RHW_EV_USB_DISABLE, 0, 0, 0, 0, NULL);
	return 0;
}

static int u_send(const uint8_t *data, size_t len, int32_t timeout_ms)
{
	size_t mps = speed == RHW_USB_HS ? RREC_USB_MPS_HS : RREC_USB_MPS_FS;
	size_t off = 0;

	if (sim_dead(RHW_EV_USB_PACKET)) {
		return -ESHUTDOWN;
	}
	if (!enabled) {
		sim_log(RHW_EV_USB_PACKET, len, mps, 0, -ENODEV, NULL);
		return -ENODEV;
	}
	if (len == 0) {
		sim_log(RHW_EV_USB_PACKET, 0, mps, 0, 0, NULL);   /* a zero-length packet: logged as such */
		return 0;
	}
	while (off < len) {
		size_t n = MIN(mps, len - off);

		if (host_stopped || (sink == NULL && host_n + n > sizeof(hostbuf))) {
			k_sleep(K_MSEC(timeout_ms));
			sim_log(RHW_EV_USB_PACKET, n, mps, 0, -EAGAIN, NULL);
			return -EAGAIN;
		}
		if (sink != NULL) {
			sink(data + off, n);
		} else {
			memcpy(hostbuf + host_n, data + off, n);
			host_n += n;
		}
		sim_log(RHW_EV_USB_PACKET, n, mps, 0, 0, NULL);
		off += n;
	}
	return 0;
}

static enum rhw_usb_speed u_speed(void)
{
	return speed;
}

static void u_set_cb(const struct rhw_usb_cb *cb)
{
	if (cb == NULL) {
		memset(&cbs, 0, sizeof(cbs));
	} else {
		cbs = *cb;
	}
}

const struct rhw_usb_api rhw_sim_usb_api = {
	.enable = u_enable, .disable = u_disable, .send = u_send, .speed = u_speed, .set_callbacks = u_set_cb,
};

void rhw_sim_usb_event(enum rhw_usb_event ev)
{
	sim_log(RHW_EV_USB_EVENT, ev, 0, 0, 0, NULL);
	if (cbs.event != NULL) {
		cbs.event(ev);
	}
}

void sim_usb_vbus_event(bool present)
{
	rhw_sim_usb_event(present ? RHW_USB_VBUS_READY : RHW_USB_VBUS_REMOVED);
}

void rhw_sim_usb_speed(enum rhw_usb_speed s)
{
	speed = s;
}

void rhw_sim_usb_host_stop(bool stop)
{
	host_stopped = stop;
}

int rhw_sim_usb_host_write(const uint8_t *data, size_t len)
{
	if (!enabled) {
		sim_log(RHW_EV_USB_RX, len, 0, 0, -ENODEV, NULL);
		return -ENODEV;
	}
	sim_log(RHW_EV_USB_RX, len, 0, 0, 0, NULL);
	if (cbs.rx != NULL) {
		cbs.rx(data, len);
	}
	return 0;
}

size_t rhw_sim_usb_host_read(uint8_t *out, size_t max)
{
	size_t n = MIN(max, host_n);

	memcpy(out, hostbuf, n);
	memmove(hostbuf, hostbuf + n, host_n - n);
	host_n -= n;
	return n;
}

void rhw_sim_usb_host_sink(void (*s)(const uint8_t *data, size_t len))
{
	sink = s;
}

bool rhw_sim_usb_enabled(void)
{
	return enabled;
}

void sim_usb_reset(bool full)
{
	enabled = false;
	memset(&cbs, 0, sizeof(cbs));
	host_n = 0;
	if (full) {
		speed = RHW_USB_FS;
		host_stopped = false;
		sink = NULL;
	}
}
