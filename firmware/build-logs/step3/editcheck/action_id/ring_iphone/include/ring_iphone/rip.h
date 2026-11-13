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
	uint32_t ns_added, ns_modified, ns_removed, ns_bad, ns_modified_unknown;
	uint32_t inbox_dropped;   /* entries pushed out by the 17th */
	uint32_t fetch_requests, fetch_done, fetch_errors, fetch_timeouts, fetch_skipped, fetch_overflow;
	uint32_t actions_sent, actions_refused, action_errors, action_failed;
	uint32_t media_sent, media_refused, media_errors, media_reports, media_ignored;
	uint32_t time_sets;
	uint32_t inbox_cleared;   /* times the inbox was emptied because a session or service ended */
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
 * is not set): nothing is sent. -ENOTCONN: the notification service is not up. -EBUSY and other
 * negative values come from the kit's write. Returns 0 when the command was handed to the link. */
int rip_action(uint32_t uid, enum rip_action action);
/* A dismiss chosen on the ring is the negative action. */
int rip_dismiss(uint32_t uid);

/* The track title, the artist and the player state as the iPhone reported them. */
void rip_media_get(struct ripl_media *out);
/* Send a remote command (Apple Media Service Remote Command). Stores nothing: the state changes only
 * when the iPhone reports. -ENOTCONN: the media service is not up. */
int rip_media_command(enum rip_media_cmd cmd);

void rip_stats_get(struct rip_stats *out);

#ifdef __cplusplus
}
#endif

#endif
