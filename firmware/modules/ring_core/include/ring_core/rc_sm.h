/*
 * Ring core: table-driven state machine of FW 1.2.
 */
#ifndef RING_CORE_RC_SM_H
#define RING_CORE_RC_SM_H

#include "rc_types.h"

#ifdef __cplusplus
extern "C" {
#endif

struct rc_row {
	uint8_t row;            /* FW 1.2 row number, 1 = first row of the table */
	uint16_t doc_line;      /* line of design/firmware.md the row was generated from */
	uint8_t from;           /* enum rc_state */
	uint8_t event;          /* enum rc_event */
	uint8_t guard;          /* enum rc_guard */
	uint8_t to;             /* enum rc_state */
	const char *event_text; /* exact text of the event column */
};

/* Generated table, src/state_table.inc. */
extern const struct rc_row rc_table[];
extern const uint16_t rc_table_rows;
extern const uint32_t rc_table_fnv1a;

/* Hand-written actions per row (src/state_actions.c). Fills out with the
 * exact action list of the row for the given facts and once-flags. */
struct rc_sm {
	uint8_t state;          /* enum rc_state */
	bool b15_warned;        /* "M3 once per discharge" (rows 17, 26) */
	bool s30_warned;        /* "M3 once" (row 29) */
};

void rc_sm_init(struct rc_sm *sm, enum rc_state start);
bool rc_guard_holds(enum rc_guard g, const struct rc_facts *f);
/* First row in table order whose from-state, event and guard match; NULL if none. */
const struct rc_row *rc_sm_find(const struct rc_sm *sm, enum rc_event ev, const struct rc_facts *f);
/* Take the transition for ev if a row matches: appends actions, sets the state.
 * Returns the row number, or 0 when no row matches (the event is then ignored). */
int rc_sm_handle(struct rc_sm *sm, enum rc_event ev, const struct rc_facts *f, struct rc_actions *out);

/* The hand-written actions of one row (src/state_actions.c). */
void rc_row_actions(struct rc_sm *sm, uint8_t row, const struct rc_facts *f, struct rc_actions *out);

void rc_actions_clear(struct rc_actions *out);
void rc_actions_push(struct rc_actions *out, enum rc_action a);
/* FNV-1a 32 over "row|FROM|event text|TO\n" of every row, as tools/gen_table.py computes it. */
uint32_t rc_table_checksum(void);

#ifdef __cplusplus
}
#endif

#endif
