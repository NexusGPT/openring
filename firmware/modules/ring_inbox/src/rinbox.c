/* Ring inbox: see rinbox.h. */

#include <errno.h>
#include <string.h>

#include <ring_inbox/rinbox.h>

static size_t seq_len(uint8_t lead)
{
	if (lead >= 0xC2 && lead <= 0xDF) {
		return 2;
	}
	if (lead >= 0xE0 && lead <= 0xEF) {
		return 3;
	}
	if (lead >= 0xF0 && lead <= 0xF4) {
		return 4;
	}
	return 1;
}

static bool is_cont(uint8_t c)
{
	return (c & 0xC0) == 0x80;
}

size_t rinbox_utf8_cut(const char *s, size_t len, size_t max)
{
	const uint8_t *p = (const uint8_t *)s;
	size_t n = len < max ? len : max;
	size_t back = 0;
	size_t j;

	if (p == NULL) {
		return 0;
	}
	/* the cut falls inside a character: the byte after the cut is a continuation byte */
	if (n < len) {
		while (n > 0 && is_cont(p[n])) {
			n--;
		}
	}
	/* the prefix ends with an incomplete character (the sender cut it): drop that character */
	j = n;
	while (j > 0 && back < 3 && is_cont(p[j - 1])) {
		j--;
		back++;
	}
	if (j > 0) {
		size_t k = j - 1; /* the byte before the continuation bytes */

		if (seq_len(p[k]) > 1 && k + seq_len(p[k]) > n) {
			n = k;
		}
	}
	return n;
}

static void put(char *dst, size_t cap, const char *src, size_t len)
{
	size_t n = 0;

	if (src != NULL) {
		/* a NUL inside the data ends the string */
		size_t m = 0;

		while (m < len && src[m] != '\0') {
			m++;
		}
		n = rinbox_utf8_cut(src, m, cap);
		memcpy(dst, src, n);
	}
	dst[n] = '\0';
}

void rinbox_init(struct rinbox *b)
{
	memset(b, 0, sizeof(*b));
}

void rinbox_clear(struct rinbox *b)
{
	rinbox_init(b);
}

uint8_t rinbox_count(const struct rinbox *b)
{
	return b->count;
}

const struct rinbox_item *rinbox_get(const struct rinbox *b, uint8_t index)
{
	return index < b->count ? &b->items[index] : NULL;
}

int rinbox_find(const struct rinbox *b, uint32_t uid)
{
	for (uint8_t i = 0; i < b->count; i++) {
		if (b->items[i].uid == uid) {
			return i;
		}
	}
	return -1;
}

static void shift_down(struct rinbox *b, uint8_t from, uint8_t to)
{
	/* move items[from..to-1] to items[from+1..to] */
	for (int i = to; i > from; i--) {
		b->items[i] = b->items[i - 1];
	}
}

int rinbox_add(struct rinbox *b, uint32_t uid, uint8_t category, uint8_t flags, uint32_t *dropped)
{
	int at = rinbox_find(b, uid);
	int did_drop = 0;

	if (at >= 0) {
		/* known id: the entry is replaced and becomes the newest */
		shift_down(b, 0, (uint8_t)at);
	} else if (b->count == RINBOX_MAX) {
		if (dropped != NULL) {
			*dropped = b->items[RINBOX_MAX - 1].uid;
		}
		did_drop = 1;
		shift_down(b, 0, RINBOX_MAX - 1);
	} else {
		shift_down(b, 0, b->count);
		b->count++;
	}
	memset(&b->items[0], 0, sizeof(b->items[0]));
	b->items[0].uid = uid;
	b->items[0].category = category;
	b->items[0].flags = flags & RINBOX_F_MASK;
	return did_drop;
}

int rinbox_modify(struct rinbox *b, uint32_t uid, uint8_t category, uint8_t flags)
{
	int at = rinbox_find(b, uid);

	if (at < 0) {
		return -ENOENT;
	}
	b->items[at].category = category;
	b->items[at].flags = flags & RINBOX_F_MASK;
	return 0;
}

int rinbox_set_text(struct rinbox *b, uint32_t uid, const char *app, size_t app_len, const char *title,
		    size_t title_len, const char *msg, size_t msg_len, const char *date, size_t date_len)
{
	int at = rinbox_find(b, uid);
	struct rinbox_item *it;

	if (at < 0) {
		return -ENOENT;
	}
	it = &b->items[at];
	put(it->app, RINBOX_APP_MAX, app, app_len);
	put(it->title, RINBOX_TITLE_MAX, title, title_len);
	put(it->msg, RINBOX_MSG_MAX, msg, msg_len);
	put(it->date, RINBOX_DATE_MAX, date, date_len);
	it->text_ready = true;
	return 0;
}

int rinbox_upsert(struct rinbox *b, uint32_t uid, uint8_t category, uint8_t flags, const char *app, size_t app_len,
		  const char *title, size_t title_len, const char *msg, size_t msg_len, const char *date, size_t date_len,
		  uint32_t *dropped)
{
	int dropped_one = 0;

	if (rinbox_find(b, uid) >= 0) {
		/* held: the place and the read mark stay */
		(void)rinbox_modify(b, uid, category, flags);
	} else {
		dropped_one = rinbox_add(b, uid, category, flags, dropped);
	}
	(void)rinbox_set_text(b, uid, app, app_len, title, title_len, msg, msg_len, date, date_len);
	return dropped_one;
}

int rinbox_remove(struct rinbox *b, uint32_t uid)
{
	int at = rinbox_find(b, uid);

	if (at < 0) {
		return -ENOENT;
	}
	for (uint8_t i = (uint8_t)at; i + 1 < b->count; i++) {
		b->items[i] = b->items[i + 1];
	}
	b->count--;
	memset(&b->items[b->count], 0, sizeof(b->items[0]));
	return 0;
}

int rinbox_mark_read(struct rinbox *b, uint32_t uid)
{
	int at = rinbox_find(b, uid);

	if (at < 0) {
		return -ENOENT;
	}
	b->items[at].read = true;
	return 0;
}
