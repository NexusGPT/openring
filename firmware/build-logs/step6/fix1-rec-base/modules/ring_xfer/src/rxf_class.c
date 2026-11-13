/*
 * rxf_class.c: the thin part of the USB transfer (software step 6, unit U4). Reads requests from the bulk OUT pipe,
 * runs them one at a time on the transfer thread, answers BUSY while one runs, enables the stack on VBUS ready and
 * disables it on VBUS removed, and passes the bus events to the join. Hardware only through rhw_usb() and rhw_clock()
 * (ring_rhw). No USB command starts or stops a recording (FW l.209): nothing here names the core.
 * "FW l.N" = line N of design/firmware.md. Written for this project.
 */
#include <errno.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include <ring_rhw/rhw.h>
#include <ring_xfer/rxf.h>

#include "rxf_desc.h"
#include "rxf_proto.h"

#define HDR RREC_MSG_HEADER_BYTES
#define BUSY_Q 4u

enum item {
	IT_REQ,
	IT_VBUS_READY,
	IT_VBUS_REMOVED,
	IT_CONFIGURED,
	IT_UNCONFIGURED,
};

static struct rxf_ctx ctx;
static const struct rxf_backend *be;
static struct rxf_cb cb;

/* request assembly (driver context, under `lk`) */
static struct k_spinlock lk;
static uint8_t buf_a[RXF_REQ_BYTES];
static uint8_t buf_b[RXF_REQ_BYTES];
static uint8_t *asm_p = buf_a;      /* being assembled */
static uint8_t *run_p = buf_b;      /* handed to the transfer thread */
static size_t asm_n, asm_len, run_n;
static bool hdr_ok, discard;
static int64_t last_rx_ms;
static uint8_t busy_q[BUSY_Q][HDR];
static uint32_t busy_n;

static atomic_t busy;               /* a request is queued or running (rxf_busy) */
static atomic_t cancel_req;         /* rxf_abort(): drop the request that has not started */
static volatile bool vbus;
K_MSGQ_DEFINE(itemq, sizeof(uint8_t), 16, 1);
static K_MUTEX_DEFINE(tx_lock);
static bool tx_held;
static K_MUTEX_DEFINE(fin_mutex);
static K_CONDVAR_DEFINE(fin_cv);

static K_THREAD_STACK_DEFINE(xfer_stack, CONFIG_RING_XFER_STACK_SIZE);
static struct k_thread xfer_thread;
static bool thread_started;
static void busy_work_fn(struct k_work *w);
static K_WORK_DEFINE(busy_work, busy_work_fn);

static uint32_t le32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void post(enum item it)
{
	uint8_t v = (uint8_t)it;

	(void)k_msgq_put(&itemq, &v, K_NO_WAIT);
}

/* ------------------------------------------------------------------ bulk OUT: requests in (driver context) */
/* A complete request, or the 16 bytes of one that cannot be read (bad magic, a length beyond the largest request). */
static void submit(size_t n)
{
	if (atomic_get(&busy) != 0) {
		/* a command runs or waits: answer BUSY (FW l.711, rule C24), or the request's own error status */
		if (busy_n < BUSY_Q) {
			rxf_proto_busy_header(asm_p, n, busy_q[busy_n]);
			busy_n++;
			k_work_submit(&busy_work);
		}
		return;
	}
	uint8_t *t = run_p;

	run_p = asm_p;
	asm_p = t;
	run_n = n;
	atomic_set(&busy, 1);
	post(IT_REQ);
}

static void rx_reset(void)
{
	asm_n = 0u;
	asm_len = 0u;
	hdr_ok = false;
	discard = false;
}

static void on_rx(const uint8_t *d, size_t n)
{
	int64_t now = rhw_clock()->now_ms();
	k_spinlock_key_t k = k_spin_lock(&lk);

	if (!vbus) {
		k_spin_unlock(&lk, k);
		return;
	}
	/* silence: a half-read request or the rest of a refused one is dropped (a resync rule, not in FW) */
	if ((asm_n != 0u || discard) && now - last_rx_ms >= CONFIG_RING_XFER_RESYNC_MS) {
		rx_reset();
	}
	last_rx_ms = now;
	while (n > 0u && !discard) {
		size_t need = asm_n < HDR ? HDR - asm_n : HDR + asm_len - asm_n;
		size_t take = MIN(need, n);

		memcpy(asm_p + asm_n, d, take);
		asm_n += take;
		d += take;
		n -= take;
		if (!hdr_ok && asm_n == HDR) {
			uint32_t len = le32(asm_p + RREC_MSG_OFF_LENGTH);
			uint16_t magic = (uint16_t)(asm_p[0] | (asm_p[1] << 8));

			if (magic != RREC_MSG_MAGIC || len > RXF_MAX_REQ_PAYLOAD) {
				submit(HDR);              /* answered BAD_MAGIC or BAD_ARG; the rest is dropped */
				rx_reset();
				discard = true;
				break;
			}
			hdr_ok = true;
			asm_len = len;
		}
		if (hdr_ok && asm_n == HDR + asm_len) {
			submit(asm_n);
			rx_reset();
		}
	}
	k_spin_unlock(&lk, k);
}

/* ------------------------------------------------------------------ bulk IN: responses out */
static int emit_cb(void *user, const uint8_t *data, size_t len, bool last)
{
	int r;

	ARG_UNUSED(user);
	if (!tx_held) {
		k_mutex_lock(&tx_lock, K_FOREVER);
		tx_held = true;
	}
	if (atomic_get(&cancel_req) != 0 || !vbus) {
		r = -ECANCELED;
	} else {
		r = rhw_usb()->send(data, len, CONFIG_RING_XFER_SEND_TIMEOUT_MS);
	}
	if (last || r != 0) {
		tx_held = false;
		k_mutex_unlock(&tx_lock);
	}
	return r;
}

static void busy_work_fn(struct k_work *w)
{
	ARG_UNUSED(w);
	for (;;) {
		uint8_t h[HDR];
		k_spinlock_key_t k = k_spin_lock(&lk);

		if (busy_n == 0u) {
			k_spin_unlock(&lk, k);
			return;
		}
		memcpy(h, busy_q[0], HDR);
		memmove(busy_q[0], busy_q[1], (BUSY_Q - 1u) * HDR);
		busy_n--;
		k_spin_unlock(&lk, k);
		/* after any response that is being sent, never inside it */
		k_mutex_lock(&tx_lock, K_FOREVER);
		if (vbus) {
			(void)rhw_usb()->send(h, HDR, CONFIG_RING_XFER_SEND_TIMEOUT_MS);
		}
		k_mutex_unlock(&tx_lock);
	}
}

/* ------------------------------------------------------------------ the transfer thread */
static void run_request(void)
{
	struct rxf_result res;

	if (atomic_get(&cancel_req) == 0 && vbus) {
		(void)rxf_proto_handle(&ctx, rxf_desc_mps(rhw_usb()->speed()), run_p, run_n, emit_cb, NULL, &res);
		if (tx_held) {
			tx_held = false;
			k_mutex_unlock(&tx_lock);
		}
	}
	atomic_set(&cancel_req, 0);
	atomic_set(&busy, 0);
	k_mutex_lock(&fin_mutex, K_FOREVER);
	k_condvar_broadcast(&fin_cv);
	k_mutex_unlock(&fin_mutex);
}

static void thread_fn(void *a, void *b, void *c)
{
	ARG_UNUSED(a);
	ARG_UNUSED(b);
	ARG_UNUSED(c);
	for (;;) {
		uint8_t it;

		if (k_msgq_get(&itemq, &it, K_FOREVER) != 0) {
			continue;
		}
		switch ((enum item)it) {
		case IT_REQ:
			run_request();
			break;
		case IT_VBUS_READY:
			/* FW l.978: the stack starts only after the power chip reported VBUS */
			(void)rhw_usb()->enable();
			break;
		case IT_VBUS_REMOVED:
			(void)rhw_usb()->disable();
			break;
		case IT_CONFIGURED:
			if (cb.configured != NULL) {
				cb.configured();
			}
			break;
		case IT_UNCONFIGURED:
			if (cb.unconfigured != NULL) {
				cb.unconfigured();
			}
			break;
		}
	}
}

/* ------------------------------------------------------------------ bus events (driver context) */
static void on_event(enum rhw_usb_event ev)
{
	k_spinlock_key_t k;

	switch (ev) {
	case RHW_USB_VBUS_READY:
		vbus = true;
		post(IT_VBUS_READY);
		break;
	case RHW_USB_VBUS_REMOVED:
		vbus = false;
		rxf_proto_abort(&ctx);            /* FW l.179: the command that runs stops, no response */
		k = k_spin_lock(&lk);
		rx_reset();
		busy_n = 0u;
		k_spin_unlock(&lk, k);
		post(IT_VBUS_REMOVED);
		break;
	case RHW_USB_CONFIGURED:
		post(IT_CONFIGURED);
		break;
	case RHW_USB_UNCONFIGURED:
	case RHW_USB_SUSPENDED:
		k = k_spin_lock(&lk);
		rx_reset();
		k_spin_unlock(&lk, k);
		post(IT_UNCONFIGURED);
		break;
	}
}

static const struct rhw_usb_cb usb_cb = { .rx = on_rx, .event = on_event };

/* ------------------------------------------------------------------ public */
int rxf_start(const struct rxf_backend *backend, const struct rxf_cb *callbacks)
{
	if (backend == NULL || backend->may_answer == NULL || backend->get_info == NULL || backend->list == NULL ||
	    backend->range_check == NULL || backend->read_chunk == NULL || backend->confirm == NULL ||
	    backend->del == NULL || backend->set_time == NULL || backend->get_battery == NULL ||
	    backend->fw_begin == NULL || backend->fw_data == NULL || backend->fw_end == NULL ||
	    backend->get_log == NULL || backend->factory == NULL) {
		return -EINVAL;
	}
	be = backend;
	memset(&cb, 0, sizeof(cb));
	if (callbacks != NULL) {
		cb = *callbacks;
	}
	k_msgq_purge(&itemq);
	k_spinlock_key_t k = k_spin_lock(&lk);

	rx_reset();
	busy_n = 0u;
	k_spin_unlock(&lk, k);
	atomic_set(&busy, 0);
	atomic_set(&cancel_req, 0);
	tx_held = false;
	vbus = false;
	rxf_proto_init(&ctx, be);
	if (!thread_started) {
		thread_started = true;
		k_thread_create(&xfer_thread, xfer_stack, K_THREAD_STACK_SIZEOF(xfer_stack), thread_fn, NULL, NULL, NULL,
				CONFIG_RING_XFER_THREAD_PRIO, 0, K_NO_WAIT);
		k_thread_name_set(&xfer_thread, "rxf");
	}
	rhw_usb()->set_callbacks(&usb_cb);
	return 0;
}

void rxf_abort(void)
{
	if (atomic_get(&busy) != 0) {
		atomic_set(&cancel_req, 1);
		rxf_proto_abort(&ctx);
	}
}

int rxf_finish(int32_t timeout_ms)
{
	k_timepoint_t end = sys_timepoint_calc(K_MSEC(timeout_ms));
	int r = 0;

	k_mutex_lock(&fin_mutex, K_FOREVER);
	while (atomic_get(&busy) != 0) {
		if (k_condvar_wait(&fin_cv, &fin_mutex, sys_timepoint_timeout(end)) != 0) {
			r = atomic_get(&busy) != 0 ? -ETIMEDOUT : 0;
			break;
		}
	}
	k_mutex_unlock(&fin_mutex);
	return r;
}

bool rxf_busy(void)
{
	return atomic_get(&busy) != 0;
}
