/*
 * Ring core: shared types. Pure logic: stdint, stdbool and string only.
 * Specification: design/firmware.md version F7 part 1 (FW). Section numbers below are FW sections.
 */
#ifndef RING_CORE_RC_TYPES_H
#define RING_CORE_RC_TYPES_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Time in ms from the event timestamps (GRTC uptime, FW 2.1). */
typedef int64_t rc_ms_t;
#define RC_NO_TICK INT64_MAX

/* States of FW 1.1, in the order of its table. */
enum rc_state {
	RC_ST_SHIP,
	RC_ST_OFF,
	RC_ST_BOOT,
	RC_ST_RECOVERY,
	RC_ST_STANDBY,
	RC_ST_RECORDING,
	RC_ST_CHARGING,
	RC_ST_TRANSFER,
	RC_ST_ERR_STORAGE_FULL,
	RC_ST_ERR_BATTERY_LOW,
	RC_ST_ERR_STORAGE_FAULT,
	RC_ST_ERR_MIC_FAULT,
	RC_ST_ERR_CHARGER,
	RC_ST_FACTORY_TEST,
	RC_ST_COUNT
};

/* Events of the FW 1.2 table (names chosen here; the text of each row is kept in the table). */
enum rc_event {
	RC_EV_VBUS_IN,
	RC_EV_VBUS_OUT,
	RC_EV_INIT_DONE,
	RC_EV_STORAGE_INIT_FAILED,  /* storage init failed 3 times, 200 ms apart (counted by the caller) */
	RC_EV_BATT_B15,
	RC_EV_BATT_B5,
	RC_EV_BATT_B2,
	RC_EV_SCAN_DONE,
	RC_EV_SCAN_READ_ERROR,
	RC_EV_LONG_PRESS,
	RC_EV_SHORT_PRESS,
	RC_EV_DOUBLE_PRESS,
	RC_EV_MENU_POWER_OFF,       /* menu "Power off" confirmed */
	RC_EV_STORAGE_SFULL,
	RC_EV_STORAGE_S30,
	RC_EV_BLE_HIGHLIGHT,
	RC_EV_CHUNK_WRITE_FAILED,   /* chunk write failed 3 times (counted by the caller) */
	RC_EV_MIC_NO_BLOCK,         /* the PDM instance gave no block for 100 ms */
	RC_EV_POWER_LOSS,
	RC_EV_USB_CONFIGURED,
	RC_EV_USB_UNCONFIGURED,     /* USB suspended or unconfigured by the case */
	RC_EV_CHARGE_ERROR,
	RC_EV_FW_END,
	RC_EV_FACTORY_ENTER,
	RC_EV_TIMER_60S,            /* made by rc_core_tick in ERR_STORAGE_FAULT, every 60 s (R3) */
	RC_EV_TIMER_5S,             /* made by rc_core_tick in ERR_MIC_FAULT */
	RC_EV_FACTORY_EXIT,
	RC_EV_SHIP_ENTER,
	RC_EV_SHIP_SAMPLE,
	RC_EV_STORAGE_RETRY_OK,     /* result of RC_ACT_RETRY_STORAGE (R3) */
	RC_EV_STORAGE_RETRY_FAILED,
	RC_EV_STORAGE_FAULT_SET,    /* internal: R-STB entry with the storage fault set (R11) */
	RC_EV_COUNT
};

/* Guards written in the event column of FW 1.2. */
enum rc_guard {
	RC_G_NONE,
	RC_G_OPEN_CLEAR_NO_VBUS_ABOVE_B5,
	RC_G_OPEN_SET,
	RC_G_VBUS,
	RC_G_NO_VBUS,
	RC_G_ABOVE_SFULL_ABOVE_B5,
	RC_G_SFULL,
	RC_G_AT_B5,
	RC_G_FACTORY_FLAG,
	RC_G_OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL_SIGN,  /* row 12, rulings R1, R4b, rule R-SIGN (the recording sign is drawn) */
	RC_G_SFULL_ABOVE_B5,        /* ruling R2 */
	RC_G_AT_B2,                 /* ruling R10 */
	RC_G_OPEN_CLEAR,            /* ruling R9 */
	RC_G_SIGN_NOT_DRAWN,        /* row 16: the sign hook refused (step 6, rule R-SIGN) */
	RC_G_COUNT
};

/* Actions the core requests. The caller carries them out in order. */
enum rc_action {
	RC_ACT_NONE = 0,
	/* FW 1.2 common actions */
	RC_ACT_OPEN,                 /* "open": VDD_SD on, mount, superblock open, VDD_MIC on, start PDM */
	RC_ACT_CLOSE,                /* "close": partial chunk, CLOSE record, superblock clear, stop PDM, clocks low, VDD_MIC off, VDD_SD off */
	RC_ACT_CHARGE_ON,
	RC_ACT_CHARGE_OFF,
	/* motor patterns, FW 3.1 */
	RC_ACT_M1,
	RC_ACT_M2,
	RC_ACT_M3,
	RC_ACT_MH,
	RC_ACT_MT,
	RC_ACT_MF,
	RC_ACT_MW,
	/* power rail and storage requests */
	RC_ACT_SD_ON,                /* VDD_SD on (row 4: "keep VDD_SD on"; row 34: "VDD_SD on") */
	RC_ACT_SD_OFF,
	RC_ACT_MOUNT,
	RC_ACT_STOP_PDM,
	RC_ACT_CLOCKS_LOW,
	RC_ACT_MIC_OFF,              /* VDD_MIC off */
	RC_ACT_SHIP_MODE,            /* enter ship mode, FW 8.4 */
	RC_ACT_SAVE_SETTINGS_TIME,
	RC_ACT_CLEAR_FACTORY_FLAG,
	RC_ACT_REQUEST_UPGRADE_TEST, /* boot_request_upgrade(BOOT_UPGRADE_TEST), FW 9.2 */
	RC_ACT_REBOOT,
	RC_ACT_FACTORY_MODE,         /* run FW 9.3 */
	RC_ACT_RETRY_STORAGE,        /* "60 s elapsed" row: run the storage init, report RC_EV_STORAGE_RETRY_OK or _FAILED (R3) */
	/* records and log */
	RC_ACT_LOG_EVENT,
	RC_ACT_LOG_CHARGE_ERROR,     /* log BCHGERRREASON and BCHGERRSENSOR */
	RC_ACT_WRITE_CLOSE_RECOVERED,/* index CLOSE record with state RECOVERED */
	RC_ACT_CLEAR_OPEN_FLAG,
	RC_ACT_HIGHLIGHT,            /* highlight marker, time of CENTRE_DOWN (rc_actions.highlight_ms) */
	/* transfer */
	RC_ACT_FINISH_COMMAND,
	RC_ACT_ABORT_COMMAND,
	/* screen requests, FW 3.3 names */
	RC_ACT_SCREEN_ON,
	RC_ACT_SCR_STATUS_5S,        /* SCR_STATUS for 5 s */
	RC_ACT_SCR_RECORDING_3S,     /* SCR_RECORDING for 3 s with the highlight count */
	RC_ACT_SCR_MSG_30MIN_3S,     /* SCR_MESSAGE "30 min left" 3 s */
	RC_ACT_SCR_MSG_IN_CASE_3S,   /* SCR_MESSAGE "In case" 3 s */
	RC_ACT_SCR_MSG_STORAGE_FULL_3S,
	RC_ACT_SCR_MSG_BATTERY_LOW_3S,
	RC_ACT_SCREEN_CENTRE,        /* the centre action of the screen shown (FW 2.2 table) */
	RC_ACT_SCREEN_UP,            /* a direction for the screen shown (FW 2.2 table) */
	RC_ACT_SCREEN_DOWN,
	RC_ACT_SCREEN_LEFT,
	RC_ACT_SCREEN_RIGHT,
	RC_ACT_COUNT
};

#define RC_MAX_ACTIONS 32

struct rc_actions {
	uint8_t n;
	uint8_t a[RC_MAX_ACTIONS];   /* enum rc_action values */
	int16_t last_row;            /* FW 1.2 row of the last transition taken, -1 if none */
	rc_ms_t highlight_ms;        /* time of CENTRE_DOWN of the last highlight, -1 if none */
};

/* Battery level as the thresholds of FW 1.1 */
enum rc_batt {
	RC_BATT_OK,   /* above B15 */
	RC_BATT_B15,  /* at or under 15 % */
	RC_BATT_B5,   /* at or under 5 % or 3.45 V */
	RC_BATT_B2    /* at or under 2 % or 3.30 V */
};

/* Facts the guards read. Events update the facts they carry; the caller sets the rest. */
struct rc_facts {
	bool vbus;
	bool open_flag;        /* superblock open flag: the caller sets it at start-up; the core then follows its own
	                        * actions (OPEN sets it; only CLOSE and CLEAR_OPEN_FLAG clear it, ruling R9) */
	bool factory_flag;
	bool storage_full;     /* free space at SFULL */
	bool storage_fault;    /* ruling R11: set on entering ERR_STORAGE_FAULT, cleared by INIT_DONE or STORAGE_RETRY_OK */
	bool screen_on;
	bool vibration_on;     /* setting "Vibration", FW 2.2 */
	bool sign_not_drawn;   /* step 6: set by the core for one long press when the sign hook refused; never by the caller */
	uint8_t batt;          /* enum rc_batt; set only through rc_core_battery() */
};

const char *rc_state_name(enum rc_state s);
const char *rc_event_name(enum rc_event e);
const char *rc_action_name(enum rc_action a);
const char *rc_guard_name(enum rc_guard g);

#ifdef __cplusplus
}
#endif

#endif
