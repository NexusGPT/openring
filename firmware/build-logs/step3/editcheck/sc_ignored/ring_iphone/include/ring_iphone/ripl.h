/*
 * Ring iPhone part, pure logic: no kernel, driver or Bluetooth call.
 *
 *  - the Apple Notification Center Service (ANCS) Data Source reassembly: the answer to a
 *    "Get Notification Attributes" request arrives in fragments of any size and is spliced here
 *    (Apple ANCS specification, "Get Notification Attributes": "If the response is larger than the
 *    negotiated GATT Maximum Transmission Unit (MTU), it is split into multiple fragments by the NP.
 *    The NC must recompose the response by splicing each fragment."). The kit's own parser keeps at
 *    most 32 bytes per attribute (BT_ANCS_ATTR_DATA_MAX, ancs_client.h line 50, checked in
 *    ancs_client.c line 479), too little for the 160-byte message of the inbox, so this one is used.
 *  - the request builder for that command
 *  - the Apple Media Service (AMS) Entity Update decoder: track title, artist, player state
 *  - the civil time of the Current Time Service (CTS) to milliseconds
 */
#ifndef RING_IPHONE_RIPL_H
#define RING_IPHONE_RIPL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---- ANCS: request and response of Get Notification Attributes ---- */

/* ANCS appendix: CommandIDGetNotificationAttributes = 0; NotificationAttributeID AppIdentifier = 0,
 * Title = 1, Message = 3, Date = 5 (Title and Message "need to be followed by a 2-bytes max length
 * parameter"); also kit ancs_client.h lines 140-193 and ancs_client.c lines 409-453 (encoding). */
#define RIPL_ANCS_CMD_GET_ATTRS    0
#define RIPL_ANCS_ATTR_APP         0
#define RIPL_ANCS_ATTR_TITLE       1
#define RIPL_ANCS_ATTR_MESSAGE     3
#define RIPL_ANCS_ATTR_DATE        5
#define RIPL_REQ_APP_MAX           48   /* kept, not requested: the app identifier has no length parameter */
#define RIPL_REQ_TITLE_MAX         48   /* max length parameter sent for the title */
#define RIPL_REQ_MESSAGE_MAX       160  /* max length parameter sent for the message */
#define RIPL_REQ_DATE_MAX          15   /* "yyyyMMdd'T'HHmmSS" (ANCS appendix note on Date) */
#define RIPL_REQ_LEN               13   /* 1 + 4 + (1) + (1+2) + (1+2) + (1) */

/* Writes the 13-byte request into buf (at least RIPL_REQ_LEN bytes); returns its length. */
size_t ripl_build_get_attrs(uint8_t *buf, uint32_t uid);

enum ripl_ds_result {
	RIPL_DS_MORE = 0,   /* more fragments are needed */
	RIPL_DS_DONE = 1,   /* the four attributes are complete */
	RIPL_DS_ERROR = -1, /* the stream does not match the request */
};

struct ripl_ds {
	uint8_t state;
	uint8_t attr;        /* index into the requested list 0..3 */
	uint8_t hdr_n;       /* bytes of the header read */
	uint16_t want;       /* length of the attribute in the stream */
	uint16_t got;        /* bytes of the attribute read */
	uint8_t len_lo;
	uint32_t uid;        /* the notification the request was for */
	uint32_t uid_seen;
	uint16_t kept[4];    /* bytes stored per attribute */
	char app[RIPL_REQ_APP_MAX + 1];
	char title[RIPL_REQ_TITLE_MAX + 1];
	char msg[RIPL_REQ_MESSAGE_MAX + 1];
	char date[RIPL_REQ_DATE_MAX + 1];
};

/* Start a response for the request of this notification id. */
void ripl_ds_start(struct ripl_ds *d, uint32_t uid);
/* Feed one Data Source notification (any size, also empty). After DONE or ERROR more input is
 * ignored and the same result is returned. */
enum ripl_ds_result ripl_ds_feed(struct ripl_ds *d, const uint8_t *data, size_t len);
uint32_t ripl_ds_uid(const struct ripl_ds *d);

/* ---- AMS: Entity Update notification ---- */

/* Kit ams_client.h lines 100-142: Entity Player = 0, Queue = 1, Track = 2; Player attribute
 * PlaybackInfo = 1; Track attribute Artist = 0, Album = 1, Title = 2, Duration = 3. Entity Update
 * notification: EntityID, AttributeID, EntityUpdateFlags, Value (Apple AMS specification, Entity
 * Update). PlaybackInfo value: "<state>,<rate>,<elapsed>" as text, for example "1,1.0,0.014" is
 * playing and "0,0.0,0.000" is paused (kit samples/bluetooth/peripheral_ams_client/README.rst,
 * "Music setup" and "Playback"). */
#define RIPL_AMS_ENTITY_PLAYER 0
#define RIPL_AMS_ENTITY_TRACK  2
#define RIPL_AMS_PLAYER_ATTR_PLAYBACK_INFO 1
#define RIPL_AMS_TRACK_ATTR_ARTIST 0
#define RIPL_AMS_TRACK_ATTR_TITLE  2

#define RIPL_TITLE_MAX  64
#define RIPL_ARTIST_MAX 48

enum ripl_player {
	RIPL_PLAYER_UNKNOWN = 0, /* the iPhone has not reported yet (or the session ended) */
	RIPL_PLAYER_PAUSED = 1,
	RIPL_PLAYER_PLAYING = 2,
};

struct ripl_media {
	char title[RIPL_TITLE_MAX + 1];
	char artist[RIPL_ARTIST_MAX + 1];
	enum ripl_player state;
	uint32_t updates; /* reports that changed something */
};

void ripl_media_init(struct ripl_media *m);
/* Apply one Entity Update (the value is the bytes after the three header bytes). Returns 1 when a
 * stored field was set (even to the same value), 0 when the pair is not one the ring stores, and a
 * negative errno for a value it cannot read (a player state other than 0 or 1 is -ENOTSUP and
 * changes nothing). Text is cut at a character boundary. */
int ripl_media_apply(struct ripl_media *m, uint8_t entity, uint8_t attr, const uint8_t *value, size_t len);

/* ---- CTS ---- */

/* Current Time characteristic value: 10 bytes, year u16 LE, month, day, hours, minutes, seconds,
 * day of week, fractions256, adjust reason (kit cts_client.c lines 20-21 and 110-135).
 * Returns the time in ms since 1970-01-01 of that civil time read as it is (the iPhone gives its
 * local time; the zone is not read, so the ring's clock holds the iPhone's local time), or
 * -EINVAL (via *ok = false). */
bool ripl_cts_to_ms(int year, int month, int day, int hours, int minutes, int seconds, int fractions256,
		    int64_t *ms);

#ifdef __cplusplus
}
#endif

#endif
