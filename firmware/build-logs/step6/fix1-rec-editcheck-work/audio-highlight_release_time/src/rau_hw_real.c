/*
 * rau_hw_real.c: the real microphone input, clock pins and HFXO request of the audio unit (software step 6, unit U3).
 * Development kit build only (decision D15): it compiles when the devicetree has the node `pdm20` enabled, otherwise
 * it is empty and the interfaces of ring_rhw stay "absent" (-ENODEV). NOT PROVEN: no simulated build compiles it and
 * no test runs it (step 6 plan section 7). Kit facts K1, K7, K8 of the plan are in firmware/docs/audio-notes.md.
 * No chip pin is named here; the pins come from the board's devicetree (step 7). Written for this project.
 */
#include <zephyr/devicetree.h>

#if DT_NODE_HAS_STATUS(DT_NODELABEL(pdm20), okay)

#include <errno.h>

#include <zephyr/audio/dmic.h>
#include <zephyr/device.h>
#include <zephyr/drivers/clock_control/nrf_clock_control.h>
#include <zephyr/drivers/pinctrl.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/onoff.h>

#include <ring_rhw/rhw.h>

#define PDM_NODE DT_NODELABEL(pdm20)

PINCTRL_DT_DEFINE(PDM_NODE);
static const struct pinctrl_dev_config *const pcfg = PINCTRL_DT_DEV_CONFIG_GET(PDM_NODE);
static const struct device *const pdm = DEVICE_DT_GET(PDM_NODE);

K_MEM_SLAB_DEFINE_STATIC(slab, RREC_BLOCK_BYTES, RREC_BLOCK_COUNT, 4);

static int r_configure(const struct rhw_mic_cfg *cfg)
{
	struct pcm_stream_cfg stream = {
		.pcm_rate = cfg->pcm_rate,
		.pcm_width = cfg->pcm_width,
		.block_size = cfg->block_size,
		.mem_slab = &slab,
	};
	struct dmic_cfg dc = {
		.io = {
			.min_pdm_clk_freq = cfg->min_pdm_clk_hz,
			.max_pdm_clk_freq = cfg->max_pdm_clk_hz,
		},
		.streams = &stream,
		.channel = {
			.req_num_streams = 1,
			.req_num_chan = cfg->channels,
			/* channel 0 = mic 1 on the left, channel 1 = mic 2 on the right (FW l.414) */
			.req_chan_map_lo = dmic_build_channel_map(0, 0, PDM_CHAN_LEFT) |
					   dmic_build_channel_map(1, 0, PDM_CHAN_RIGHT),
		},
	};

	return dmic_configure(pdm, &dc);
}

static int r_start(void)
{
	return dmic_trigger(pdm, DMIC_TRIGGER_START);
}

static int r_stop(void)
{
	return dmic_trigger(pdm, DMIC_TRIGGER_STOP);
}

static int r_read(void **block, size_t *size, int32_t timeout_ms)
{
	return dmic_read(pdm, 0, block, size, timeout_ms);
}

static void r_free(void *block)
{
	k_mem_slab_free(&slab, block);
}

static int r_pins_sleep(void)
{
	return pinctrl_apply_state(pcfg, PINCTRL_STATE_SLEEP);
}

static int r_pins_default(void)
{
	return pinctrl_apply_state(pcfg, PINCTRL_STATE_DEFAULT);
}

static const struct rhw_mic_api real_mic = {
	.configure = r_configure, .start = r_start, .stop = r_stop, .read = r_read, .free_block = r_free,
	.pins_sleep = r_pins_sleep, .pins_default = r_pins_default,
};

/* HFXO through the kit's clock control on-off service (FW l.428) */
static struct onoff_manager *hf_mgr;
static struct onoff_client hf_cli;
static void (*hf_running_cb)(void);
static bool hf_is_running;
static uint32_t hf_requests;

static void hf_done(struct onoff_manager *mgr, struct onoff_client *cli, uint32_t state, int res)
{
	ARG_UNUSED(mgr);
	ARG_UNUSED(cli);
	ARG_UNUSED(state);
	if (res == 0) {
		hf_is_running = true;
		if (hf_running_cb != NULL) {
			hf_running_cb();
		}
	}
}

static int r_hf_request(void (*running)(void))
{
	if (hf_requests++ > 0) {
		if (running != NULL && hf_is_running) {
			running();
		}
		return 0;
	}
	hf_running_cb = running;
	hf_is_running = false;
	sys_notify_init_callback(&hf_cli.notify, hf_done);
	return onoff_request(hf_mgr, &hf_cli) < 0 ? -EIO : 0;
}

static int r_hf_release(void)
{
	if (hf_requests == 0) {
		return -EALREADY;
	}
	if (--hf_requests == 0) {
		hf_is_running = false;
		return onoff_release(hf_mgr) < 0 ? -EIO : 0;
	}
	return 0;
}

static bool r_hf_running(void)
{
	return hf_is_running;
}

static const struct rhw_hfxo_api real_hfxo = {
	.request = r_hf_request, .release = r_hf_release, .running = r_hf_running,
};

static int rau_hw_real_init(void)
{
	hf_mgr = z_nrf_clock_control_get_onoff(CLOCK_CONTROL_NRF_SUBSYS_HF);
	rhw_register_mic(&real_mic);
	rhw_register_hfxo(&real_hfxo);
	return 0;
}
SYS_INIT(rau_hw_real_init, APPLICATION, 90);

#endif /* pdm20 enabled */
