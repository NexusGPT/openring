/*
 * Ring iPhone part: Apple's three services as a client, for the active device.
 *
 *  - Notification Center Service (ANCS): the inbox of the last 16 notifications, perform-action
 *  - Media Service (AMS): track title, artist, player state, the six remote commands
 *  - Current Time Service (CTS): the ring's clock (ring_time) takes the iPhone's time
 *  - Service Changed (GATT service): the ring looks for the three services again when it is indicated
 *
 * Started by rglue_init() (ring_glue) next to devices and control. It needs no other call: when the
 * link of the active device reaches security level 4 it finds the services; a device without them is
 * not an error (the inbox stays empty, the commands return -ENOTCONN).
 *
 * Nothing in this part calls the core, the glue or the recorder: nothing from the iPhone can start
 * or stop a recording, or change a core state. The stored data changes only on the iPhone's reports
 * (Apple: the ring shows the state the iPhone reports, not the state it asked for).
 */
#ifndef RING_IPHONE_RIP_H
#define RING_IPHONE_RIP_H

#include <stdbool.h>
#include <stdint.h>

#include <ring_inbox/rinbox.h>
#include <ring_iphone/ripl.h>

#ifdef __cplusplus
extern "C" {
#endif

enum rip_action {
	RIP_ACTION_POSITIVE = 0, /* Apple ActionIDPositive */
	RIP_ACTION_NEGATIVE = 1, /* Apple ActionIDNegative: the dismiss */
};

enum rip_media_cmd {
	RIP_MEDIA_PLAY = 0,
	RIP_MEDIA_PAUSE,
	RIP_MEDIA_NEXT,
	RIP_MEDIA_PREVIOUS,
	RIP_MEDIA_VOLUME_UP,
	RIP_MEDIA_VOLUME_DOWN,
	RIP_MEDIA_CMD_COUNT,
};

struct rip_stats {
	uint32_t sessions;        /* links of the active device that reached level 4 and were used */
	uint32_t sessions_ended;
	uint32_t gattp_found, gattp_missing;
	uint32_t sc_indications;
	uint32_t ancs_up, ancs_down, ancs_missing;   /* subscribed, stopped, not found */
	uint32_t ams_up, ams_down, ams_missing;
	uint32_t cts_up, cts_down, cts_missing;
	uint32_t dm_errors;
	uint32_t dm_stale;        /* answers of a discovery that belonged to a session that had ended: dropped */
	uint32_t ns_added, ns_modified, ns_removed, ns_bad, ns_modified_unknown;
	uint32_t inbox_dropped;   /* entries pushed out by the 17th */
	uint32_t fetch_requests, fetch_done, fetch_errors, fetch_timeouts, fetch_skipped, fetch_overflow;
	uint32_t fetch_retries;   /* a failed request asked for again (once per notification) */
	uint32_t fetch_failed;    /* a request given up after its retry (or one that could not be retried) */
	uint32_t ended_in_discovery; /* sessions whose link ended before all three services had been looked for */
	uint32_t actions_sent, actions_refused, action_errors, action_failed;
	uint32_t media_sent, media_refused, media_errors, media_reports, media_ignored;
	uint32_t time_sets;
	uint32_t zone_errors;      /* zone reads that failed or had a wrong length: the last zone was kept */
	uint32_t ds_skipped;       /* bytes of the Data Source skipped because they were not the answer in flight */
	uint32_t zone_reads, zone_known_sets; /* Local Time Information reads; clock settings made with a known zone */
	uint32_t inbox_cleared;   /* times the inbox was emptied because a session or service ended */
	/* step 5: the relay service's use of the store (design/firmware.md 7.7) */
	uint32_t relay_opens, relay_puts, relay_removes, relay_clears; /* HELLO sessions, entries stored, removed, CLEAR frames */
	uint32_t relay_dropped;   /* entries pushed out by the 17th (relay source) */
	uint32_t relay_actions;   /* actions handed to the relay service */
	uint32_t relay_blocked;   /* Apple's notification service found on a link that already had a relay session */
};

/* Step 5: the source of the notifications of a link. It is fixed by the first user (Apple's notification service found on
 * the link, or a relay HELLO) and ends with the link. The screens never see it. */
enum rip_src {
	RIP_SRC_NONE = 0,
	RIP_SRC_APPLE,
	RIP_SRC_RELAY,
};

struct bt_conn;

/* What the relay service gives the iPhone part so that an action reaches the source of the entry. Registered once at start
 * (rip_relay_register). action() is called without any lock of this part held. It returns 0 when the frame was handed to the
 * helper, or a negative errno (-ENOTCONN: no session or no subscription to Out). */
struct rip_relay_ops {
	int (*action)(uint32_t uid, enum rip_action action);
};

/* Called once by rglue_init(). 0 or a negative errno. */
int rip_init(void);

/* The services are found and subscribed for the current link. */
bool rip_ancs_ready(void);
bool rip_ams_ready(void);
bool rip_cts_ready(void);

/* The inbox: index 0 is the newest. Copies the entry; false when out of range. */
uint8_t rip_inbox_count(void);
bool rip_inbox_get(uint8_t index, struct rinbox_item *out);
/* The wearer has seen it (local mark only: nothing is sent to the iPhone). */
int rip_inbox_mark_read(uint32_t uid);

/* Perform the positive or the negative action of a notification of the inbox. Sends Apple's
 * Perform Notification Action command (CommandID 2, notification id, ActionID) to the iPhone. The inbox
 * changes only when the iPhone then reports the removal.
 * -ENOENT: the id is not in the inbox. -ENOTSUP: the notification does not have that action (its flag
 * is not set): nothing is sent. -ENOTCONN: the notification service is not up. -EBUSY (the kit allows
 * one action write at a time: try again after the previous one was answered) and other negative values
 * come from the kit's write. Returns 0 when the command was handed to the link. */
int rip_action(uint32_t uid, enum rip_action action);
/* A dismiss chosen on the ring is the negative action. */
int rip_dismiss(uint32_t uid);

/* The track title, the artist and the player state as the iPhone reported them. */
void rip_media_get(struct ripl_media *out);
/* Send a remote command (Apple Media Service Remote Command). Stores nothing: the state changes only
 * when the iPhone reports. -ENOTCONN: the media service is not up. */
int rip_media_command(enum rip_media_cmd cmd);

void rip_stats_get(struct rip_stats *out);

/* ---- step 5: the relay service writes the same store (design/firmware.md 7.7) ----
 * One mutex of this part guards the store for both sources. The relay calls these with its own lock held (order: relay lock,
 * then this part's lock); this part calls the relay only without its lock. */
void rip_relay_register(const struct rip_relay_ops *ops);
/* The source of this link now. */
enum rip_src rip_src_of(const struct bt_conn *link);
/* HELLO: the link's source becomes the relay and what the relay stored is emptied. 0, or -EPERM when Apple's notification
 * service was found on this link (the relay frame is refused with code 7). */
int rip_relay_open(const struct bt_conn *link);
/* PUT, REMOVE, CLEAR on the relay's link: 0, -EPERM (Apple's link), -ENOTCONN (this link is not the relay's). rip_relay_put
 * returns 0 for a stored or replaced entry. REMOVE of an id that is not held is not an error. */
int rip_relay_put(const struct bt_conn *link, uint32_t uid, uint8_t category, uint8_t flags, const char *app, size_t app_len,
		  const char *title, size_t title_len, const char *msg, size_t msg_len, const char *date, size_t date_len);
int rip_relay_remove(const struct bt_conn *link, uint32_t uid);
int rip_relay_clear(const struct bt_conn *link);

#ifdef CONFIG_RING_RELAY_TEST_HOOKS
/* Test ring only (never set in the product): hold the start of the iPhone part's session (the 20 ms after level 4) until released, so a test can
 * put a relay HELLO and entries before it. */
void rip_test_hold_session_start(bool hold);
#endif

#ifdef __cplusplus
}
#endif

#endif
