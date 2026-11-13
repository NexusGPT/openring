#!/usr/bin/env python3
"""broken_edit.py <variant> <modules dir> <out dir>: copy modules/ring_screens to <out dir>/ring_screens and make ONE named fault.

Prints EXPECT=<name of the one ztest case that must fail>. The real files are not touched. An edit that does not match exactly
once is an error."""
import pathlib
import shutil
import sys

variant, mods, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
dst = out / "ring_screens"
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(mods / "ring_screens", dst)

L = "src/rscr_logic.c"
EDITS = {
    # R-SIGN: at the end of the idle time the recording screen goes dark instead of dimming to SCR_REC_DIM
    "rsign_dark": (L, "\t\tif (recording) {\n\t\t\ts->screen = SCR_REC_DIM;\n\t\t}", "\t\tif (recording) {\n\t\t\ts->screen = SCR_OFF;\n\t\t}",
                   "test_rsign_recording_never_dark"),
    # R-SIGN at the drawing layer: the panel is blanked while SCR_REC_DIM is shown
    "rsign_blank_panel": ("src/rscr.c", "want_on = frame.s.screen != SCR_OFF;", "want_on = frame.s.screen != SCR_OFF && frame.s.screen != SCR_REC_DIM;",
                          "test_04_recording_screens_and_sign"),
    # the lock does not hold: the screen counts as lit when it is off
    "lock_open": (L, "\treturn full || s->session;", "\treturn (full || s->session) || true;", "test_lock_first_event_only_wakes"),
    # a double press does not close the control session
    "double_ignored": (L, "if (last_event == RC_EV_DOUBLE_PRESS && s->session) {", "if (false) {",
                       "test_session_open_and_double_press_closes"),
    # a long press (recording starts) closes the control session
    "long_closes_session": (L, "\t\tleave_pair(s, fx);\n\t\ts->highlights = 0;", "\t\tleave_pair(s, fx);\n\t\tclose_session(s, v, fx, now);\n\t\ts->highlights = 0;",
                            "test_long_press_does_not_close_a_session"),
    # Down in a list does not move the selection
    "down_stuck": (L, "} else if (*sel + 1 < n) {", "} else if (false) {", "test_table_every_screen_every_action"),
    # the dismiss on the notification detail asks for the positive action
    "dismiss_key": (L, "fx_push(fx, FX_NOTIF_DISMISS, 0, s->notif_uid);", "fx_push(fx, FX_NOTIF_POSITIVE, 0, s->notif_uid);",
                    "test_table_every_screen_every_action"),
    # finding 1: SCR_REC_DIM is driven at brightness 0, not at the lowest level
    "dim_brightness_zero": (L, "return s->screen == SCR_REC_DIM ? RSCR_LEVEL_LOWEST :", "return s->screen == SCR_REC_DIM ? 0 :",
                            "test_04_recording_screens_and_sign"),
    # finding 3: the panel is blanked after the draw while SCR_REC_DIM is shown (the draw still happens)
    "blank_after_draw": ("src/rscr.c", "\tif (want_on != panel_on_state || level != panel_level) {",
                         "\tif (frame.s.screen == SCR_REC_DIM) {\n\t\t(void)rscr_panel(false, level);\n\t}\n\tif (want_on != panel_on_state || level != panel_level) {",
                         "test_04_recording_screens_and_sign"),
    # finding 2: one wrong passkey digit and one wrong timer digit
    "wrong_passkey_digit": ("src/rscr_draw.c", "(unsigned)(f->s.passkey % 1000));", "(unsigned)(f->s.passkey % 1000) + 1);",
                            "test_09_pairing_passkey"),
    "wrong_timer_digit": ("src/rscr_draw.c", "(unsigned)(s / 3600), (unsigned)((s / 60) % 60), (unsigned)(s % 60));",
                          "(unsigned)(s / 3600), (unsigned)((s / 60) % 60), (unsigned)((s % 60) + 1));",
                          "test_04_recording_screens_and_sign"),
    # a notification with no title shows its app identifier on the detail screen
    "no_title_app": ("src/rscr_draw.c", "text_w(r, it->title[0] != '\\0' ? it->title : \"Notification\", F16,",
                     "text_w(r, it->title[0] != '\\0' ? it->title : it->app, F16,",
                     "test_16_notification_without_a_title_shows_the_word_notification"),
    # rscr_sign_start draws on its caller's thread instead of handing the draw to the screens thread
    "sign_on_caller_thread": ("src/rscr.c", "\twake_thread();\n\tif (k_sem_take(&sign_done, K_MSEC(CONFIG_RING_SCREENS_SIGN_WAIT_MS)) == 0) {",
                              "\tdo_sign_start();\n\tif (k_sem_take(&sign_done, K_MSEC(CONFIG_RING_SCREENS_SIGN_WAIT_MS)) == 0) {",
                              "test_11_sign_start_is_drawn_by_the_screens_thread"),
    # round 3, new fault 1: a timed-out rscr_sign_start keeps its request (the thread draws it later)
    "sign_timeout_keeps_request": ("src/rscr.c", "\t\tif (sign_req.waiting == id) {\n\t\t\tsign_req.waiting = 0;\n\t\t\tsign_req.pending = false;\n\t\t\trc = -ETIMEDOUT;",
                                   "\t\tif (true) {\n\t\t\trc = -ETIMEDOUT;",
                                   "test_17_a_timed_out_sign_start_is_cancelled_and_never_drawn_later"),
    # round 3, new fault 2: FX_POWER_OFF is sent in every state
    "power_off_outside_standby": (L, "\t\t\t\tif (v->core_state == RC_ST_STANDBY) {\n\t\t\t\t\tfx_push(fx, FX_POWER_OFF, 0, 0);",
                                  "\t\t\t\tif (true) {\n\t\t\t\t\tfx_push(fx, FX_POWER_OFF, 0, 0);", "test_power_off_only_in_standby"),
    # software step 6 (U9): the current limit turns the screen off in RECORDING instead of dimming it (R-SIGN broken by the new call)
    "ilim_dark_in_recording": (L, "\t\ts->screen = SCR_REC_DIM;   /* R-SIGN: dimmed, never dark */", "\t\ts->screen = SCR_OFF;   /* R-SIGN: dimmed, never dark */",
                               "test_ilim_dim_never_dark_in_recording"),
    # software step 6 (U9, lead's ruling): a recording sign started in the current-limit hold is drawn at full brightness
    "start_in_hold_full_bright": (L, "\ts->screen = hold ? SCR_REC_DIM : SCR_RECORDING;   /* the sign at the start: dimmed in the hold */",
                                  "\ts->screen = SCR_RECORDING;   /* the sign at the start: dimmed in the hold */",
                                  "test_start_during_ilim_hold_draws_dim_sign"),
    # software step 6 (U9): the factory frame for red is drawn green
    "factory_wrong_colour": ("src/rscr_draw.c", "\tcase FAC_RED:\n\t\tlv_obj_set_style_bg_color(r, lv_color_make(255, 0, 0), 0);",
                             "\tcase FAC_RED:\n\t\tlv_obj_set_style_bg_color(r, lv_color_make(0, 255, 0), 0);", "test_factory_colours"),
    # the passkey digits are not drawn
    "passkey_not_drawn": ("src/rscr_draw.c", "\tif (f->s.pair_has_key) {", "\tif (false) {", "test_09_pairing_passkey"),
}
if variant not in EDITS:
    print("unknown variant", variant, file=sys.stderr)
    sys.exit(2)
rel, old, new, expect = EDITS[variant]
f = dst / rel
s = f.read_text()
if s.count(old) != 1:
    print("the edit did not match exactly once:", s.count(old), variant, file=sys.stderr)
    sys.exit(1)
f.write_text(s.replace(old, new))
print("EXPECT=" + expect)
print("edited", rel, file=sys.stderr)
