/*
 * Ring inbox: the store of the last 16 notifications of the iPhone. Pure logic: no kernel, driver
 * or Bluetooth call, no locking (the owner, ring_iphone, holds a mutex around every call).
 *
 * Order: items[0] is the newest. rinbox_add() puts the new entry first; when 16 are held the oldest
 * (items[15]) is dropped. An entry changed by rinbox_modify() keeps its place.
 *
 * Text rules (design/firmware.md section 7.6): application identifier at most 48 bytes, title at
 * most 48, message at most 160, date 15 characters. Strings are UTF-8 and always cut at a character
 * boundary: the stored length is the longest prefix not longer than the limit that holds no
 * incomplete character at its end. Every string is NUL terminated.
 *
 * Flag bits are Apple's EventFlags (ANCS appendix: Silent 1<<0, Important 1<<1, PreExisting 1<<2,
 * PositiveAction 1<<3, NegativeAction 1<<4; kit ancs_client.h lines 68-87 give the same bit numbers).
 */
#ifndef RING_INBOX_RINBOX_H
#define RING_INBOX_RINBOX_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RINBOX_MAX      17
#define RINBOX_APP_MAX  48
#define RINBOX_TITLE_MAX 48
#define RINBOX_MSG_MAX  160
#define RINBOX_DATE_MAX 15

#define RINBOX_F_SILENT       (1U << 0)
#define RINBOX_F_IMPORTANT    (1U << 1)
#define RINBOX_F_PREEXISTING  (1U << 2)
#define RINBOX_F_POSITIVE     (1U << 3)  /* the notification has a positive action */
#define RINBOX_F_NEGATIVE     (1U << 4)  /* the notification has a negative action */
#define RINBOX_F_MASK         0x1FU

struct rinbox_item {
	uint32_t uid;       /* the iPhone's notification id */
	uint8_t category;   /* Apple's CategoryID 0..11 (other values are stored as received) */
	uint8_t flags;      /* RINBOX_F_* */
	bool read;          /* the wearer has seen it; set by rinbox_mark_read() only */
	bool text_ready;    /* the attributes (app, title, message, date) have arrived */
	char app[RINBOX_APP_MAX + 1];
	char title[RINBOX_TITLE_MAX + 1];
	char msg[RINBOX_MSG_MAX + 1];
	char date[RINBOX_DATE_MAX + 1];
};

struct rinbox {
	struct rinbox_item items[RINBOX_MAX];
	uint8_t count;
};

void rinbox_init(struct rinbox *b);
void rinbox_clear(struct rinbox *b);
uint8_t rinbox_count(const struct rinbox *b);
/* index 0 is the newest; NULL when out of range */
const struct rinbox_item *rinbox_get(const struct rinbox *b, uint8_t index);
/* index of the entry with this id, or -1 */
int rinbox_find(const struct rinbox *b, uint32_t uid);

/* A notification was added. If the id is already held the entry is replaced and moved to the front
 * (the iPhone's ids are unique inside a session). The text fields are empty and read is false.
 * When the store was full and the id is new, the oldest entry is dropped and its id written to
 * *dropped (when not NULL); otherwise *dropped is left alone. Returns 1 if an entry was dropped,
 * else 0. */
int rinbox_add(struct rinbox *b, uint32_t uid, uint8_t category, uint8_t flags, uint32_t *dropped);

/* The iPhone modified a notification: category and flags are replaced, the place and the text are
 * kept. -ENOENT when the id is not held. */
int rinbox_modify(struct rinbox *b, uint32_t uid, uint8_t category, uint8_t flags);

/* The attributes of a notification arrived: they replace the stored text (cut as the text rules
 * say; NULL means empty). Sets text_ready. -ENOENT when the id is not held. */
int rinbox_set_text(struct rinbox *b, uint32_t uid, const char *app, size_t app_len, const char *title,
		    size_t title_len, const char *msg, size_t msg_len, const char *date, size_t date_len);

/* The iPhone removed a notification. -ENOENT when the id is not held. */
int rinbox_remove(struct rinbox *b, uint32_t uid);

/* -ENOENT when the id is not held. */
int rinbox_mark_read(struct rinbox *b, uint32_t uid);

/* The length of the longest prefix of s[0..len) that is at most max bytes and ends on a character
 * boundary (no incomplete UTF-8 sequence at its end). A byte that is not valid UTF-8 counts as one
 * character. */
size_t rinbox_utf8_cut(const char *s, size_t len, size_t max);

#ifdef __cplusplus
}
#endif

#endif
