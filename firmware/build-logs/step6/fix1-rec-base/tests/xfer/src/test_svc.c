/*
 * test_svc.c: suite xfer_svc (unit U4): the thin part (rxf_class.c) on the simulated USB transport, with the fake
 * backend. Rows X4, X6, X16, C18, C24 of firmware/docs/step6-plan.md. The test is the case's host: it writes requests
 * with rhw_sim_usb_host_write() and reads responses with rhw_sim_usb_host_read() or a sink. Simulated time only.
 */
#include "xt.h"

static uint32_t conf_n, unconf_n;
static char conf_thread[16];

static void on_conf(void)
{
	conf_n++;
	strncpy(conf_thread, k_thread_name_get(k_current_get()), sizeof(conf_thread) - 1);
}

static void on_unconf(void)
{
	unconf_n++;
}

static const struct rxf_cb cbs = { .configured = on_conf, .unconfigured = on_unconf };

static void before(void *f)
{
	ARG_UNUSED(f);
	rhw_sim_reset();
	fake_reset();
	conf_n = unconf_n = 0;
	conf_thread[0] = 0;
	zassert_equal(rxf_start(fake_be(), &cbs), 0);
}

static void after(void *f)
{
	ARG_UNUSED(f);
	rhw_sim_usb_host_stop(false);
	rhw_sim_usb_host_sink(NULL);
	(void)rxf_finish(5000);
	k_msleep(5);
}

ZTEST_SUITE(xfer_svc, NULL, NULL, before, after, NULL);

static uint8_t rq[RXF_REQ_BYTES];
static uint8_t rsp[20000];

static void vbus_on(void)
{
	rhw_sim_vbus(true);
	k_msleep(2);
}

static void host_send(uint8_t op, uint32_t tag, const void *pl, uint32_t plen)
{
	size_t n = xt_req(rq, op, tag, pl, plen);

	zassert_equal(rhw_sim_usb_host_write(rq, n), 0);
}

/* what the host receives: 16 bytes, then length more; returns the bytes read (stops at the timeout) */
static size_t host_get(uint8_t *out, size_t max, uint32_t timeout_ms)
{
	size_t n = 0;

	for (uint32_t t = 0; t < timeout_ms; t++) {
		n += rhw_sim_usb_host_read(out + n, max - n);
		if (n >= 16 && n >= 16u + xt_le(out + 8, 4)) {
			return n;
		}
		k_msleep(1);
	}
	return n + rhw_sim_usb_host_read(out + n, max - n);
}

/* X4: the stack is enabled on VBUS ready and disabled on VBUS removed, and not before */
ZTEST(xfer_svc, test_stack_follows_vbus)
{
	uint8_t one[16];

	k_msleep(5);
	zassert_false(rhw_sim_usb_enabled(), "no stack without VBUS");
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_ENABLE), 0u, "no enable before VBUS");
	zassert_equal(rhw_sim_usb_host_write(one, 1), -ENODEV, "nothing listens without VBUS");

	rhw_sim_vbus(true);
	k_msleep(2);
	zassert_true(rhw_sim_usb_enabled());
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_ENABLE), 1u);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_DISABLE), 0u);

	rhw_sim_vbus(false);
	k_msleep(2);
	zassert_false(rhw_sim_usb_enabled());
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_ENABLE), 1u);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_DISABLE), 1u);

	/* a second insertion: one more of each, in order enable then disable */
	rhw_sim_vbus(true);
	k_msleep(2);
	rhw_sim_vbus(false);
	k_msleep(2);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_ENABLE), 2u);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_DISABLE), 2u);
	int32_t e1 = rhw_sim_log_find(RHW_EV_USB_ENABLE, 0);
	int32_t d1 = rhw_sim_log_find(RHW_EV_USB_DISABLE, 0);
	int32_t e2 = rhw_sim_log_find(RHW_EV_USB_ENABLE, (uint32_t)e1 + 1);

	zassert_true(e1 >= 0 && e1 < d1 && d1 < e2, "enable, disable, enable in this order");
	zassert_false(rhw_sim_usb_enabled());
}

/* X4: the unit answers only while the backend allows it (CHARGING, TRANSFER, FACTORY_TEST) */
ZTEST(xfer_svc, test_silent_when_not_allowed_over_transport)
{
	vbus_on();
	fk.allowed = false;
	host_send(RREC_OP_GET_INFO, 1, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 0u, "no byte while the state does not allow USB");
	zassert_equal(fk.calls[RREC_OP_GET_INFO], 0u);
	fk.allowed = true;
	host_send(RREC_OP_GET_INFO, 2, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u);
	zassert_equal(rsp[3], RREC_ST_OK);
}

/* a request over the transport, written whole, in packets of 64 and byte by byte: the same response */
ZTEST(xfer_svc, test_request_in_pieces)
{
	uint8_t pl[8] = { 0x02, 0x01, 0, 0, 0xD4, 0xC3, 0xB2, 0xA1 };
	size_t n = xt_req(rq, RREC_OP_CONFIRM, 0x0A0B0C0Du, pl, 8);
	static const size_t step[] = { 24, 5, 1, 16, 17 };

	vbus_on();
	for (unsigned s = 0; s < ARRAY_SIZE(step); s++) {
		fake_reset();
		for (size_t off = 0; off < n; off += step[s]) {
			zassert_equal(rhw_sim_usb_host_write(rq + off, MIN(step[s], n - off)), 0);
			k_msleep(1);
		}
		zassert_equal(host_get(rsp, sizeof(rsp), 30), 16u, "step %u", (unsigned)step[s]);
		zassert_equal(rsp[3], RREC_ST_OK);
		zassert_equal(xt_le(rsp + 4, 4), 0x0A0B0C0Du);
		zassert_equal(fk.last_rec, 0x102u);
		zassert_equal(fk.last_digest, 0xA1B2C3D4u);
	}
	/* two requests in one write: the first runs, the second finds it still busy or runs after: both are answered once */
	fake_reset();
	size_t n2 = xt_req(rq + n, RREC_OP_GET_BATTERY, 0x22, NULL, 0);

	zassert_equal(rhw_sim_usb_host_write(rq, n + n2), 0);
	k_msleep(20);
	size_t got = rhw_sim_usb_host_read(rsp, sizeof(rsp));

	zassert_equal(got, 32u, "an answer for each of the two requests");
	/* the BUSY header may overtake the response of the first, so match by tag */
	for (unsigned i = 0; i < 2; i++) {
		uint32_t tag = xt_le(rsp + 16 * i + 4, 4);

		if (tag == 0x0A0B0C0Du) {
			zassert_equal(rsp[16 * i + 3], RREC_ST_OK, "the first request ran");
		} else {
			zassert_equal(tag, 0x22u);
			zassert_equal(rsp[16 * i + 3], RREC_ST_BUSY, "the second arrived while the first was queued: BUSY (FW l.711)");
		}
	}
	zassert_equal(fk.calls[RREC_OP_GET_BATTERY], 0u, "the second request did not run");
}

/* X6: no zero-length packet ends a response; every packet but the last is full; the bytes are 16 + length */
static void check_packets(unsigned expect_bytes, uint32_t mps)
{
	uint32_t n = rhw_sim_log_count(), pk = 0, sum = 0;
	struct rhw_sim_ev ev;
	bool short_seen = false;

	for (uint32_t i = 0; i < n; i++) {
		zassert_true(rhw_sim_log_get(i, &ev));
		if (ev.kind != RHW_EV_USB_PACKET) {
			continue;
		}
		zassert_not_equal(ev.a0, 0, "a zero-length packet at log entry %u", i);
		zassert_equal(ev.a1, mps, "packet size of the speed");
		zassert_false(short_seen, "a short packet before the end of the response");
		if (ev.a0 < (int64_t)mps) {
			short_seen = true;
		}
		zassert_true(ev.a0 <= (int64_t)mps);
		sum += (uint32_t)ev.a0;
		pk++;
	}
	zassert_equal(sum, expect_bytes, "bytes in the packets");
	zassert_true(pk >= 1u);
}

ZTEST(xfer_svc, test_no_zero_length_packet)
{
	uint8_t fac = 0x01;

	vbus_on();
	/* full speed: response of exactly 64 bytes, then 128, then 100 (one short) */
	static const size_t pay[] = { 48, 112, 84 };

	for (unsigned i = 0; i < ARRAY_SIZE(pay); i++) {
		fk.factory_out_len = pay[i];
		rhw_sim_log_clear();
		host_send(RREC_OP_FACTORY, 1, &fac, 1);
		zassert_equal(host_get(rsp, sizeof(rsp), 30), 16u + pay[i]);
		zassert_equal(xt_le(rsp + 8, 4), pay[i]);
		check_packets((unsigned)(16 + pay[i]), 64);
	}
	/* high speed: 256 bytes are one short packet, nothing after it */
	rhw_sim_usb_speed(RHW_USB_HS);
	fk.factory_out_len = 240;
	rhw_sim_log_clear();
	host_send(RREC_OP_FACTORY, 1, &fac, 1);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 16u + 240u);
	check_packets(16 + 240, 512);
	/* exactly 512 bytes (16 + 496): one full packet and nothing after it */
	uint8_t pl[6] = { 0, 0, 0, 0, 64, 0 };

	fk.list_len = 496;
	rhw_sim_log_clear();
	host_send(RREC_OP_LIST_RECORDINGS, 2, pl, 6);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 512u);
	check_packets(512, 512);
	zassert_equal(rhw_sim_log_count_kind(RHW_EV_USB_PACKET), 1u);
	/* a LIST of 64 entries: 16 + 2 + 4,096 = 4,114 bytes = 8 packets of 512 and a short one */
	fk.list_len = RXF_LIST_PAYLOAD_MAX;

	rhw_sim_log_clear();
	host_send(RREC_OP_LIST_RECORDINGS, 2, pl, 6);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 4114u);
	check_packets(4114, 512);
}

/* the bytes of a long response go to a sink: header, then the reference CRC of everything after it */
static size_t sink_total;
static uint8_t sink_hdr[16];
static uint32_t sink_crc;
static bool sink_abort_first;

static void sink_fn(const uint8_t *d, size_t n)
{
	size_t skip = 0;

	if (sink_total < 16) {
		skip = MIN(16 - sink_total, n);
		memcpy(sink_hdr + sink_total, d, skip);
	}
	if (n > skip) {
		sink_crc = xt_crc(sink_crc, d + skip, n - skip);
	}
	sink_total += n;
	if (sink_abort_first) {
		sink_abort_first = false;
		rxf_abort();
	}
}

/* X6, X10 over the transport: a READ_RANGE of 3 chunks arrives as one stream of packets of the speed, no short packet
 * inside, header CRC equal to the reference CRC of the payload */
ZTEST(xfer_svc, test_read_range_over_transport)
{
	uint8_t pl[12];
	static const enum rhw_usb_speed sp[] = { RHW_USB_FS, RHW_USB_HS };

	vbus_on();
	for (unsigned s = 0; s < 2; s++) {
		xt_put(pl, 12, 4);
		xt_put(pl + 4, 0, 4);
		xt_put(pl + 8, 3, 4);
		rhw_sim_usb_speed(sp[s]);
		sink_total = 0;
		sink_crc = 0;
		rhw_sim_usb_host_sink(sink_fn);
		rhw_sim_log_clear();
		host_send(RREC_OP_READ_RANGE, 0x44, pl, 12);
		for (unsigned t = 0; t < 2000 && sink_total < 16u + 3u * 33280u; t++) {
			k_msleep(1);
		}
		zassert_equal(sink_total, 16u + 3u * 33280u);
		zassert_equal(xt_le(sink_hdr + 8, 4), 3u * 33280u);
		zassert_equal(xt_le(sink_hdr + 12, 4), sink_crc, "crc of the payload");
		check_packets(16 + 3 * 33280, sp[s] == RHW_USB_HS ? 512 : 64);
		rhw_sim_usb_host_sink(NULL);
		(void)rxf_finish(1000);
	}
}

static void slow(void)
{
	k_msleep(50);
}

/* X19, C24: a request that arrives while a command runs gets BUSY at once, the command's response follows, and the
 * unit is free again afterwards */
ZTEST(xfer_svc, test_busy_over_transport)
{
	vbus_on();
	fk.hook = slow;
	host_send(RREC_OP_GET_BATTERY, 0x31, NULL, 0);
	k_msleep(5);
	zassert_true(rxf_busy(), "the command runs (rxf_busy for the join)");
	host_send(RREC_OP_GET_INFO, 0x32, NULL, 0);
	k_msleep(5);
	size_t n = rhw_sim_usb_host_read(rsp, sizeof(rsp));

	zassert_equal(n, 16u, "BUSY came while the command still ran");
	zassert_equal(rsp[3], RREC_ST_BUSY);
	zassert_equal(rsp[2], RREC_OP_GET_INFO);
	zassert_equal(xt_le(rsp + 4, 4), 0x32u);
	zassert_equal(fk.calls[RREC_OP_GET_INFO], 0u);
	k_msleep(80);
	n = rhw_sim_usb_host_read(rsp, sizeof(rsp));
	zassert_equal(n, 25u, "then the response of the command that ran");
	zassert_equal(rsp[3], RREC_ST_OK);
	zassert_equal(xt_le(rsp + 4, 4), 0x31u);
	zassert_false(rxf_busy());
	fk.hook = NULL;
	host_send(RREC_OP_GET_INFO, 0x33, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u);
	zassert_equal(rsp[3], RREC_ST_OK);
	/* a bad request while a command runs gets its own status, not BUSY */
	fk.hook = slow;
	host_send(RREC_OP_GET_BATTERY, 0x34, NULL, 0);
	k_msleep(5);
	size_t m = xt_req(rq, RREC_OP_GET_INFO, 0x35, NULL, 0);

	rq[12] = 9;
	zassert_equal(rhw_sim_usb_host_write(rq, m), 0);
	k_msleep(5);
	n = rhw_sim_usb_host_read(rsp, sizeof(rsp));
	zassert_equal(n, 16u);
	zassert_equal(rsp[3], RREC_ST_BAD_CRC);
	k_msleep(80);
}

/* C18: unconfigured in TRANSFER finishes the command that runs: rxf_finish() waits for it and its response */
ZTEST(xfer_svc, test_finish_and_abort)
{
	vbus_on();
	zassert_equal(rxf_finish(10), 0, "nothing runs: returns at once");
	fk.hook = slow;
	host_send(RREC_OP_GET_BATTERY, 1, NULL, 0);
	k_msleep(5);
	zassert_true(rxf_busy());
	zassert_equal(rxf_finish(10), -ETIMEDOUT, "the command needs 50 ms");
	zassert_equal(rxf_finish(200), 0);
	zassert_false(rxf_busy());
	zassert_equal(rhw_sim_usb_host_read(rsp, sizeof(rsp)), 25u, "its response was handed over before finish returned");
	zassert_equal(rsp[3], RREC_ST_OK);

	/* rxf_abort(): the command that runs ends, no response is sent for it */
	host_send(RREC_OP_GET_BATTERY, 2, NULL, 0);
	k_msleep(5);
	rxf_abort();
	zassert_equal(rxf_finish(200), 0);
	zassert_equal(rhw_sim_usb_host_read(rsp, sizeof(rsp)), 0u, "no response for the aborted command");
	zassert_equal(fk.after_calls, 1u, "only the first command was reported");
	fk.hook = NULL;
	host_send(RREC_OP_GET_INFO, 3, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u, "the next command runs");
	/* an abort with nothing running does not spoil the next command */
	rxf_abort();
	host_send(RREC_OP_GET_INFO, 4, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u);

	/* VBUS removed while a command runs (FW l.179): nothing is sent, the stack goes off, the next insertion works */
	fk.hook = slow;
	host_send(RREC_OP_GET_BATTERY, 5, NULL, 0);
	k_msleep(5);
	rhw_sim_vbus(false);
	k_msleep(80);
	zassert_equal(rhw_sim_usb_host_read(rsp, sizeof(rsp)), 0u);
	zassert_false(rhw_sim_usb_enabled());
	zassert_false(rxf_busy());
	fk.hook = NULL;
	vbus_on();
	host_send(RREC_OP_GET_INFO, 6, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u);

	/* VBUS removed in the middle of a long response: the stream stops */
	uint8_t pl[12];

	xt_put(pl, 1, 4);
	xt_put(pl + 4, 0, 4);
	xt_put(pl + 8, 8, 4);
	sink_total = 0;
	sink_crc = 0;
	sink_abort_first = true;
	rhw_sim_usb_host_sink(sink_fn);
	host_send(RREC_OP_READ_RANGE, 7, pl, 12);
	k_msleep(100);
	zassert_true(sink_total > 0u && sink_total < 16u + 8u * 33280u, "the response stopped after an abort (%u bytes)",
		     (unsigned)sink_total);
	zassert_false(rxf_busy());
	rhw_sim_usb_host_sink(NULL);
}

/* the bus events reach the join on the transfer thread: configured, unconfigured, suspended; VBUS removal is not one */
ZTEST(xfer_svc, test_configured_callbacks)
{
	vbus_on();
	rhw_sim_usb_event(RHW_USB_CONFIGURED);
	k_msleep(2);
	zassert_equal(conf_n, 1u);
	zassert_equal(strcmp(conf_thread, "rxf"), 0, "on the transfer thread, not the driver's context (%s)", conf_thread);
	rhw_sim_usb_event(RHW_USB_UNCONFIGURED);
	k_msleep(2);
	zassert_equal(unconf_n, 1u);
	rhw_sim_usb_event(RHW_USB_SUSPENDED);
	k_msleep(2);
	zassert_equal(unconf_n, 2u);
	rhw_sim_vbus(false);
	k_msleep(2);
	zassert_equal(conf_n, 1u);
	zassert_equal(unconf_n, 2u);
}

/* a half-read request is dropped after the pipe was quiet; the rest of a refused request is dropped, then the next
 * request is read afresh */
ZTEST(xfer_svc, test_bad_magic_and_resync)
{
	uint8_t pl[8] = { 1, 0, 0, 0, 2, 0, 0, 0 };
	size_t n = xt_req(rq, RREC_OP_CONFIRM, 0x61, pl, 8);

	vbus_on();
	/* wrong magic with its payload in the same write: one BAD_MAGIC answer, payload bytes not read as a request */
	xt_put(rq, 0x5253, 2);
	zassert_equal(rhw_sim_usb_host_write(rq, n), 0);
	k_msleep(3);
	zassert_equal(rhw_sim_usb_host_read(rsp, sizeof(rsp)), 16u);
	zassert_equal(rsp[3], RREC_ST_BAD_MAGIC);
	zassert_equal(xt_le(rsp + 4, 4), 0x61u);
	zassert_equal(xt_le(rsp + 8, 4), 0u);
	zassert_equal(fk.calls[RREC_OP_CONFIRM], 0u);
	/* after a quiet period a good request is read */
	k_msleep(150);
	n = xt_req(rq, RREC_OP_GET_INFO, 0x62, NULL, 0);
	zassert_equal(rhw_sim_usb_host_write(rq, n), 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u);
	zassert_equal(xt_le(rsp + 4, 4), 0x62u);

	/* a length beyond the largest request: BAD_ARG, no memory overrun */
	n = xt_req(rq, RREC_OP_FW_DATA, 0x63, NULL, 0);
	xt_put(rq + 8, 0x7FFFFFFFu, 4);
	zassert_equal(rhw_sim_usb_host_write(rq, 16), 0);
	k_msleep(3);
	zassert_equal(rhw_sim_usb_host_read(rsp, sizeof(rsp)), 16u);
	zassert_equal(rsp[3], RREC_ST_BAD_ARG);
	k_msleep(150);

	/* half a request, then silence, then a whole one: only the whole one is answered */
	n = xt_req(rq, RREC_OP_CONFIRM, 0x64, pl, 8);
	zassert_equal(rhw_sim_usb_host_write(rq, 20), 0);
	k_msleep(150);
	n = xt_req(rq, RREC_OP_GET_INFO, 0x65, NULL, 0);
	zassert_equal(rhw_sim_usb_host_write(rq, n), 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 51u);
	zassert_equal(xt_le(rsp + 4, 4), 0x65u);
	k_msleep(10);
	zassert_equal(rhw_sim_usb_host_read(rsp, sizeof(rsp)), 0u, "nothing else was answered");
}

/* X16: the reboot request of the join comes after the OK response went out through the transport */
ZTEST(xfer_svc, test_reboot_after_response)
{
	vbus_on();
	rhw_sim_log_clear();
	host_send(RREC_OP_REBOOT, 0x77, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 16u);
	k_msleep(2);
	zassert_equal(fk.after_calls, 1u);
	zassert_equal(fk.after_op, RREC_OP_REBOOT);
	zassert_equal(fk.after_st, RREC_ST_OK);
	zassert_equal(fk.after_tag, 0x77u);
	zassert_equal(fk.after_packets, 1u, "the response packet was in the log when the reboot request ran");
	/* the host stops reading: the send times out, the response is not handed over, no reboot request */
	fake_reset();
	rhw_sim_usb_host_stop(true);
	host_send(RREC_OP_REBOOT, 0x78, NULL, 0);
	k_msleep(CONFIG_RING_XFER_SEND_TIMEOUT_MS + 100);
	zassert_equal(fk.after_calls, 0u, "no reboot for an OK that never left");
	zassert_false(rxf_busy());
	rhw_sim_usb_host_stop(false);
	/* FW_END the same */
	host_send(RREC_OP_FW_END, 0x79, NULL, 0);
	zassert_equal(host_get(rsp, sizeof(rsp), 30), 16u);
	k_msleep(2);
	zassert_equal(fk.after_op, RREC_OP_FW_END);
}

/* rxf_start refuses a backend with a missing function */
ZTEST(xfer_svc, test_start_checks_backend)
{
	struct rxf_backend b = *fake_be();

	zassert_equal(rxf_start(NULL, NULL), -EINVAL);
	b.read_chunk = NULL;
	zassert_equal(rxf_start(&b, NULL), -EINVAL);
	b = *fake_be();
	zassert_equal(rxf_start(&b, NULL), 0, "no callbacks is allowed");
	vbus_on();
	rhw_sim_usb_event(RHW_USB_CONFIGURED);
	k_msleep(2);
	zassert_equal(conf_n, 0u);
}
