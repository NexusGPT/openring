/*
 * Ring core: the actions of each FW 1.2 row, hand-written because the
 * document gives them as prose. The row number and the document's line are
 * beside each (design/firmware.md version F6 with F7 part 1, R4b, R9 to R15; row N is line 132 + N).
 * tests/core/count_rows.py checks every "case N: / * line L" against the generated table.
 */
#include "ring_core/rc_sm.h"

#define P(a) push(out, f, RC_ACT_##a)

/* Setting "Vibration" off disables MH and joystick ticks (MT) only (FW 2.2, line 285). */
static void push(struct rc_actions *out, const struct rc_facts *f, enum rc_action a)
{
	if (!f->vibration_on && (a == RC_ACT_MH || a == RC_ACT_MT)) {
		return;
	}
	rc_actions_push(out, a);
}

void rc_row_actions(struct rc_sm *sm, uint8_t row, const struct rc_facts *f, struct rc_actions *out)
{
	switch (row) {
	case 1:  /* line 133 SHIP, VBUS appears: chip leaves ship mode (hardware); charge on */
	case 2:  /* line 134 OFF, VBUS appears: as above, including charge on */
		P(CHARGE_ON);
		break;
	case 3:  /* line 135: VDD_SD off */
		P(SD_OFF);
		break;
	case 4:  /* line 136: keep VDD_SD on */
		P(SD_ON);
		break;
	case 5:  /* line 137: VDD_SD off; charge on */
		P(SD_OFF);
		P(CHARGE_ON);
		break;
	case 6:  /* line 138: log event; MF */
		P(LOG_EVENT);
		P(MF);
		break;
	case 7:  /* line 139: enter ship mode */
		P(SHIP_MODE);
		break;
	case 8:  /* line 140: VDD_SD off; M3 (R13) */
		P(SD_OFF);
		P(M3);
		break;
	case 9:  /* line 141: CLOSE record RECOVERED; clear open flag; VDD_SD off */
		P(WRITE_CLOSE_RECOVERED);
		P(CLEAR_OPEN_FLAG);
		P(SD_OFF);
		break;
	case 10: /* line 142: same actions; charge on */
		P(WRITE_CLOSE_RECOVERED);
		P(CLEAR_OPEN_FLAG);
		P(SD_OFF);
		P(CHARGE_ON);
		break;
	case 11: /* line 143: log event; MF */
		P(LOG_EVENT);
		P(MF);
		break;
	case 12: /* line 144: (guard R1, R4b, R-SIGN) M1; open (R21: M1 at the press, before storage is opened) */
		P(M1);
		P(OPEN);
		sm->s30_warned = false;
		break;
	case 13: /* line 145: no recording starts (R4b); VDD_SD on; mount; RECOVERY scans */
		P(SD_ON);
		P(MOUNT);
		break;
	case 14: /* line 146: no recording starts; screen "Battery low" 3 s (R1) */
		P(SCR_MSG_BATTERY_LOW_3S);
		break;
	case 15: /* line 147: no recording starts; screen "Storage full" 3 s (R1) */
		P(SCR_MSG_STORAGE_FULL_3S);
		break;
	case 16: /* line 148: no recording starts (sign not drawn, R-SIGN); VDD_MIC stays off; M3; event log record */
		P(M3);
		P(LOG_EVENT);
		break;
	case 17: /* line 149: screen off: screen on, status screen, 5 s; screen on: centre action, then MT (R6) */
		if (f->screen_on) {
			P(SCREEN_CENTRE);
			P(MT);
		} else {
			P(SCREEN_ON);
			P(SCR_STATUS_5S);
		}
		break;
	case 18: /* line 150: nothing */
		break;
	case 19: /* line 151: save settings and time; M2; ship mode */
		P(SAVE_SETTINGS_TIME);
		P(M2);
		P(SHIP_MODE);
		break;
	case 20: /* line 152: charge on */
		P(CHARGE_ON);
		break;
	case 21: /* line 153: M3 once per discharge; status screen 5 s */
		if (!sm->b15_warned) {
			P(M3);
			sm->b15_warned = true;
		}
		P(SCR_STATUS_5S);
		break;
	case 22: /* line 154: M3 */
		P(M3);
		break;
	case 23: /* line 155: save settings and time; ship mode */
		P(SAVE_SETTINGS_TIME);
		P(SHIP_MODE);
		break;
	case 24: /* line 156: M3 */
		P(M3);
		break;
	case 25: /* line 157: none; the 60 s retry starts (R11) */
		break;
	case 26: /* line 158: close; M2 */
		P(CLOSE);
		P(M2);
		break;
	case 27: /* line 159: highlight marker; MH; screen 3 s with highlight count */
		P(HIGHLIGHT);
		P(MH);
		P(SCR_RECORDING_3S);
		break;
	case 28: /* line 160: nothing (no highlight, no stop) */
		break;
	case 29: /* line 161: highlight marker; MH */
		P(HIGHLIGHT);
		P(MH);
		break;
	case 30: /* line 162: close; M2; charge on */
		P(CLOSE);
		P(M2);
		P(CHARGE_ON);
		break;
	case 31: /* line 163: M3 once per discharge */
		if (!sm->b15_warned) {
			P(M3);
			sm->b15_warned = true;
		}
		break;
	case 32: /* line 164: close; M3 */
		P(CLOSE);
		P(M3);
		break;
	case 33: /* line 165: close; ship mode */
		P(CLOSE);
		P(SHIP_MODE);
		break;
	case 34: /* line 166: M3 once; screen 3 s "30 min left" */
		if (!sm->s30_warned) {
			P(M3);
			sm->s30_warned = true;
		}
		P(SCR_MSG_30MIN_3S);
		break;
	case 35: /* line 167: close; M3 */
		P(CLOSE);
		P(M3);
		break;
	case 36: /* line 168: stop PDM; clocks low; VDD_MIC off; superblock left open; MF */
		P(STOP_PDM);
		P(CLOCKS_LOW);
		P(MIC_OFF);
		P(MF);
		break;
	case 37: /* line 169: close; MF */
		P(CLOSE);
		P(MF);
		break;
	case 38: /* line 170: nothing runs */
		break;
	case 39: /* line 171: VDD_SD on; mount; charge on stays */
		P(SD_ON);
		P(MOUNT);
		break;
	case 40: /* line 172: none */
	case 41: /* line 173: none (R2) */
		break;
	case 42: /* line 174: save settings and time; ship mode (R10) */
		P(SAVE_SETTINGS_TIME);
		P(SHIP_MODE);
		break;
	case 43: /* line 175: none */
		break;
	case 44: /* line 176: log BCHGERRREASON and BCHGERRSENSOR; charge off; MF */
		P(LOG_CHARGE_ERROR);
		P(CHARGE_OFF);
		P(MF);
		break;
	case 45: /* line 177: refused: M3; screen "In case" 3 s; charge on stays */
		P(M3);
		P(SCR_MSG_IN_CASE_3S);
		break;
	case 46: /* line 178: finish the current command; VDD_SD off; charge on */
		P(FINISH_COMMAND);
		P(SD_OFF);
		P(CHARGE_ON);
		break;
	case 47: /* line 179: abort the command; VDD_SD off */
		P(ABORT_COMMAND);
		P(SD_OFF);
		break;
	case 48: /* line 180: boot_request_upgrade(BOOT_UPGRADE_TEST); reboot */
		P(REQUEST_UPGRADE_TEST);
		P(REBOOT);
		break;
	case 49: /* line 181: section 9.3 */
		P(FACTORY_MODE);
		break;
	case 50: /* line 182: refused: M3 */
		P(M3);
		break;
	case 51: /* line 183: charge on */
		P(CHARGE_ON);
		break;
	case 52: /* line 184: refused: M3; screen "Storage full" 3 s */
		P(M3);
		P(SCR_MSG_STORAGE_FULL_3S);
		break;
	case 53: /* line 185: M3 */
		P(M3);
		break;
	case 54: /* line 186: ship mode */
		P(SHIP_MODE);
		break;
	case 55: /* line 187: charge on */
		P(CHARGE_ON);
		break;
	case 56: /* line 188: refused: M3; screen "Battery low" 3 s */
		P(M3);
		P(SCR_MSG_BATTERY_LOW_3S);
		break;
	case 57: /* line 189: save settings and time; ship mode */
		P(SAVE_SETTINGS_TIME);
		P(SHIP_MODE);
		break;
	case 58: /* line 190: charge on; the case reads the event log */
		P(CHARGE_ON);
		break;
	case 59: /* line 191: retry storage (R3) */
		P(RETRY_STORAGE);
		break;
	case 60: /* line 192: keep VDD_SD on; RECOVERY scans (R9) */
		P(SD_ON);
		break;
	case 61: /* line 193: none; rule R-STB applies (R9) */
		break;
	case 62: /* line 194: none; the next try comes 60 s later (R3) */
		break;
	case 63: /* line 195: ship mode */
		P(SHIP_MODE);
		break;
	case 64: /* line 196: the fault is in the event log */
		break;
	case 65: /* line 197: charge on */
		P(CHARGE_ON);
		break;
	case 66: /* line 198: save settings and time; ship mode (R15) */
		P(SAVE_SETTINGS_TIME);
		P(SHIP_MODE);
		break;
	case 67: /* line 199: none */
		break;
	case 68: /* line 200: save settings and time; ship mode (R15) */
		P(SAVE_SETTINGS_TIME);
		P(SHIP_MODE);
		break;
	case 69: /* line 201: reboot */
		P(REBOOT);
		break;
	case 70: /* line 202: clear the factory flag; ship mode */
		P(CLEAR_FACTORY_FLAG);
		P(SHIP_MODE);
		break;
	case 71: /* line 203: keep the factory flag; ship mode */
		P(SHIP_MODE);
		break;
	case 72: /* line 204: reboot */
		P(REBOOT);
		break;
	default:
		break;
	}
}
