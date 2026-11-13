/*
 * Key values of the scenes. A region of a frame is compared, pixel for pixel, with the same text drawn alone by the same code
 * (rscr_ref_text: the screens' own label helpers and fonts, on a flat background). So a wrong time, timer, passkey digit,
 * percent, count or message text fails its scene, and the frame of another scene fails too. Every text, colour, position and
 * region below is a literal written here. Included by test_draw.c only.
 */
#ifndef TEST_REFS_H
#define TEST_REFS_H

#define WHITE  0xF0F0EE
#define GREY   0x8C8C8A
#define DIMC   0x50504E
#define REDC   0xFF3B30
#define GREENC 0x30D158
#define AMBERC 0xFFB000
#define PILLON 0xECE6DA
#define PILLC  0x262624
#define BLK    0x000000

struct vref {
	const char *txt;
	uint8_t font;
	uint32_t fg, bg;
	int16_t x, y, w;
	uint8_t align;     /* 0 left, 1 centre, 2 right */
	bool wrap;
	int16_t rx0, ry0, rx1, ry1;   /* the region compared */
	uint8_t *cache;
};

#define VR(t, f, fg, bg, x, y, w, al, wr, x0, y0, x1, y1) { t, f, fg, bg, x, y, w, al, wr, x0, y0, x1, y1, NULL }

static uint8_t refpool[1536 * 1024];
static size_t refpool_used;
static uint8_t refpic[RSCR_W * RSCR_H * 3];

static const uint8_t *ref_bits(struct vref *v)
{
	size_t n = (size_t)(v->rx1 - v->rx0 + 1) * (v->ry1 - v->ry0 + 1) * 3;

	if (v->cache == NULL) {
		zassert_true(refpool_used + n <= sizeof(refpool), "reference pool");
		rscr_ref_text(v->txt, v->font, v->fg, v->bg, v->x, v->y, v->w, v->align, v->wrap);
		rscr_capture_rgb(refpic);
		v->cache = &refpool[refpool_used];
		refpool_used += n;
		for (int y = v->ry0; y <= v->ry1; y++) {
			memcpy(v->cache + (size_t)(y - v->ry0) * (v->rx1 - v->rx0 + 1) * 3, &refpic[(y * RSCR_W + v->rx0) * 3],
			       (size_t)(v->rx1 - v->rx0 + 1) * 3);
		}
	}
	return v->cache;
}

/* the region of the frame p is identical to the text drawn alone */
static bool vmatch(const uint8_t *p, struct vref *v)
{
	const uint8_t *r = ref_bits(v);
	size_t rowlen = (size_t)(v->rx1 - v->rx0 + 1) * 3;

	for (int y = v->ry0; y <= v->ry1; y++) {
		if (memcmp(&p[(y * RSCR_W + v->rx0) * 3], r + (size_t)(y - v->ry0) * rowlen, rowlen) != 0) {
			return false;
		}
	}
	return true;
}

static struct vref v_status[] = {
	VR("10:42", 32, WHITE, BLK, 18, 12, 0, 0, false, 18, 12, 118, 52),
	VR("Ready", 16, GREY, BLK, 18, 56, 0, 0, false, 18, 56, 70, 76),
};
static struct vref v_menu[] = {
	VR("Recordings", 16, BLK, PILLON, 22, 19, 196, 0, false, 22, 19, 150, 38),
	VR("Control", 16, WHITE, BLK, 22, 49, 196, 0, false, 22, 49, 150, 68),
	VR("Devices", 16, WHITE, BLK, 22, 79, 196, 0, false, 22, 79, 150, 98),
};
static struct vref v_settings[] = {
	VR("Settings", 14, GREY, BLK, 18, 10, 0, 0, false, 18, 10, 100, 27),
	VR("Brightness", 16, BLK, PILLON, 22, 33, 130, 0, false, 22, 33, 140, 52),
	VR("3 of 3", 16, DIMC, PILLON, 150, 33, 66, 2, false, 150, 33, 215, 52),
	VR("Vibration", 16, WHITE, BLK, 22, 58, 130, 0, false, 22, 58, 140, 77),
	VR("On", 16, GREY, BLK, 150, 58, 66, 2, false, 150, 58, 215, 77),
	VR("Time format", 16, WHITE, BLK, 22, 83, 130, 0, false, 22, 83, 140, 102),
	VR("24 h", 16, GREY, BLK, 150, 83, 66, 2, false, 150, 83, 215, 102),
};
static struct vref v_recording_idle[] = {
	VR("00:12:47", 16, DIMC, BLK, 122, 82, 100, 2, false, 122, 82, 221, 100),
};
static struct vref v_recording[] = {
	VR("Recording", 16, WHITE, BLK, 38, 82, 0, 0, false, 38, 82, 120, 100),
	VR("00:12:47", 16, GREY, BLK, 122, 82, 100, 2, false, 122, 82, 221, 100),
};
static struct vref v_recording_highlight[] = {
	VR("Recording", 16, WHITE, BLK, 38, 82, 0, 0, false, 38, 82, 120, 100),
	VR("00:12:49", 16, GREY, BLK, 122, 82, 100, 2, false, 122, 82, 221, 100),
	VR("1 marked", 14, GREY, BLK, 18, 62, 204, 2, false, 18, 62, 221, 80),
};
static struct vref v_notifs_empty[] = {
	VR("Notifications", 14, GREY, BLK, 18, 14, 0, 0, false, 18, 14, 130, 32),
	VR("None", 16, WHITE, BLK, 18, 50, 0, 0, false, 18, 50, 60, 70),
};
static struct vref v_notifs[] = {
	VR("Notifications 2", 14, GREY, BLK, 18, 10, 0, 0, false, 18, 10, 140, 27),
	VR("Weekly report", 16, BLK, PILLON, 28, 33, 190, 0, false, 28, 33, 150, 52),
	VR("Grace Lin", 16, WHITE, BLK, 28, 58, 190, 0, false, 28, 58, 150, 77),
};
static struct vref v_notif[] = {
	VR("Grace Lin", 16, WHITE, BLK, 44, 11, 178, 0, false, 44, 11, 150, 30),
	VR("Any update on the hero shot?", 14, GREY, BLK, 18, 36, 204, 0, true, 18, 36, 221, 70),
};
static struct vref v_modes[] = {
	VR("Control", 14, GREY, BLK, 18, 10, 0, 0, false, 18, 10, 100, 27),
	VR("Media", 16, BLK, PILLON, 22, 33, 196, 0, false, 22, 33, 150, 52),
	VR("Presenter", 16, WHITE, BLK, 22, 58, 196, 0, false, 22, 58, 150, 77),
	VR("Pointer", 16, WHITE, BLK, 22, 83, 196, 0, false, 22, 83, 150, 102),
};
#define HINT VR("Press twice to leave", 14, DIMC, BLK, 18, 88, 0, 0, false, 18, 88, 200, 106)
static struct vref v_ctl_media[] = {
	VR("Media", 16, WHITE, BLK, 18, 10, 0, 0, false, 18, 10, 100, 28),
	VR("Night Drive", 16, WHITE, BLK, 18, 34, 204, 0, false, 18, 34, 221, 52),
	HINT,
};
static struct vref v_ctl_presenter[] = {
	VR("Presenter", 16, WHITE, BLK, 18, 10, 0, 0, false, 18, 10, 110, 28),
	VR("Slides", 16, WHITE, BLK, 18, 34, 0, 0, false, 18, 34, 100, 52),
	HINT,
};
static struct vref v_ctl_pointer[] = {
	VR("Pointer", 16, WHITE, BLK, 18, 10, 0, 0, false, 18, 10, 110, 28),
	VR("Move and click", 16, WHITE, BLK, 18, 34, 0, 0, false, 18, 34, 160, 52),
	HINT,
};
static struct vref v_ctl_agent[] = {
	VR("Agent", 16, WHITE, BLK, 18, 10, 0, 0, false, 18, 10, 110, 28),
	VR("Answer a request", 16, WHITE, BLK, 18, 34, 0, 0, false, 18, 34, 180, 52),
	VR("Decline", 16, REDC, BLK, 18, 66, 0, 0, false, 18, 66, 100, 84),
	VR("Accept", 16, GREENC, BLK, 130, 66, 92, 2, false, 130, 66, 221, 84),
	HINT,
};
static struct vref v_devices[] = {
	VR("Devices", 14, GREY, BLK, 18, 14, 0, 0, false, 18, 14, 100, 31),
	VR("Phone", 14, WHITE, PILLC, 17, 56, 62, 1, false, 27, 56, 69, 72),
	VR("Laptop", 14, BLK, PILLON, 89, 56, 62, 1, false, 99, 56, 141, 72),
	VR("Tablet", 14, WHITE, PILLC, 161, 56, 62, 1, false, 171, 56, 213, 72),
};
static struct vref v_device[] = {
	VR("Laptop", 16, WHITE, BLK, 18, 10, 204, 0, false, 18, 10, 150, 29),
	VR("Use", 16, BLK, PILLON, 22, 44, 0, 0, false, 22, 44, 70, 63),
	VR("Remove", 16, WHITE, BLK, 22, 74, 0, 0, false, 22, 74, 110, 93),
};
static struct vref v_confirm[] = {
	VR("Remove Laptop?", 16, WHITE, BLK, 18, 12, 204, 0, false, 18, 12, 221, 31),
	VR("Yes: short press centre", 14, GREENC, BLK, 18, 56, 0, 0, false, 18, 56, 200, 73),
	VR("No: left", 14, GREY, BLK, 18, 80, 0, 0, false, 18, 80, 100, 97),
};
static struct vref v_pairing[] = {
	VR("Pair", 14, GREY, BLK, 18, 12, 0, 0, false, 18, 12, 60, 29),
	VR("482 913", 32, WHITE, BLK, 18, 36, 0, 0, false, 18, 36, 150, 76),
	VR("50 s", 14, GREY, BLK, 18, 88, 204, 2, false, 18, 88, 221, 106),
};
static struct vref v_charging[] = {
	VR("64%", 28, WHITE, BLK, 18, 10, 0, 0, false, 18, 10, 100, 44),
	VR("Charging", 16, GREY, BLK, 18, 50, 0, 0, false, 18, 50, 110, 70),
	VR("38 min", 14, GREY, BLK, 54, 86, 0, 0, false, 54, 86, 110, 104),
};
static struct vref v_message[] = {
	VR("In case", 16, WHITE, BLK, 18, 30, 204, 0, true, 18, 30, 221, 52),
};
static struct vref v_message_bl[] = {
	VR("Battery low", 16, AMBERC, BLK, 18, 30, 204, 0, true, 18, 30, 221, 52),
};

struct scene {
	const char *name;
	struct vref *refs;
	int n;
};
#define SC(nm, arr) { nm, arr, ARRAY_SIZE(arr) }
/* the 21 pictures, in the order the test saves them */
static struct scene scenes[] = {
	SC("status", v_status), SC("menu", v_menu), SC("settings", v_settings), SC("recording-idle", v_recording_idle),
	SC("recording", v_recording), SC("recording-highlight", v_recording_highlight),
	SC("notifications-empty", v_notifs_empty), SC("notifications", v_notifs), SC("notification", v_notif),
	SC("modes", v_modes), SC("control-media", v_ctl_media), SC("control-presenter", v_ctl_presenter),
	SC("control-pointer", v_ctl_pointer), SC("control-agent", v_ctl_agent), SC("devices", v_devices),
	SC("device", v_device), SC("confirm", v_confirm), SC("pairing", v_pairing), SC("charging", v_charging),
	SC("message", v_message), SC("message-battery-low", v_message_bl),
};
#define NSCENES ARRAY_SIZE(scenes)
static uint8_t scene_pic[NSCENES][RSCR_W * RSCR_H * 3];
static bool scene_have[NSCENES];

static int scene_index(const char *name)
{
	for (unsigned i = 0; i < NSCENES; i++) {
		if (strcmp(scenes[i].name, name) == 0) {
			return (int)i;
		}
	}
	return -1;
}

/* every key value of scene i is in the frame p */
static bool scene_ok(int i, const uint8_t *p)
{
	for (int k = 0; k < scenes[i].n; k++) {
		if (!vmatch(p, &scenes[i].refs[k])) {
			return false;
		}
	}
	return true;
}

#endif
