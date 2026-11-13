/*
 * The scanner of the ship beacon test (BabbleSim, see run.sh): a stand-in for the jig, which "receives the ship beacon
 * while VBUS is on, sees it stop within 1 s of removing VBUS, and sees none for 60 s" (design/firmware.md l.1034, l.1035,
 * l.1057) and sees the radio test's advertising (l.1031). A passive scan, no connection. It shares no constant with the
 * code under test: every number below is written out from the specification.
 *
 * The ring's script (simulated ms): 2,000 SHIP_ENTER, 8,000 VBUS removed, 70,000 T-RADIO for 10 s. The scanner evaluates at
 * 86,000.
 * Output: "HOST CHECK <name> PASS|FAIL", "HOST BEACON NAME <name>", one "HOST RESULT PASS|FAIL".
 */
#include <stdlib.h>
#include <string.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#define SHIP_AT_MS 2000
#define VBUS_OFF_AT_MS 8000
#define RADIO_AT_MS 70000
#define RADIO_MS 10000
#define EVAL_AT_MS 86000

/* Bluetooth Core: advertising report event types */
#define ADV_IND 0x00
#define ADV_DIRECT_IND 0x01
#define ADV_SCAN_IND 0x02
#define ADV_NONCONN_IND 0x03
#define AD_NAME_COMPLETE 0x09

#define MAX_REPORTS 2048

struct report {
	int64_t t;
	uint8_t type;
	char name[24];
};
static struct report reps[MAX_REPORTS];
static volatile int nrep;
static int fails;
static int checks;

#define CHECK(label, cond)                                                                            \
	do {                                                                                          \
		bool ok_ = (cond);                                                                    \
		checks++;                                                                             \
		fails += ok_ ? 0 : 1;                                                                 \
		printk("HOST CHECK %s %s (t=%lld)\n", label, ok_ ? "PASS" : "FAIL", k_uptime_get()); \
	} while (0)

static bool name_cb(struct bt_data *d, void *user)
{
	char *dst = user;

	if (d->type == AD_NAME_COMPLETE) {
		size_t n = d->data_len < 23 ? d->data_len : 23;

		memcpy(dst, d->data, n);
		dst[n] = '\0';
		return false;
	}
	return true;
}

static void scan_cb(const bt_addr_le_t *addr, int8_t rssi, uint8_t type, struct net_buf_simple *ad)
{
	ARG_UNUSED(addr);
	ARG_UNUSED(rssi);
	if (nrep < MAX_REPORTS) {
		struct report *r = &reps[nrep];

		r->t = k_uptime_get();
		r->type = type;
		memset(r->name, 0, sizeof(r->name));
		bt_data_parse(ad, name_cb, r->name);
		nrep++;
	}
}

static int count_in(int64_t from, int64_t to) /* reports with from <= t <= to */
{
	int c = 0;

	for (int i = 0; i < nrep; i++) {
		c += (reps[i].t >= from && reps[i].t <= to);
	}
	return c;
}

static int count_not_nonconn(void)
{
	int c = 0;

	for (int i = 0; i < nrep; i++) {
		c += (reps[i].type != ADV_NONCONN_IND);
	}
	return c;
}

static bool name_ok(const char *s)
{
	if (strlen(s) != 8 || strncmp(s, "Ring", 4) != 0) {
		return false;
	}
	for (int i = 4; i < 8; i++) {
		char c = s[i];

		if (!((c >= '0' && c <= '9') || (c >= 'A' && c <= 'F'))) {
			return false;
		}
	}
	return true;
}

static int cmp_i64(const void *a, const void *b)
{
	int64_t x = *(const int64_t *)a;
	int64_t y = *(const int64_t *)b;

	return (x > y) - (x < y);
}

int main(void)
{
	struct bt_le_scan_param sp = {
		.type = BT_LE_SCAN_TYPE_PASSIVE,
		.options = BT_LE_SCAN_OPT_NONE,
		.interval = 0x0060,
		.window = 0x0060, /* a continuous scan */
	};
	int err = bt_enable(NULL);

	CHECK("bt_enable", err == 0);
	err = bt_le_scan_start(&sp, scan_cb);
	CHECK("scan started", err == 0);

	k_sleep(K_MSEC(EVAL_AT_MS - k_uptime_get()));
	int n = nrep;

	printk("HOST REPORTS %d\n", n);
	CHECK("heard the ring", n > 0);
	/* nothing before the command */
	CHECK("silent before SHIP_ENTER", count_in(0, SHIP_AT_MS - 1) == 0);
	/* the beacon: it starts at once, 100 ms interval */
	int first = -1;

	for (int i = 0; i < n; i++) {
		if (reps[i].t >= SHIP_AT_MS) {
			first = i;
			break;
		}
	}
	CHECK("beacon starts within 300 ms of the command", first >= 0 && reps[first].t - SHIP_AT_MS < 300);
	CHECK("beacon heard while VBUS is on (at least 40 reports in 6 s)", count_in(SHIP_AT_MS, VBUS_OFF_AT_MS) >= 40);
	if (first >= 0) {
		printk("HOST BEACON NAME %s\n", reps[first].name);
		CHECK("name is Ring and 4 upper case hex digits", name_ok(reps[first].name));
		bool same = true;

		for (int i = 0; i < n; i++) {
			same &= (strcmp(reps[i].name, reps[first].name) == 0);
		}
		CHECK("the same name in every report", same);
	}
	/* not connectable: every report is ADV_NONCONN_IND */
	CHECK("every report is not connectable (ADV_NONCONN_IND)", count_not_nonconn() == 0);
	/* the interval: median gap of the first window between 95 and 125 ms */
	{
		static int64_t gaps[MAX_REPORTS];
		int ng = 0;
		int64_t prev = -1;

		for (int i = 0; i < n; i++) {
			if (reps[i].t >= SHIP_AT_MS && reps[i].t <= VBUS_OFF_AT_MS) {
				if (prev >= 0) {
					gaps[ng++] = reps[i].t - prev;
				}
				prev = reps[i].t;
			}
		}
		int64_t med = 0;

		if (ng > 0) {
			qsort(gaps, ng, sizeof(gaps[0]), cmp_i64);
			med = gaps[ng / 2];
		}
		printk("HOST MEDIAN GAP %lld ms of %d\n", med, ng);
		CHECK("interval about 100 ms (median gap 95 to 125 ms)", ng >= 30 && med >= 95 && med <= 125);
	}
	/* stops within 1 s of the removal and stays off for 60 s */
	CHECK("stopped within 1 s of VBUS removal", count_in(VBUS_OFF_AT_MS + 1000 + 1, VBUS_OFF_AT_MS + 2000) == 0);
	CHECK("none for 60 s after the removal", count_in(VBUS_OFF_AT_MS + 1000 + 1, VBUS_OFF_AT_MS + 60000) == 0);
	/* the radio test: about 10 s of advertising, then none */
	CHECK("radio test heard for 10 s (at least 80 reports)", count_in(RADIO_AT_MS, RADIO_AT_MS + RADIO_MS) >= 80);
	CHECK("radio test stops with the test", count_in(RADIO_AT_MS + RADIO_MS + 300, EVAL_AT_MS) == 0);
	printk("HOST RESULT %s (%d checks)\n", fails == 0 ? "PASS" : "FAIL", checks);
	for (;;) {
		k_sleep(K_SECONDS(10));
	}
	return 0;
}
