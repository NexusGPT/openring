/*
 * Ring screens, drawing part: draws one screen with LVGL in a 240 x 120 frame (landscape, the picture the wearer
 * sees) and turns the frame for the 120 x 240 panel in one function (the display flush, rscr_to_panel()).
 */
#ifndef RING_SCREENS_RSCR_DRAW_H
#define RING_SCREENS_RSCR_DRAW_H

#include <ring_iphone/ripl.h>
#include <ring_screens/rscr_logic.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RSCR_W 240
#define RSCR_H 120

/* Everything one picture needs: the pure state, the view, and the data read from the other modules. */
struct rscr_frame {
	rc_ms_t now;
	struct rscr s;
	struct rscr_view v;
	bool time_set;
	uint8_t hh, mm;           /* wall time (ring_time, with the zone) */
	uint32_t elapsed_s;       /* seconds since the recording started */
	uint8_t batt_pct;
	bool charging, full;
	uint16_t to_full_min;
	char dev_name[RDEV_SLOTS][17];
	struct ripl_media media;
	bool ams_ready;
	struct rinbox_item inbox[RINBOX_MAX];
	uint8_t err_code;         /* event log code of the error screen (the core state number) */
};

/* Start LVGL and the display. 0 or a negative errno. */
int rscr_draw_init(void);
/* Draw the frame and push it to the display now. 0, or -EIO when the display refused a write. */
int rscr_draw(const struct rscr_frame *f);
/* Panel on or off (display blanking) */
int rscr_panel(bool on, uint8_t brightness);

#ifdef __cplusplus
}
#endif

#endif
