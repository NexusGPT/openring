/* ring_iphone logic tests (native_sim and the simulated ring chip, no radio): the request builder,
 * the reassembly of the notification attribute answer, the media decoder. The expected byte strings
 * are written out here from Apple's ANCS specification (Get Notification Attributes) and the kit's
 * encoder (ancs_client.c lines 409-453), not produced by the code under test. */

#include <errno.h>
#include <string.h>

#include <zephyr/ztest.h>

#include <ring_iphone/ripl.h>

ZTEST_SUITE(ring_iphone, NULL, NULL, NULL, NULL, NULL);

/* Build an answer: command 0, uid, then the four tuples (id, length, data) in the order of the request. */
static size_t answer(uint8_t *o, uint32_t uid, const char *app, const char *title, const uint8_t *msg,
		     uint16_t msg_len, const char *date)
{
	size_t n = 0;
	const char *s[4] = { app, title, NULL, date };
	static const uint8_t ids[4] = { 0, 1, 3, 5 };

	o[n++] = 0;
	o[n++] = (uint8_t)uid;
	o[n++] = (uint8_t)(uid >> 8);
	o[n++] = (uint8_t)(uid >> 16);
	o[n++] = (uint8_t)(uid >> 24);
	for (int i = 0; i < 4; i++) {
		uint16_t l = (i == 2) ? msg_len : (uint16_t)strlen(s[i]);

		o[n++] = ids[i];
		o[n++] = (uint8_t)l;
		o[n++] = (uint8_t)(l >> 8);
		memcpy(&o[n], i == 2 ? (const char *)msg : s[i], l);
		n += l;
	}
	return n;
}

ZTEST(ring_iphone, test_request_bytes)
{
	uint8_t r[RIPL_REQ_LEN + 2];
	static const uint8_t want[13] = {
		0x00,                   /* CommandIDGetNotificationAttributes */
		0x04, 0x03, 0x02, 0x01, /* notification uid 0x01020304, little endian */
		0x00,                   /* AppIdentifier */
		0x01, 0x30, 0x00,       /* Title, max length 48 */
		0x03, 0xA0, 0x00,       /* Message, max length 160 */
		0x05,                   /* Date */
	};

	memset(r, 0xEE, sizeof(r));
	zassert_equal(ripl_build_get_attrs(r, 0x01020304), 13);
	zassert_mem_equal(r, want, 13);
	zassert_equal(r[13], 0xEE, "nothing written past the request");
}

ZTEST(ring_iphone, test_ds_whole)
{
	uint8_t a[300];
	struct ripl_ds d;
	size_t n = answer(a, 0xA1B2C3D4, "com.apple.MobileSMS", "Anna", (const uint8_t *)"Hello there", 11, "20261111T220546");

	ripl_ds_start(&d, 0xA1B2C3D4);
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_DONE);
	zassert_str_equal(d.app, "com.apple.MobileSMS");
	zassert_str_equal(d.title, "Anna");
	zassert_str_equal(d.msg, "Hello there");
	zassert_str_equal(d.date, "20261111T220546");
	zassert_equal(d.kept[0], 19);
	zassert_equal(d.kept[2], 11);
}

ZTEST(ring_iphone, test_ds_every_fragment_size)
{
	uint8_t a[300];
	size_t n = answer(a, 7, "com.example.app", "Title", (const uint8_t *)"The message text", 16, "20260102T030405");

	for (size_t frag = 1; frag <= n; frag++) {
		struct ripl_ds d;
		enum ripl_ds_result r = RIPL_DS_MORE;
		size_t i = 0;

		ripl_ds_start(&d, 7);
		while (i < n) {
			size_t k = MIN(frag, n - i);

			zassert_equal(r, RIPL_DS_MORE, "frag %zu: done too early at byte %zu", frag, i);
			r = ripl_ds_feed(&d, &a[i], k);
			i += k;
		}
		zassert_equal(r, RIPL_DS_DONE, "frag %zu", frag);
		zassert_str_equal(d.app, "com.example.app", "frag %zu", frag);
		zassert_str_equal(d.title, "Title");
		zassert_str_equal(d.msg, "The message text");
		zassert_str_equal(d.date, "20260102T030405");
	}
}

ZTEST(ring_iphone, test_ds_empty_notification_ok)
{
	uint8_t a[100];
	struct ripl_ds d;
	size_t n = answer(a, 1, "x.y", "", (const uint8_t *)"", 0, "");

	ripl_ds_start(&d, 1);
	zassert_equal(ripl_ds_feed(&d, a, 0), RIPL_DS_MORE, "an empty fragment changes nothing");
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_DONE);
	zassert_str_equal(d.app, "x.y");
	zassert_str_equal(d.title, "");
	zassert_str_equal(d.msg, "");
	zassert_str_equal(d.date, "");
}

/* The sender sends more than the limit (a sender that ignores the max length): the rest is skipped and the
 * next attribute is read from the right place. */
ZTEST(ring_iphone, test_ds_longer_than_limit_is_skipped)
{
	uint8_t a[400];
	uint8_t msg[200];
	struct ripl_ds d;
	size_t n;

	memset(msg, 'm', sizeof(msg));
	n = answer(a, 9, "com.long.app", "A title", msg, 200, "20261111T220546");
	ripl_ds_start(&d, 9);
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_DONE);
	zassert_equal(strlen(d.msg), 160, "the first 160 bytes are kept");
	zassert_str_equal(d.date, "20261111T220546", "the date after the long message is intact");
}

ZTEST(ring_iphone, test_ds_app_identifier_longer_than_48_is_kept_to_48)
{
	uint8_t a[300];
	struct ripl_ds d;
	char app[80];
	size_t n;

	memset(app, 'p', sizeof(app) - 1);
	app[79] = '\0';
	n = answer(a, 3, app, "T", (const uint8_t *)"M", 1, "D");
	ripl_ds_start(&d, 3);
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_DONE);
	zassert_equal(strlen(d.app), 48);
	zassert_str_equal(d.title, "T");
}

ZTEST(ring_iphone, test_ds_errors)
{
	uint8_t a[100];
	struct ripl_ds d;
	size_t n = answer(a, 5, "a", "b", (const uint8_t *)"c", 1, "d");

	/* attributes out of the requested order, in an answer to this id: swap the ids of title and message */
	a[5 + 3 + 1] = 3; /* the title tuple starts at 5 + (1+2+1) = 9 */
	ripl_ds_start(&d, 5);
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_ERROR);
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_ERROR, "stays an error");
}

/* A late answer of a request that was given up: it is skipped, whole or in any fragments, and the answer to the
 * current request that follows (or comes in between) is read correctly. */
ZTEST(ring_iphone, test_ds_late_answer_of_another_request_is_skipped)
{
	uint8_t stale[200], good[200];
	size_t ns = answer(stale, 6, "stale.app", "Stale title", (const uint8_t *)"stale message", 13, "20260101T000000");
	size_t ng = answer(good, 5, "good.app", "Good", (const uint8_t *)"good message", 12, "20261111T220546");

	for (size_t frag = 1; frag <= ns + ng; frag++) {
		uint8_t all[400];
		struct ripl_ds d;
		enum ripl_ds_result r = RIPL_DS_MORE;

		memcpy(all, stale, ns);
		memcpy(all + ns, good, ng);
		ripl_ds_start(&d, 5);
		for (size_t i = 0; i < ns + ng; i += frag) {
			size_t k = MIN(frag, ns + ng - i);

			zassert_equal(r, RIPL_DS_MORE, "frag %zu: done before the right answer ended", frag);
			r = ripl_ds_feed(&d, &all[i], k);
		}
		zassert_equal(r, RIPL_DS_DONE, "frag %zu", frag);
		zassert_str_equal(d.app, "good.app", "frag %zu", frag);
		zassert_str_equal(d.title, "Good");
		zassert_str_equal(d.msg, "good message");
		zassert_str_equal(d.date, "20261111T220546");
		zassert_true(d.skipped > 0, "the stale answer was skipped");
	}
	/* a stale answer that ends with a zero byte just before the good one starts: the four bytes read as an id must be
	 * searched again, so the good header is not swallowed */
	{
		uint8_t st2[40], all[400];
		struct ripl_ds d;
		size_t m = answer(st2, 7, "", "", (const uint8_t *)"", 0, ""); /* ends with 05 00 00 */

		memcpy(all, st2, m);
		memcpy(all + m, good, ng);
		ripl_ds_start(&d, 5);
		zassert_equal(ripl_ds_feed(&d, all, m + ng), RIPL_DS_DONE);
		zassert_str_equal(d.msg, "good message");
	}
	/* a stale answer that ends with the bytes 05 00 00 and so makes, with the first byte of ours, a header for id 5 whose
	 * first attribute is wrong: it is a false header, ours is found after it */
	{
		uint8_t st3[40], all[400];
		struct ripl_ds d;
		size_t m = answer(st3, 7, "", "", (const uint8_t *)"", 0, "");

		memcpy(all, st3, m);
		memcpy(all + m, good, ng);
		ripl_ds_start(&d, 5);
		zassert_equal(ripl_ds_feed(&d, all, m + ng), RIPL_DS_DONE);
		zassert_str_equal(d.title, "Good");
	}
	/* only a stale answer: never done */
	{
		struct ripl_ds d;

		ripl_ds_start(&d, 5);
		zassert_equal(ripl_ds_feed(&d, stale, ns), RIPL_DS_MORE);
	}
	/* the middle of a stale answer (the header went to the request that was given up): skipped too */
	{
		struct ripl_ds d;
		uint8_t all[400];

		memcpy(all, stale + 9, ns - 9);
		memcpy(all + ns - 9, good, ng);
		ripl_ds_start(&d, 5);
		zassert_equal(ripl_ds_feed(&d, all, ns - 9 + ng), RIPL_DS_DONE);
		zassert_str_equal(d.msg, "good message");
	}
	/* another command id (1 = app attributes) is not an answer to this request: skipped */
	{
		struct ripl_ds d;

		good[0] = 1;
		ripl_ds_start(&d, 5);
		zassert_equal(ripl_ds_feed(&d, good, ng), RIPL_DS_MORE);
	}
}

ZTEST(ring_iphone, test_ds_ignores_bytes_after_the_end)
{
	uint8_t a[100];
	struct ripl_ds d;
	size_t n = answer(a, 5, "a", "b", (const uint8_t *)"c", 1, "d");

	a[n] = 0xFF;
	ripl_ds_start(&d, 5);
	zassert_equal(ripl_ds_feed(&d, a, n + 1), RIPL_DS_DONE);
	zassert_equal(ripl_ds_feed(&d, a, n), RIPL_DS_DONE);
	zassert_str_equal(d.msg, "c");
}

ZTEST(ring_iphone, test_media_starts_unknown)
{
	struct ripl_media m;

	ripl_media_init(&m);
	zassert_equal(m.state, RIPL_PLAYER_UNKNOWN);
	zassert_str_equal(m.title, "");
	zassert_str_equal(m.artist, "");
}

ZTEST(ring_iphone, test_media_playback_state)
{
	struct ripl_media m;
	static const uint8_t play[] = "1,1.0,0.014";
	static const uint8_t pause[] = "0,0.0,0.000";
	static const uint8_t rew[] = "2,-2.0,10.000";
	static const uint8_t bad[] = "x,1.0,0.0";

	ripl_media_init(&m);
	zassert_equal(ripl_media_apply(&m, 0, 1, play, sizeof(play) - 1), 1);
	zassert_equal(m.state, RIPL_PLAYER_PLAYING);
	zassert_equal(ripl_media_apply(&m, 0, 1, pause, sizeof(pause) - 1), 1);
	zassert_equal(m.state, RIPL_PLAYER_PAUSED);
	zassert_equal(ripl_media_apply(&m, 0, 1, rew, sizeof(rew) - 1), -ENOTSUP);
	zassert_equal(m.state, RIPL_PLAYER_PAUSED, "a state the ring does not store changes nothing");
	zassert_equal(ripl_media_apply(&m, 0, 1, bad, sizeof(bad) - 1), -EINVAL);
	zassert_equal(m.state, RIPL_PLAYER_PAUSED);
	zassert_equal(ripl_media_apply(&m, 0, 1, (const uint8_t *)"1", 1), 1, "state alone");
	zassert_equal(m.state, RIPL_PLAYER_PLAYING);
	zassert_equal(ripl_media_apply(&m, 0, 1, (const uint8_t *)"", 0), -EINVAL);
}

ZTEST(ring_iphone, test_media_track_text)
{
	struct ripl_media m;
	uint8_t long_title[100];

	ripl_media_init(&m);
	zassert_equal(ripl_media_apply(&m, 2, 2, (const uint8_t *)"Bohemian Rhapsody", 17), 1);
	zassert_equal(ripl_media_apply(&m, 2, 0, (const uint8_t *)"Queen", 5), 1);
	zassert_str_equal(m.title, "Bohemian Rhapsody");
	zassert_str_equal(m.artist, "Queen");
	zassert_equal(m.state, RIPL_PLAYER_UNKNOWN, "a track report does not touch the player state");
	zassert_equal(ripl_media_apply(&m, 2, 2, (const uint8_t *)"", 0), 1, "an empty title clears it");
	zassert_str_equal(m.title, "");
	/* not stored: album (1), duration (3), the queue entity, the player name */
	zassert_equal(ripl_media_apply(&m, 2, 1, (const uint8_t *)"Album", 5), 0);
	zassert_equal(ripl_media_apply(&m, 2, 3, (const uint8_t *)"120.0", 5), 0);
	zassert_equal(ripl_media_apply(&m, 1, 0, (const uint8_t *)"1", 1), 0);
	zassert_equal(ripl_media_apply(&m, 0, 0, (const uint8_t *)"Music", 5), 0);
	zassert_str_equal(m.artist, "Queen");
	memset(long_title, 'T', sizeof(long_title));
	zassert_equal(ripl_media_apply(&m, 2, 2, long_title, 100), 1);
	zassert_equal(strlen(m.title), 64);
	zassert_equal(ripl_media_apply(&m, 2, 0, long_title, 100), 1);
	zassert_equal(strlen(m.artist), 48);
}

ZTEST(ring_iphone, test_media_text_cut_on_a_character)
{
	struct ripl_media m;
	uint8_t t[70];
	size_t i = 0;

	ripl_media_init(&m);
	t[i++] = 'a';
	for (int k = 0; k < 21; k++) { /* 1 + 63 = 64 bytes, then one more 3-byte character */
		t[i++] = 0xE2;
		t[i++] = 0x82;
		t[i++] = 0xAC;
	}
	t[i++] = 0xE2;
	t[i++] = 0x82;
	t[i++] = 0xAC;
	zassert_equal(i, 67);
	zassert_equal(ripl_media_apply(&m, 2, 2, t, i), 1);
	zassert_equal(strlen(m.title), 64, "21 characters and the 'a': 64 bytes, the 22nd character does not fit");
}

ZTEST(ring_iphone, test_cts_to_ms)
{
	int64_t ms = 0;

	zassert_true(ripl_cts_to_ms(2026, 11, 11, 22, 5, 46, 0, &ms));
	zassert_equal(ms, 1794434746000LL);
	zassert_false(ripl_cts_to_ms(2026, 13, 11, 22, 5, 46, 0, &ms));
	zassert_false(ripl_cts_to_ms(0, 0, 0, 0, 0, 0, 0, &ms), "year 0 (unknown) is not a time");
}

ZTEST(ring_iphone, test_cts_zone)
{
	int16_t m = 77;

	zassert_true(ripl_cts_zone(4, 0, &m));
	zassert_equal(m, 60, "+1 h, standard time");
	zassert_true(ripl_cts_zone(4, 4, &m));
	zassert_equal(m, 120, "+1 h and daylight saving +1 h");
	zassert_true(ripl_cts_zone(-20, 2, &m));
	zassert_equal(m, -270, "-5 h and +0.5 h");
	zassert_true(ripl_cts_zone(0, 0, &m));
	zassert_equal(m, 0);
	zassert_true(ripl_cts_zone(56, 8, &m));
	zassert_equal(m, 960);
	m = 77;
	zassert_false(ripl_cts_zone(-128, 0, &m), "zone unknown");
	zassert_false(ripl_cts_zone(4, 255, &m), "daylight offset unknown");
	zassert_false(ripl_cts_zone(57, 0, &m), "out of range");
	zassert_false(ripl_cts_zone(-49, 0, &m), "out of range");
	zassert_false(ripl_cts_zone(4, 3, &m), "not a defined daylight code");
	zassert_equal(m, 77, "nothing is written when not known");
}

/* The clock from the iPhone's time and zone. Time notification i arrives at uptime 1000 + 5000 i and says that the
 * iPhone's local time is (a base + 5000 i) ms; the zone read of each notification returns 37 ms to 400 ms later. The clock
 * must then say, at every moment, exactly local time - zone, whatever the delay: no drift (1 ms) over 100 notifications. */
ZTEST(ring_iphone, test_clock_no_drift_with_delayed_zone_read)
{
	struct ripl_clock c;
	struct rtime_rec r;
	const int64_t base = 1794434746000LL;
	const int16_t zone = 120;

	ripl_clock_init(&c);
	rtime_rec_init(&r);
	/* the first zone read */
	ripl_clock_time(&c, base, 1000);
	ripl_clock_zone(&c, true, true, zone, 1100);
	zassert_true(ripl_clock_apply(&c, &r));
	for (int i = 0; i < 100; i++) {
		int64_t up = 1000 + 5000LL * i;
		int64_t local = base + 5000LL * i;
		int64_t delay = 37 + (i * 37) % 364;

		ripl_clock_time(&c, local, up);
		zassert_true(ripl_clock_apply(&c, &r));
		/* the zone read comes back `delay` ms later, the same zone: it is applied to the arrival moment */
		ripl_clock_zone(&c, true, true, zone, up + delay);
		zassert_true(ripl_clock_apply(&c, &r));
		zassert_equal(rtime_rec_utc_ms(&r, up + delay), local - zone * 60000LL + delay,
			      "notification %d: the clock moved by the zone read (delay %lld)", i, delay);
		zassert_equal(rtime_rec_utc_ms(&r, up + 4999), local - zone * 60000LL + 4999, "i=%d", i);
	}
	zassert_true(r.zone_known);
	zassert_equal(r.tz_min, zone);
}

ZTEST(ring_iphone, test_clock_failed_zone_read_keeps_the_last_zone)
{
	struct ripl_clock c;
	struct rtime_rec r;

	ripl_clock_init(&c);
	rtime_rec_init(&r);
	ripl_clock_time(&c, 1794434746000LL, 1000);
	ripl_clock_zone(&c, true, true, 120, 1100);
	zassert_true(ripl_clock_apply(&c, &r));
	zassert_true(r.zone_known);
	/* a later notification, then a zone read that fails (error or wrong length) */
	ripl_clock_time(&c, 1794434751000LL, 6000);
	ripl_clock_zone(&c, false, false, 0, 6100);
	zassert_equal(c.zone_errors, 1);
	zassert_true(ripl_clock_apply(&c, &r));
	zassert_true(r.zone_known, "one failed read does not turn a UTC clock into local time");
	zassert_equal(r.tz_min, 120);
	zassert_equal(rtime_rec_utc_ms(&r, 6000), 1794434751000LL - 7200000LL);
	/* a read that returned the unknown values does turn it into local time */
	ripl_clock_zone(&c, true, false, 0, 6200);
	zassert_true(ripl_clock_apply(&c, &r));
	zassert_false(r.zone_known);
	zassert_equal(rtime_rec_utc_ms(&r, 6000), 1794434751000LL);
	/* a new link: nothing is kept */
	ripl_clock_init(&c);
	zassert_false(ripl_clock_apply(&c, &r), "no time yet");
}

/* The false header with notification id 0: a stale answer that ends with an empty date (05 00 00) followed by an answer to id 0
 * reads as a header (00, id 0, attribute 0, length 0) and then goes wrong. The parser cannot tell this from a real header
 * without keeping the whole answer (about 300 bytes) to read it again; it ends in an error (or, with other length bytes, a
 * timeout), and the ring then asks again with a fresh parser state: the cost is one retry (at most the 3 s timeout). This test shows both halves: the stream is not completed, and a fresh start on the
 * same bytes of the retry's answer is. */
ZTEST(ring_iphone, test_false_header_with_id_zero_recovers_by_retry)
{
	uint8_t stale[40], good[100], all[200];
	struct ripl_ds d;
	size_t ns = answer(stale, 7, "", "", (const uint8_t *)"", 0, ""); /* ends 05 00 00 */
	size_t ng = answer(good, 0, "good.app", "Good", (const uint8_t *)"good message", 12, "20261111T220546");

	memcpy(all, stale, ns);
	memcpy(all + ns, good, ng);
	ripl_ds_start(&d, 0);
	/* not completed with the right text: either still waiting or wrong, never the good text */
	zassert_not_equal(ripl_ds_feed(&d, all, ns + ng), RIPL_DS_DONE, "known limit: the false header spoils it");
	zassert_not_equal(strcmp(d.msg, "good message"), 0);
	/* the retry: a fresh parser state and the answer alone */
	ripl_ds_start(&d, 0);
	zassert_equal(ripl_ds_feed(&d, good, ng), RIPL_DS_DONE);
	zassert_str_equal(d.msg, "good message");
}
