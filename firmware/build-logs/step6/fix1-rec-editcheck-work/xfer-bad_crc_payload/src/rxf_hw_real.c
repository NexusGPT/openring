/*
 * rxf_hw_real.c: the real USB device for the transfer part (software step 6, unit U4). Built only where the simulated
 * drivers are off (the development kit build, decision D15). It is NOT PROVEN on a ring: no USB controller exists in
 * any simulation of step 6 (plan section 7, row X1). Where the devicetree has no enabled `zephyr_udc0` node the file registers
 * nothing and rhw_usb() keeps answering -ENODEV (the "absent" instance of ring_rhw).
 * Kit calls used: the device_next stack (USBD_DEFINE_CLASS, usbd_add_configuration, usbd_register_class, usbd_init,
 * usbd_enable, usbd_disable, usbd_bus_speed, usbd_msg_register_cb, usbd_ep_enqueue, usbd_ep_buf_alloc/free via the
 * buffer pool macro). Written for this project; the stack's own loopback class is the model of the shape only.
 * "FW l.N" = line N of design/firmware.md. No pin is named here.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>
#include <zephyr/net_buf.h>
#include <zephyr/usb/usbd.h>

#include <ring_rhw/rhw.h>

#include "rxf_desc.h"

/* what the full-run stage "recorder-product-drivers" prints: whether the real calls were compiled */
#if DT_NODE_HAS_STATUS(DT_NODELABEL(zephyr_udc0), okay)
const bool rxf_hw_real_compiled = true;

/* Placeholders for the product's identity: the vendor and product id and the strings are the owner's to choose
 * (TO CONFIRM); the values below are the kit's test pair and must be replaced before a release. */
#define RXF_VID 0x2fe3
#define RXF_PID 0x0100
#define RXF_BLOCK 1024u         /* bytes per IN transfer: a multiple of both packet sizes (CONFIG_UDC_BUF_POOL_SIZE of the
				 * application must hold a few of them) */

struct rxf_desc_set {
	uint8_t bytes[RXF_DESC_BYTES];
	struct usb_desc_header nil;
};

static struct rxf_desc_set fs_set, hs_set;
static struct rhw_usb_cb ucb;
static struct usbd_class_data *class_ctx;
static K_SEM_DEFINE(in_done, 0, 1);
static int in_err;
static bool configured;

USBD_DEVICE_DEFINE(rxf_usbd, DEVICE_DT_GET(DT_NODELABEL(zephyr_udc0)), RXF_VID, RXF_PID);
USBD_DESC_LANG_DEFINE(rxf_lang);
USBD_DESC_MANUFACTURER_DEFINE(rxf_mfr, "Ring");
USBD_DESC_PRODUCT_DEFINE(rxf_product, "Ring recorder");
USBD_DESC_CONFIG_DEFINE(rxf_fs_cfg_desc, "FS");
USBD_DESC_CONFIG_DEFINE(rxf_hs_cfg_desc, "HS");
static const uint8_t rxf_attrib = 0;            /* bus powered, no remote wake-up */
USBD_CONFIGURATION_DEFINE(rxf_fs_config, rxf_attrib, 100, &rxf_fs_cfg_desc);
USBD_CONFIGURATION_DEFINE(rxf_hs_config, rxf_attrib, 100, &rxf_hs_cfg_desc);

static struct net_buf *in_pending;      /* the IN buffer on the bus: tells the IN completion from an OUT one */

static int enqueue_out(struct usbd_class_data *c_data)
{
	struct net_buf *buf = usbd_ep_buf_alloc(c_data, RREC_USB_EP_OUT, RREC_USB_MPS_HS);
	int r;

	if (buf == NULL) {
		return -ENOMEM;
	}
	r = usbd_ep_enqueue(c_data, buf);
	if (r != 0) {
		net_buf_unref(buf);
	}
	return r;
}

static int rxf_request(struct usbd_class_data *c_data, struct net_buf *buf, int err)
{
	if (buf != in_pending) {
		if (err == 0 && ucb.rx != NULL && buf->len != 0) {
			ucb.rx(buf->data, buf->len);                 /* FW l.677: copy and queue */
		}
		net_buf_unref(buf);
		if (err != -ECONNABORTED) {
			(void)enqueue_out(c_data);
		}
	} else {
		in_err = err;
		in_pending = NULL;
		net_buf_unref(buf);
		k_sem_give(&in_done);
	}
	return 0;
}

static void *rxf_get_desc(struct usbd_class_data *c_data, const enum usbd_speed speed)
{
	ARG_UNUSED(c_data);
	return speed == USBD_SPEED_HS ? (void *)&hs_set : (void *)&fs_set;   /* FW l.669, l.1 of 6.1 */
}

static void rxf_enable(struct usbd_class_data *c_data)
{
	class_ctx = c_data;
	configured = true;
	(void)enqueue_out(c_data);
	(void)enqueue_out(c_data);
}

static void rxf_disable(struct usbd_class_data *c_data)
{
	ARG_UNUSED(c_data);
	configured = false;
}

static int rxf_init(struct usbd_class_data *c_data)
{
	ARG_UNUSED(c_data);
	(void)rxf_desc_get(RHW_USB_FS, fs_set.bytes);
	(void)rxf_desc_get(RHW_USB_HS, hs_set.bytes);
	memset(&fs_set.nil, 0, sizeof(fs_set.nil));
	memset(&hs_set.nil, 0, sizeof(hs_set.nil));
	return 0;
}

static struct usbd_class_api rxf_class_api = {
	.request = rxf_request,
	.enable = rxf_enable,
	.disable = rxf_disable,
	.init = rxf_init,
	.get_desc = rxf_get_desc,
};

USBD_DEFINE_CLASS(rxf_vendor, &rxf_class_api, NULL, NULL);

static void msg_cb(struct usbd_context *const ctx, const struct usbd_msg *const msg)
{
	ARG_UNUSED(ctx);
	if (ucb.event == NULL) {
		return;
	}
	switch (msg->type) {
	case USBD_MSG_VBUS_READY:
		ucb.event(RHW_USB_VBUS_READY);
		break;
	case USBD_MSG_VBUS_REMOVED:
		ucb.event(RHW_USB_VBUS_REMOVED);
		break;
	case USBD_MSG_CONFIGURATION:
		ucb.event(msg->status != 0 ? RHW_USB_CONFIGURED : RHW_USB_UNCONFIGURED);
		break;
	case USBD_MSG_SUSPEND:
		ucb.event(RHW_USB_SUSPENDED);
		break;
	case USBD_MSG_RESET:
		ucb.event(RHW_USB_UNCONFIGURED);
		break;
	default:
		break;
	}
}

static bool inited;

/* The first call of the stack that fails ends the start; its own error code goes back to the caller. */
#define STEP(call)                                                                                                     \
	do {                                                                                                           \
		int step_r = (call);                                                                                   \
		if (step_r != 0) {                                                                                     \
			return step_r;                                                                                 \
		}                                                                                                      \
	} while (0)

static int r_enable(void)
{
	if (!inited) {
		STEP(usbd_add_descriptor(&rxf_usbd, &rxf_lang));
		STEP(usbd_add_descriptor(&rxf_usbd, &rxf_mfr));
		STEP(usbd_add_descriptor(&rxf_usbd, &rxf_product));
		STEP(usbd_add_configuration(&rxf_usbd, USBD_SPEED_FS, &rxf_fs_config));
		/* FW l.669: both registered, the high-speed one when the controller can do it (the nRF54LM20A usbhs can) */
		if (usbd_caps_speed(&rxf_usbd) == USBD_SPEED_HS) {
			STEP(usbd_add_configuration(&rxf_usbd, USBD_SPEED_HS, &rxf_hs_config));
		}
		STEP(usbd_register_class(&rxf_usbd, "rxf_vendor", USBD_SPEED_FS, 1));
		if (usbd_caps_speed(&rxf_usbd) == USBD_SPEED_HS) {
			STEP(usbd_register_class(&rxf_usbd, "rxf_vendor", USBD_SPEED_HS, 1));
		}
		STEP(usbd_msg_register_cb(&rxf_usbd, msg_cb));
		STEP(usbd_init(&rxf_usbd));
		inited = true;
	}
	return usbd_enable(&rxf_usbd);              /* only after VBUS ready (FW l.978) */
}

static int r_disable(void)
{
	return usbd_disable(&rxf_usbd);             /* on VBUS removed (FW l.978) */
}

static int r_send(const uint8_t *data, size_t len, int32_t timeout_ms)
{
	size_t off = 0;

	if (!inited || !configured) {
		return -ENODEV;
	}
	while (off < len) {
		size_t n = MIN(RXF_BLOCK, len - off);
		struct net_buf *buf = usbd_ep_buf_alloc(class_ctx, RREC_USB_EP_IN, n);
		int r;

		if (buf == NULL) {
			return -EAGAIN;
		}
		net_buf_add_mem(buf, data + off, n);
		in_pending = buf;
		r = usbd_ep_enqueue(class_ctx, buf);
		if (r != 0) {
			in_pending = NULL;
			net_buf_unref(buf);
			return r;
		}
		if (k_sem_take(&in_done, K_MSEC(timeout_ms)) != 0) {
			return -EAGAIN;                 /* the host stopped reading */
		}
		if (in_err != 0) {
			return in_err;
		}
		off += n;
	}
	return 0;
}

static enum rhw_usb_speed r_speed(void)
{
	return usbd_bus_speed(&rxf_usbd) == USBD_SPEED_HS ? RHW_USB_HS : RHW_USB_FS;   /* FW l.669 */
}

static void r_set_callbacks(const struct rhw_usb_cb *cb)
{
	if (cb == NULL) {
		memset(&ucb, 0, sizeof(ucb));
	} else {
		ucb = *cb;
	}
}

static const struct rhw_usb_api real_api = {
	.enable = r_enable, .disable = r_disable, .send = r_send, .speed = r_speed, .set_callbacks = r_set_callbacks,
};

static int rxf_hw_real_register(void)
{
	return rhw_register_usb(&real_api);
}

SYS_INIT(rxf_hw_real_register, APPLICATION, 90);
#else
const bool rxf_hw_real_compiled = false;
#endif
