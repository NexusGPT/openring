/* main.c: build-only application for tests/xfer/real_build (unit U4): refers to the thin part and to the real file's
 * marker so that both are linked. Never run. */
#include <stdbool.h>
#include <zephyr/kernel.h>

#include <ring_rhw/rhw.h>
#include <ring_xfer/rxf.h>

extern const bool rxf_hw_real_compiled;

int main(void)
{
	int (*start)(const struct rxf_backend *, const struct rxf_cb *) = rxf_start;

	printk("rxf_start %p real compiled %d\n", (void *)start, rxf_hw_real_compiled);
	/* the instance behind rhw_usb(): the real one answers 0 when the stack starts, the "absent" one -ENODEV */
	printk("rhw_usb enable returned %d\n", rhw_usb()->enable());
	return 0;
}
