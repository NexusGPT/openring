/* ring_inbox logic tests (native_sim and the simulated ring chip, no radio). */

#include <errno.h>
#include <string.h>

#include <zephyr/ztest.h>

#include <ring_inbox/rinbox.h>

static struct rinbox b;

static void before(void *f)
{
	ARG_UNUSED(f);
	rinbox_init(&b);
}

ZTEST_SUITE(ring_inbox, NULL, NULL, before, NULL, NULL);

static void add_text(uint32_t uid, const char *app, const char *title, const char *msg, const char *date)
{
	zassert_equal(rinbox_set_text(&b, uid, app, strlen(app), title, strlen(title), msg, strlen(msg), date,
				      strlen(date)),
		      0);
}

ZTEST(ring_inbox, test_sizes_are_the_rule)
{
	zassert_equal(RINBOX_MAX, 16);
	zassert_equal(RINBOX_APP_MAX, 48);
	zassert_equal(RINBOX_TITLE_MAX, 48);
	zassert_equal(RINBOX_MSG_MAX, 160);
}

ZTEST(ring_inbox, test_empty_at_start)
{
	zassert_equal(rinbox_count(&b), 0);
	zassert_is_null(rinbox_get(&b, 0));
	zassert_equal(rinbox_find(&b, 1), -1);
}

ZTEST(ring_inbox, test_add_newest_first)
{
	uint32_t dropped = 99;

	zassert_equal(rinbox_add(&b, 10, 4, RINBOX_F_NEGATIVE, &dropped), 0);
	zassert_equal(rinbox_add(&b, 20, 6, RINBOX_F_POSITIVE | RINBOX_F_NEGATIVE | RINBOX_F_IMPORTANT, &dropped), 0);
	zassert_equal(rinbox_add(&b, 30, 1, RINBOX_F_SILENT | RINBOX_F_PREEXISTING, &dropped), 0);
	zassert_equal(dropped, 99, "nothing was dropped, the out value is left alone");
	zassert_equal(rinbox_count(&b), 3);
	zassert_equal(rinbox_get(&b, 0)->uid, 30, "newest first");
	zassert_equal(rinbox_get(&b, 1)->uid, 20);
	zassert_equal(rinbox_get(&b, 2)->uid, 10);
	zassert_equal(rinbox_get(&b, 1)->category, 6);
	zassert_equal(rinbox_get(&b, 1)->flags, RINBOX_F_POSITIVE | RINBOX_F_NEGATIVE | RINBOX_F_IMPORTANT);
	zassert_equal(rinbox_get(&b, 0)->flags, RINBOX_F_SILENT | RINBOX_F_PREEXISTING);
	zassert_false(rinbox_get(&b, 0)->read);
	zassert_false(rinbox_get(&b, 0)->text_ready);
}

ZTEST(ring_inbox, test_flag_bits_are_apples)
{
	zassert_equal(RINBOX_F_SILENT, 0x01);
	zassert_equal(RINBOX_F_IMPORTANT, 0x02);
	zassert_equal(RINBOX_F_PREEXISTING, 0x04);
	zassert_equal(RINBOX_F_POSITIVE, 0x08);
	zassert_equal(RINBOX_F_NEGATIVE, 0x10);
	/* bits above the five are not stored */
	zassert_equal(rinbox_add(&b, 1, 0, 0xFF, NULL), 0);
	zassert_equal(rinbox_get(&b, 0)->flags, 0x1F);
}

ZTEST(ring_inbox, test_full_drops_oldest)
{
	uint32_t dropped = 0;

	for (uint32_t i = 1; i <= 16; i++) {
		zassert_equal(rinbox_add(&b, i, 0, 0, &dropped), 0, "no drop up to 16 (%u)", i);
	}
	zassert_equal(rinbox_count(&b), 16);
	zassert_equal(rinbox_get(&b, 15)->uid, 1, "the oldest is last");
	zassert_equal(rinbox_add(&b, 17, 0, 0, &dropped), 1, "the 17th drops one");
	zassert_equal(dropped, 1, "the oldest (id 1) was dropped");
	zassert_equal(rinbox_count(&b), 16);
	zassert_equal(rinbox_get(&b, 0)->uid, 17);
	zassert_equal(rinbox_get(&b, 15)->uid, 2);
	zassert_equal(rinbox_find(&b, 1), -1);
	zassert_equal(rinbox_add(&b, 18, 0, 0, &dropped), 1);
	zassert_equal(dropped, 2);
	zassert_equal(rinbox_get(&b, 15)->uid, 3);
}

ZTEST(ring_inbox, test_add_known_id_moves_front)
{
	uint32_t dropped = 0;

	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_add(&b, 2, 0, 0, NULL), 0);
	zassert_equal(rinbox_add(&b, 3, 0, 0, NULL), 0);
	add_text(1, "a", "b", "c", "d");
	zassert_equal(rinbox_add(&b, 1, 5, RINBOX_F_NEGATIVE, &dropped), 0, "a known id drops nothing");
	zassert_equal(rinbox_count(&b), 3);
	zassert_equal(rinbox_get(&b, 0)->uid, 1);
	zassert_equal(rinbox_get(&b, 1)->uid, 3);
	zassert_equal(rinbox_get(&b, 2)->uid, 2);
	zassert_false(rinbox_get(&b, 0)->text_ready, "the old text is gone");
	zassert_equal(rinbox_get(&b, 0)->category, 5);
}

ZTEST(ring_inbox, test_modify_keeps_place_and_text)
{
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_add(&b, 2, 0, 0, NULL), 0);
	add_text(1, "app.one", "T1", "M1", "20261111T000000");
	zassert_equal(rinbox_modify(&b, 1, 7, RINBOX_F_POSITIVE), 0);
	zassert_equal(rinbox_get(&b, 1)->uid, 1, "the place is kept");
	zassert_equal(rinbox_get(&b, 1)->category, 7);
	zassert_equal(rinbox_get(&b, 1)->flags, RINBOX_F_POSITIVE);
	zassert_str_equal(rinbox_get(&b, 1)->title, "T1");
	zassert_equal(rinbox_modify(&b, 99, 0, 0), -ENOENT);
}

ZTEST(ring_inbox, test_set_text_replaces)
{
	zassert_equal(rinbox_add(&b, 5, 0, 0, NULL), 0);
	add_text(5, "com.apple.MobileSMS", "Anna", "Hello there", "20261111T220546");
	zassert_true(rinbox_get(&b, 0)->text_ready);
	zassert_str_equal(rinbox_get(&b, 0)->app, "com.apple.MobileSMS");
	zassert_str_equal(rinbox_get(&b, 0)->title, "Anna");
	zassert_str_equal(rinbox_get(&b, 0)->msg, "Hello there");
	zassert_str_equal(rinbox_get(&b, 0)->date, "20261111T220546");
	add_text(5, "com.apple.MobileSMS", "Anna", "Changed", "20261111T220600");
	zassert_str_equal(rinbox_get(&b, 0)->msg, "Changed", "the new text replaced the old, nothing is left over");
	zassert_str_equal(rinbox_get(&b, 0)->date, "20261111T220600");
	zassert_equal(rinbox_set_text(&b, 77, "x", 1, "x", 1, "x", 1, "x", 1), -ENOENT);
}

ZTEST(ring_inbox, test_remove)
{
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_add(&b, 2, 0, 0, NULL), 0);
	zassert_equal(rinbox_add(&b, 3, 0, 0, NULL), 0);
	zassert_equal(rinbox_remove(&b, 2), 0);
	zassert_equal(rinbox_count(&b), 2);
	zassert_equal(rinbox_get(&b, 0)->uid, 3);
	zassert_equal(rinbox_get(&b, 1)->uid, 1);
	zassert_equal(rinbox_find(&b, 2), -1);
	zassert_equal(rinbox_remove(&b, 2), -ENOENT);
	zassert_equal(rinbox_remove(&b, 3), 0);
	zassert_equal(rinbox_remove(&b, 1), 0);
	zassert_equal(rinbox_count(&b), 0);
}

ZTEST(ring_inbox, test_mark_read_and_clear)
{
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_mark_read(&b, 1), 0);
	zassert_true(rinbox_get(&b, 0)->read);
	zassert_equal(rinbox_mark_read(&b, 2), -ENOENT);
	rinbox_clear(&b);
	zassert_equal(rinbox_count(&b), 0);
	zassert_equal(rinbox_find(&b, 1), -1);
}

ZTEST(ring_inbox, test_text_limits_ascii)
{
	char app[100], title[100], msg[300];

	memset(app, 'a', sizeof(app));
	memset(title, 't', sizeof(title));
	memset(msg, 'm', sizeof(msg));
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_set_text(&b, 1, app, 100, title, 100, msg, 300, "20261111T220546XXXX", 19), 0);
	zassert_equal(strlen(rinbox_get(&b, 0)->app), 48);
	zassert_equal(strlen(rinbox_get(&b, 0)->title), 48);
	zassert_equal(strlen(rinbox_get(&b, 0)->msg), 160);
	zassert_equal(strlen(rinbox_get(&b, 0)->date), 15);
	zassert_equal(rinbox_get(&b, 0)->msg[159], 'm');
}

ZTEST(ring_inbox, test_text_exactly_at_limit_is_kept)
{
	char msg[160];

	memset(msg, 'x', sizeof(msg));
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_set_text(&b, 1, "a", 1, "t", 1, msg, 160, "d", 1), 0);
	zassert_equal(strlen(rinbox_get(&b, 0)->msg), 160);
}

ZTEST(ring_inbox, test_text_nul_ends_the_string)
{
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_set_text(&b, 1, "ab\0cd", 5, NULL, 0, "x\0y", 3, "", 0), 0);
	zassert_str_equal(rinbox_get(&b, 0)->app, "ab");
	zassert_str_equal(rinbox_get(&b, 0)->title, "");
	zassert_str_equal(rinbox_get(&b, 0)->msg, "x");
}

/* A 200-byte message of three-byte characters: the limit 160 falls inside a character. */
ZTEST(ring_inbox, test_utf8_cut_long_message)
{
	char msg[201];
	const struct rinbox_item *it;
	size_t i = 0;

	for (int k = 0; k < 66; k++) { /* 66 x U+20AC (E2 82 AC) = 198 bytes */
		msg[i++] = (char)0xE2;
		msg[i++] = (char)0x82;
		msg[i++] = (char)0xAC;
	}
	msg[i++] = 'x';
	msg[i++] = 'y';
	zassert_equal(i, 200);
	zassert_equal(rinbox_add(&b, 1, 0, 0, NULL), 0);
	zassert_equal(rinbox_set_text(&b, 1, "a", 1, "t", 1, msg, 200, "d", 1), 0);
	it = rinbox_get(&b, 0);
	zassert_equal(strlen(it->msg), 159, "53 whole characters, not 160 bytes");
	zassert_equal((uint8_t)it->msg[156], 0xE2);
	zassert_equal((uint8_t)it->msg[158], 0xAC);
}

ZTEST(ring_inbox, test_utf8_cut_cases)
{
	/* U+00E9 (C3 A9), U+20AC (E2 82 AC), U+1F600 (F0 9F 98 80) */
	static const char s2[] = "a\xC3\xA9" "b";
	static const char s3[] = "a\xE2\x82\xAC" "b";
	static const char s4[] = "a\xF0\x9F\x98\x80" "b";

	zassert_equal(rinbox_utf8_cut(s2, 4, 4), 4, "fits: unchanged");
	zassert_equal(rinbox_utf8_cut(s2, 4, 3), 3);
	zassert_equal(rinbox_utf8_cut(s2, 4, 2), 1, "inside the two-byte character: before it");
	zassert_equal(rinbox_utf8_cut(s3, 5, 4), 4);
	zassert_equal(rinbox_utf8_cut(s3, 5, 3), 1, "inside the three-byte character");
	zassert_equal(rinbox_utf8_cut(s3, 5, 2), 1);
	zassert_equal(rinbox_utf8_cut(s4, 6, 5), 5);
	zassert_equal(rinbox_utf8_cut(s4, 6, 4), 1);
	zassert_equal(rinbox_utf8_cut(s4, 6, 3), 1);
	zassert_equal(rinbox_utf8_cut(s4, 6, 2), 1);
	zassert_equal(rinbox_utf8_cut(s4, 6, 1), 1);
	zassert_equal(rinbox_utf8_cut(s4, 6, 0), 0);
	zassert_equal(rinbox_utf8_cut("", 0, 10), 0);
	zassert_equal(rinbox_utf8_cut("abc", 3, 160), 3);
	/* the sender cut a character: the data ends inside it */
	zassert_equal(rinbox_utf8_cut("ab\xE2\x82", 4, 160), 2, "an incomplete character at the end is dropped");
	zassert_equal(rinbox_utf8_cut("ab\xE2", 3, 160), 2);
	zassert_equal(rinbox_utf8_cut("ab\xF0\x9F\x98", 5, 160), 2);
}

/* Property: for every length and every limit, the cut is within both, ends on a character boundary
 * and is the longest such prefix. */
ZTEST(ring_inbox, test_utf8_cut_property)
{
	static const char s[] = "a\xC3\xA9" "b\xE2\x82\xAC" "c\xF0\x9F\x98\x80" "d\xC3\xA9\xE2\x82\xAC";
	size_t len = sizeof(s) - 1;
	/* the start offsets of the characters, and the end */
	static const size_t bounds[] = { 0, 1, 3, 4, 7, 8, 12, 13, 15, 18 };

	zassert_equal(len, 18);
	for (size_t l = 0; l <= len; l++) {
		for (size_t m = 0; m <= len + 2; m++) {
			size_t cut = rinbox_utf8_cut(s, l, m);
			size_t best = 0;
			bool on_bound = false;

			for (size_t k = 0; k < ARRAY_SIZE(bounds); k++) {
				if (bounds[k] <= l && bounds[k] <= m && bounds[k] > best) {
					best = bounds[k];
				}
				if (bounds[k] == cut) {
					on_bound = true;
				}
			}
			/* when l itself is not a boundary the data ends inside a character: the best prefix is
			 * the last boundary not after l, which the loop found */
			zassert_true(cut <= l && cut <= m, "l=%zu m=%zu cut=%zu", l, m, cut);
			zassert_true(on_bound, "l=%zu m=%zu cut=%zu is inside a character", l, m, cut);
			zassert_equal(cut, best, "l=%zu m=%zu cut=%zu best=%zu", l, m, cut, best);
		}
	}
}
