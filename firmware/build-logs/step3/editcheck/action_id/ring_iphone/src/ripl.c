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
			if (c != RIPL_ANCS_CMD_GET_ATTRS) {
				d->state = DS_ERR;
				break;
			}
			d->hdr_n = 0;
			d->uid_seen = 0;
			d->state = DS_UID;
			i++;
			break;
		case DS_UID:
			d->uid_seen |= (uint32_t)c << (8 * d->hdr_n);
			d->hdr_n++;
			i++;
			if (d->hdr_n == 4) {
				d->state = d->uid_seen == d->uid ? DS_ATTR_ID : DS_ERR;
			}
			break;
		case DS_ATTR_ID:
			/* the tuples come in the order of the request (ANCS specification) */
			d->state = c == attr_order[d->attr] ? DS_LEN_LO : DS_ERR;
			i++;
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
