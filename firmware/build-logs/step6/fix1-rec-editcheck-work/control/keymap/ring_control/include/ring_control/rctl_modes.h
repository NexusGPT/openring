/*
 * Ring control: the four modes and what each joystick action sends.
 * This header is the whole mapping. One row per mode, one column per
 * joystick action, as a reader checks it against design.md section 3 and the
 * owner's list. Key codes are USB HID usages (HID Usage Tables 1.4):
 * keyboard page 0x07, consumer page 0x0C.
 *
 * Joystick actions are the five the core gives for the screen shown
 * (RC_ACT_SCREEN_CENTRE, _UP, _DOWN, _LEFT, _RIGHT). The long press of the
 * centre is not here: it belongs to recording only and no mode may use it.
 *
 * Pure data: no kernel, driver or Bluetooth include.
 */
#ifndef RING_CONTROL_RCTL_MODES_H
#define RING_CONTROL_RCTL_MODES_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum rctl_mode {
	RCTL_MEDIA,
	RCTL_PRESENTER,
	RCTL_POINTER,
	RCTL_AGENT,
	RCTL_MODE_COUNT
};

/* The joystick actions of the core (short press of the centre, four directions). */
enum rctl_action {
	RCTL_CENTRE,
	RCTL_UP,
	RCTL_DOWN,
	RCTL_LEFT,
	RCTL_RIGHT,
	RCTL_ACTION_COUNT
};

/* What an action sends. */
enum rctl_kind {
	RCTL_SEND_NONE,     /* nothing is sent */
	RCTL_SEND_KEY,      /* keyboard: key down report, then the release report */
	RCTL_SEND_CONSUMER, /* consumer control: usage down report, then the release report */
	RCTL_SEND_MOVE,     /* pointer: one relative move report (dx, dy), no button */
	RCTL_SEND_CLICK     /* pointer: button 1 down report, then the release report */
};

struct rctl_entry {
	uint8_t kind;   /* enum rctl_kind */
	uint16_t usage; /* RCTL_SEND_KEY: keyboard usage; RCTL_SEND_CONSUMER: consumer usage */
	int8_t dx;      /* RCTL_SEND_MOVE */
	int8_t dy;      /* RCTL_SEND_MOVE: negative is up */
};

/* Keyboard usages (page 0x07) */
#define RCTL_K_RETURN      0x28
#define RCTL_K_ESCAPE      0x29
#define RCTL_K_PAGE_UP     0x4B
#define RCTL_K_PAGE_DOWN   0x4E
#define RCTL_K_RIGHT_ARROW 0x4F
#define RCTL_K_LEFT_ARROW  0x50
#define RCTL_K_DOWN_ARROW  0x51
#define RCTL_K_UP_ARROW    0x52

/* Consumer usages (page 0x0C) */
#define RCTL_C_PLAY_PAUSE  0x00CD
#define RCTL_C_NEXT        0x00B5  /* Scan Next Track */
#define RCTL_C_PREVIOUS    0x00B6  /* Scan Previous Track */
#define RCTL_C_VOLUME_UP   0x00E9
#define RCTL_C_VOLUME_DOWN 0x00EA

/* Pointer step in report units for one direction event. A held direction
 * repeats through the core (500 ms, then every 150 ms), so the pointer keeps
 * moving while the joystick is held. */
#define RCTL_POINTER_STEP 16

#define RCTL_E_NONE             { RCTL_SEND_NONE, 0, 0, 0 }
#define RCTL_E_KEY(k)           { RCTL_SEND_KEY, (k), 0, 0 }
#define RCTL_E_CONSUMER(u)      { RCTL_SEND_CONSUMER, (u), 0, 0 }
#define RCTL_E_MOVE(x, y)       { RCTL_SEND_MOVE, 0, (x), (y) }
#define RCTL_E_CLICK            { RCTL_SEND_CLICK, 0, 0, 0 }

/*
 * The mode table.
 *
 *             centre (short)   up             down           left           right
 * media       play or pause    volume up      volume down    previous       next
 * presenter   (nothing)        previous slide next slide     previous slide next slide
 * pointer     click            move up        move down      move left      move right
 * agent       Return           Up Arrow       Down Arrow     Escape         Return
 *
 * presenter: the slide keys are the arrow keys; the option below swaps them
 * for Page Up and Page Down.
 * agent: keys only, no text is typed. right is accept (Return), left is
 * decline (Escape).
 */
static const struct rctl_entry rctl_map[RCTL_MODE_COUNT][RCTL_ACTION_COUNT] = {
	[RCTL_MEDIA] = {
		[RCTL_CENTRE] = RCTL_E_CONSUMER(RCTL_C_PLAY_PAUSE),
		[RCTL_UP]     = RCTL_E_CONSUMER(RCTL_C_VOLUME_UP),
		[RCTL_DOWN]   = RCTL_E_CONSUMER(RCTL_C_VOLUME_DOWN),
		[RCTL_LEFT]   = RCTL_E_CONSUMER(RCTL_C_PREVIOUS),
		[RCTL_RIGHT]  = RCTL_E_CONSUMER(RCTL_C_NEXT),
	},
	[RCTL_PRESENTER] = {
		[RCTL_CENTRE] = RCTL_E_NONE,
		[RCTL_UP]     = RCTL_E_KEY(RCTL_K_LEFT_ARROW),
		[RCTL_DOWN]   = RCTL_E_KEY(RCTL_K_RIGHT_ARROW),
		[RCTL_LEFT]   = RCTL_E_KEY(RCTL_K_LEFT_ARROW),
		[RCTL_RIGHT]  = RCTL_E_KEY(RCTL_K_LEFT_ARROW),
	},
	[RCTL_POINTER] = {
		[RCTL_CENTRE] = RCTL_E_CLICK,
		[RCTL_UP]     = RCTL_E_MOVE(0, -RCTL_POINTER_STEP),
		[RCTL_DOWN]   = RCTL_E_MOVE(0, RCTL_POINTER_STEP),
		[RCTL_LEFT]   = RCTL_E_MOVE(-RCTL_POINTER_STEP, 0),
		[RCTL_RIGHT]  = RCTL_E_MOVE(RCTL_POINTER_STEP, 0),
	},
	[RCTL_AGENT] = {
		[RCTL_CENTRE] = RCTL_E_KEY(RCTL_K_RETURN),
		[RCTL_UP]     = RCTL_E_KEY(RCTL_K_UP_ARROW),
		[RCTL_DOWN]   = RCTL_E_KEY(RCTL_K_DOWN_ARROW),
		[RCTL_LEFT]   = RCTL_E_KEY(RCTL_K_ESCAPE),
		[RCTL_RIGHT]  = RCTL_E_KEY(RCTL_K_RETURN),
	},
};

/* Presenter with the Page keys option: the same four directions, Page Up and Page Down. */
static const struct rctl_entry rctl_presenter_pages[RCTL_ACTION_COUNT] = {
	[RCTL_CENTRE] = RCTL_E_NONE,
	[RCTL_UP]     = RCTL_E_KEY(RCTL_K_PAGE_UP),
	[RCTL_DOWN]   = RCTL_E_KEY(RCTL_K_PAGE_DOWN),
	[RCTL_LEFT]   = RCTL_E_KEY(RCTL_K_PAGE_UP),
	[RCTL_RIGHT]  = RCTL_E_KEY(RCTL_K_PAGE_DOWN),
};

#ifdef __cplusplus
}
#endif

#endif
