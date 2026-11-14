# Builds faulty copies of rst_hw_real.c (each breaks FW l.506 in the product) and runs the extracted ring-lines-safe
# check on each. Expected for each fake: the check FAILS (exit 1). A fake that passes is a hole in the check.
import subprocess, sys, os
src_path, out = sys.argv[1], sys.argv[2]
check = os.path.join(out, "ring_lines_check.py")
src = open(src_path).read()
LS_END = "\treturn c != 0 ? c : p;\n}\n"
fakes = {
    # A: a macro after lines_safe makes every wrapper call do nothing
    "macro-noop": src.replace(LS_END, LS_END + "#define lines_safe() 0\n", 1),
    # B: SD_CS driven high, the word GPIO_DISCONNECTED kept in a cast
    "cs-driven-high": src.replace("int c = gpio_pin_configure_dt(&sd_cs, GPIO_DISCONNECTED);",
                                  "int c = gpio_pin_configure_dt(&sd_cs, GPIO_OUTPUT_ACTIVE); (void)GPIO_DISCONNECTED;", 1),
    # C: default pin state re-applied after the sleep state inside lines_safe
    "default-after-sleep": src.replace("int p = pinctrl_apply_state(spi00_pins, PINCTRL_STATE_SLEEP);",
                                       "int p = pinctrl_apply_state(spi00_pins, PINCTRL_STATE_SLEEP); (void)pinctrl_apply_state(spi00_pins, PINCTRL_STATE_DEFAULT);", 1),
    # D: a second table registered whose suspend skips lines_safe
    "second-table": src.replace("static int rst_hw_real_register(void)\n{\n\tint r = rhw_register_disk(&real_disk);\n\n\treturn r != 0 ? r : rhw_register_sdbus(&real_sdbus);",
                                "static int b_off(void) { return 0; }\nstatic const struct rhw_sdbus_api other = { .suspend = b_off, .resume = b_resume };\nstatic int rst_hw_real_register(void)\n{\n\tint r = rhw_register_disk(&real_disk);\n\n\treturn r != 0 ? r : rhw_register_sdbus(&other);", 1),
    # E: resume_inner drives the lines when the first init fails (no rail check), honest shape kept
    "honest-control": src,
}
for name, text in fakes.items():
    if name != "honest-control" and text == src:
        print("%s: PLANT FAILED (text not found)" % name)
        continue
    p = os.path.join(out, "fake-" + name + ".c")
    open(p, "w").write(text)
    r = subprocess.run([sys.executable, "-I", check, p], capture_output=True, text=True)
    open(p + ".log", "w").write(r.stdout + r.stderr)
    last = (r.stdout.strip().splitlines() or ["<no output>"])[-1]
    print("%s: exit %d: %s" % (name, r.returncode, last))
