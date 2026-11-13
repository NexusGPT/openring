/* Ring iPhone part, pure logic: see ripl.h. */

#include <errno.h>
#include <string.h>

#include <ring_inbox/rinbox.h>
#include <ring_iphone/ripl.h>
#include <ring_time/rtime_logic.h>

size_t ripl_build_get_attrs(uint8_t *buf, uint32_t uid)
{
	size_t n = 0;

	buf[n++] = RIPL_ANCS_CMD_GET_ATTRS;
	buf[n++] = (uint8_t)uid;
	buf[n++] = (uint8_t)(uid >> 8);
	buf[n++] = (uint8_t)(uid >> 16);
	buf[n++] = (uint8_t)(uid >> 24);
	buf[n++] = RIPL_ANCS_ATTR_APP;
	buf[n++] = RIPL_ANCS_ATTR_TITLE;
	buf[n++] = (uint8_t)RIPL_REQ_TITLE_MAX;
	buf[n++] = (uint8_t)(RIPL_REQ_TITLE_MAX >> 8);
	buf[n++] = RIPL_ANCS_ATTR_MESSAGE;
	buf[n++] = (uint8_t)RIPL_REQ_MESSAGE_MAX;
	buf[n++] = (uint8_t)(RIPL_REQ_MESSAGE_MAX >> 8);
	buf[n++] = RIPL_ANCS_ATTR_DATE;
	return n;
}

enum {
	DS_CMD,
	DS_UID,
	DS_ATTR_ID,
	DS_LEN_LO,
	DS_LEN_HI,
	DS_DATA,
	DS_DONE,
	DS_ERR,
};

static const uint8_t attr_order[4] = {
	RIPL_ANCS_ATTR_APP, RIPL_ANCS_ATTR_TITLE, RIPL_ANCS_ATTR_MESSAGE, RIPL_ANCS_ATTR_DATE,
};

void ripl_ds_start(struct ripl_ds *d, uint32_t uid)
{
	memset(d, 0, sizeof(*d));
	d->state = DS_CMD;
	d->uid = uid;
}

uint32_t ripl_ds_uid(const struct ripl_ds *d)
{
	return d->uid;
}

static char *attr_buf(struct ripl_ds *d, size_t *cap)
{
	switch (d->attr) {
	case 0:
		*cap = RIPL_REQ_APP_MAX;
		return d->app;
	case 1:
		*cap = RIPL_REQ_TITLE_MAX;
		return d->title;
	case 2:
		*cap = RIPL_REQ_MESSAGE_MAX;
		return d->msg;
	default:
		*cap = RIPL_REQ_DATE_MAX;
		return d->date;
	}
}

/* The attribute is complete: go to the next one, or finish. */
static void attr_end(struct ripl_ds *d)
{
	d->attr++;
	d->state = d->attr >= 4 ? DS_DONE : DS_ATTR_ID;
}

enum ripl_ds_result ripl_ds_feed(struct ripl_ds *d, const uint8_t *data, size_t len)
{
	size_t i = 0;

	while (i < len) {
		uint8_t c = data[i];

		switch (d->state) {
		case DS_CMD:
			/* Before a valid header the stream is searched byte by byte: a late fragment of an answer that
			 * was given up (or any bytes of an answer to another request) are skipped, not an error. */
			i++;
			if (c == RIPL_ANCS_CMD_GET_ATTRS) {
				d->hdr_n = 0;
				d->uid_seen = 0;
				d->state = DS_UID;
			} else {
				d->skipped++;
			}
			break;
		case DS_UID:
			d->uid_seen |= (uint32_t)c << (8 * d->hdr_n);
			d->hdr[d->hdr_n] = c;
			d->hdr_n++;
			i++;
			if (d->hdr_n == 4) {
				if (d->uid_seen == d->uid) {
					d->state = DS_ATTR_ID;
				} else {
					/* the answer to another notification: skipped. The four bytes read as an id may
					 * hold the start of the answer we want (a stale answer that ended just before
					 * it), so they are searched again. */
					uint8_t again[4];

					memcpy(again, d->hdr, 4);
					d->skipped += 1;
					d->state = DS_CMD;
					(void)ripl_ds_feed(d, again, 4);
				}
			}
			break;
		case DS_ATTR_ID:
			i++;
			if (d->attr == 0 && c != attr_order[0]) {
				/* not the first tuple of our request: the "header" was bytes of another answer that happen to
				 * read as our id (the end of a stale answer and the start of ours). Search again from the byte
				 * after the command byte. */
				uint8_t again[5];

				memcpy(again, d->hdr, 4);
				again[4] = c;
				d->skipped += 1;
				d->state = DS_CMD;
				(void)ripl_ds_feed(d, again, 5);
				break;
			}
			/* the tuples come in the order of the request (ANCS specification) */
			d->state = c == attr_order[d->attr] ? DS_LEN_LO : DS_ERR;
			break;
		case DS_LEN_LO:
			d->len_lo = c;
			d->state = DS_LEN_HI;
			i++;
			break;
		case DS_LEN_HI:
			d->want = (uint16_t)(d->len_lo | ((uint16_t)c << 8));
			d->got = 0;
			d->kept[d->attr] = 0;
			i++;
			if (d->want == 0) {
				size_t cap;
				char *b = attr_buf(d, &cap);

				b[0] = '\0';
				attr_end(d);
			} else {
				d->state = DS_DATA;
			}
			break;
		case DS_DATA: {
			size_t cap;
			char *b = attr_buf(d, &cap);
			size_t take = (size_t)(d->want - d->got);

			if (take > len - i) {
				take = len - i;
			}
			for (size_t k = 0; k < take; k++) {
				if (d->kept[d->attr] < cap) {
					b[d->kept[d->attr]++] = (char)data[i + k];
				}
			}
			d->got = (uint16_t)(d->got + take);
			i += take;
			if (d->got == d->want) {
				b[d->kept[d->attr]] = '\0';
				attr_end(d);
			}
			break;
		}
		case DS_DONE:
		case DS_ERR:
		default:
			i = len; /* ignored */
			break;
		}
		if (d->state == DS_ERR) {
			return RIPL_DS_ERROR;
		}
	}
	return d->state == DS_DONE ? RIPL_DS_DONE : RIPL_DS_MORE;
}

/* ---- AMS ---- */

void ripl_media_init(struct ripl_media *m)
{
	memset(m, 0, sizeof(*m));
	m->state = RIPL_PLAYER_UNKNOWN;
}

static void set_text(char *dst, size_t cap, const uint8_t *v, size_t len)
{
	size_t n = 0;

	while (n < len && v[n] != 0) {
		n++;
	}
	n = rinbox_utf8_cut((const char *)v, n, cap);
	memcpy(dst, v, n);
	dst[n] = '\0';
}

int ripl_media_apply(struct ripl_media *m, uint8_t entity, uint8_t attr, const uint8_t *value, size_t len)
{
	if (entity == RIPL_AMS_ENTITY_TRACK && attr == RIPL_AMS_TRACK_ATTR_TITLE) {
		set_text(m->title, RIPL_TITLE_MAX, value, len);
	} else if (entity == RIPL_AMS_ENTITY_TRACK && attr == RIPL_AMS_TRACK_ATTR_ARTIST) {
		set_text(m->artist, RIPL_ARTIST_MAX, value, len);
	} else if (entity == RIPL_AMS_ENTITY_PLAYER && attr == RIPL_AMS_PLAYER_ATTR_PLAYBACK_INFO) {
		/* "<state>,<rate>,<elapsed>": the state is the digits before the first comma */
		unsigned int st = 0;
		size_t i = 0;

		while (i < len && value[i] >= '0' && value[i] <= '9' && i < 3) {
			st = st * 10 + (unsigned int)(value[i] - '0');
			i++;
		}
		if (i == 0 || (i < len && value[i] != ',')) {
			return -EINVAL;
		}
		if (st == 0) {
			m->state = RIPL_PLAYER_PAUSED;
		} else if (st == 1) {
			m->state = RIPL_PLAYER_PLAYING;
		} else {
			return -ENOTSUP;
		}
	} else {
		return 0;
	}
	m->updates++;
	return 1;
}

/* ---- CTS ---- */

bool ripl_cts_to_ms(int year, int month, int day, int hours, int minutes, int seconds, int fractions256,
		    int64_t *ms)
{
	return rtime_civil_to_ms(year, month, day, hours, minutes, seconds, fractions256, ms) == 0;
}

/* ---- CTS: zone ---- */

bool ripl_cts_zone(int8_t tz15, uint8_t dst, int16_t *total_min)
{
	int dst_min;

	if (tz15 < -48 || tz15 > 56) {
		return false; /* -128 is "unknown" */
	}
	switch (dst) {
	case 0:
		dst_min = 0;
		break;
	case 2:
		dst_min = 30;
		break;
	case 4:
		dst_min = 60;
		break;
	case 8:
		dst_min = 120;
		break;
	default:
		return false; /* 255 is "unknown" */
	}
	*total_min = (int16_t)(tz15 * 15 + dst_min);
	return true;
}

/* ---- CTS: the clock ---- */

void ripl_clock_init(struct ripl_clock *c)
{
	memset(c, 0, sizeof(*c));
}

void ripl_clock_time(struct ripl_clock *c, int64_t local_ms, int64_t up_ms)
{
	c->have_time = true;
	c->local_ms = local_ms;
	c->up_ms = up_ms;
}

void ripl_clock_zone(struct ripl_clock *c, bool read_ok, bool known, int16_t zone_min, int64_t up_now_ms)
{
	(void)up_now_ms;
	if (!read_ok) {
		c->zone_errors++;
		return;
	}
	c->zone_known = known;
	c->zone_min = known ? zone_min : 0;
}

bool ripl_clock_apply(const struct ripl_clock *c, struct rtime_rec *rec)
{
	if (!c->have_time) {
		return false;
	}
	if (c->zone_known) {
		rtime_rec_set(rec, c->up_ms, c->local_ms, c->zone_min, true);
	} else {
		rtime_rec_set(rec, c->up_ms, c->local_ms, 0, false);
	}
	return true;
}
