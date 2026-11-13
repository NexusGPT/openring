/*
 * rmo_hw_real.c: the real MOTOR output of the motor unit (software step 6, unit U6). Development kit build only
 * (decision D15): it compiles when the devicetree has an alias `ring-motor` that names a GPIO. Otherwise it is empty
 * and the motor interface of ring_rhw stays "absent". NOT PROVEN: no simulated build compiles it and no test runs it
 * (step 6 plan section 7). No chip pin is named here; the pin comes from the board's devicetree (step 7). Written for
 * this project.
 */
#include <zephyr/devicetree.h>

#if DT_NODE_EXISTS(DT_ALIAS(ring_motor))

#include <errno.h>

#include <zephyr/drivers/gpio.h>
#include <zephyr/init.h>

#include <ring_rhw/rhw.h>

static const struct gpio_dt_spec motor = GPIO_DT_SPEC_GET(DT_ALIAS(ring_motor), gpios);

/* MOTOR high = U11 enabled = motor on; low = off. A plain level, never PWM (FW l.314). */
static int r_set(bool high)
{
	return gpio_pin_set_dt(&motor, high ? 1 : 0);
}

static const struct rhw_motor_api real_motor = { .set = r_set };

static int rmo_real_init(void)
{
	if (!gpio_is_ready_dt(&motor)) {
		return -ENODEV;
	}
	int err = gpio_pin_configure_dt(&motor, GPIO_OUTPUT_INACTIVE);

	if (err != 0) {
		return err;
	}
	return rhw_register_motor(&real_motor);
}

SYS_INIT(rmo_real_init, APPLICATION, 50);

#endif
