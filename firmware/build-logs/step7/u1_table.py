#!/usr/bin/env python3
"""Prints the table of bar 5: every U1 row of the netlist | chip pin | devicetree node or property | driver file | status.
Usage: python3 u1_table.py <netlist.csv> <tools/check_ring_pins.py>
The devicetree place of each signal is read from the check's own table (SIGNALS, NO_NODE_BY_NATURE), so the table and
the check cannot disagree; the driver column is USERS below (from the sources named there)."""
import csv
import importlib.util
import sys

net_path, chk_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("chk", chk_path)
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

J = ("none: no joystick driver exists (app/src/main.c l.13-14: \"the driver calls rglue_input()\", "
     "not written); kit gpio-keys driver not enabled (CONFIG_INPUT off)", "not used yet")
LCD = ("none: no panel driver (the memory display stands in, modules/ring_screens/src/memdisplay.c); "
       "the MIPI DBI node has no driver (CONFIG_MIPI_DBI off)", "not used yet")
UNUSED = ("none, by design: a test pad the firmware never configures (design/firmware.md l.77)", "not used yet")
PMIC = ("kit mfd_npm13xx.c, i2c_nrfx_twim.c (rpw_hw_real.c would use it: not compiled, CONFIG_RING_POWER_REAL=n)",
        "builds only")
SD = ("modules/ring_store/src/rst_hw_real.c through kit sdhc_spi.c, spi_nrfx_spim.c", "builds only")
MIC = ("modules/ring_audio/src/rau_hw_real.c through kit dmic_nrfx_pdm.c", "builds only")
USERS = {
    "BTN_REC": J, "JOY_UP": J, "JOY_DOWN": J, "JOY_LEFT": J, "JOY_RIGHT": J,
    "MOTOR": ("modules/ring_motor/src/rmo_hw_real.c (alias ring-motor)", "builds only"),
    "LCD_CS": LCD, "LCD_DCX": LCD, "LCD_RST": LCD, "LCD_TE": LCD, "LCD_SCK": LCD, "LCD_MOSI": LCD,
    "OLED_PWR_EN": ("none: no screen supply code (zephyr,user property only)", "not used yet"),
    "PMIC_INT": PMIC, "PMIC_SDA": PMIC, "PMIC_SCL": PMIC,
    "SD_CS": SD, "SD_SCK": SD, "SD_MOSI": SD, "SD_MISO": SD,
    "MIC_A_CLK": MIC, "MIC_A_DATA": MIC,
    "MIC_B_DATA": UNUSED, "SPARE_P1_00": UNUSED, "SPARE_P2_00": UNUSED, "SPARE_P3_03": UNUSED, "SPARE_P3_04": UNUSED,
    "DBG_TX": ("kit uart_nrfx_uarte.c (the console)", "builds only"),
    "XL1": ("kit clock control (LFXO, the GRTC's clock)", "builds only"),
    "XL2": ("kit clock control (LFXO, the GRTC's clock)", "builds only"),
    "XC1": ("kit clock control (HFXO); rau_hw_real.c requests it", "builds only"),
    "XC2": ("kit clock control (HFXO); rau_hw_real.c requests it", "builds only"),
    "USB_DP": ("modules/ring_xfer/src/rxf_hw_real.c through kit udc_dwc2.c", "builds only"),
    "USB_DN": ("modules/ring_xfer/src/rxf_hw_real.c through kit udc_dwc2.c", "builds only"),
    "U1_VBUS": ("modules/ring_xfer/src/rxf_hw_real.c through kit udc_dwc2.c", "builds only"),
    "ANT1_NODE": ("kit Bluetooth controller (radio)", "builds only"),
}

print("| U1 net | ball | chip pin | devicetree node or property | used by which driver file | status |")
print("|---|---|---|---|---|---|")
n = 0
for r in csv.DictReader(open(net_path, newline="")):
    if r["reference"] != "U1":
        continue
    n += 1
    net, ball, pin = r["net"], r["pin_number"], r["pin_name"]
    if net == "":
        print("| (no net) | %s | %s | none | none | not connected on the ring board |" % (ball, pin))
        continue
    if net in chk.NO_NODE_BY_NATURE:
        print("| %s | %s | %s | none (%s) | none | no node by nature |" % (net, ball, pin, chk.NO_NODE_BY_NATURE[net]))
        continue
    kind, where, what = chk.SIGNALS[net]
    if kind == "gpio":
        place = "`%s` property `%s`" % (where, what)
    elif kind == "psel":
        place = "`%s` pin control, function `%s` (default and sleep)" % (where, what)
    else:
        place = "`%s` (fixed function of the chip)" % where
    users, status = USERS[net]
    print("| %s | %s | %s | %s | %s | %s |" % (net, ball, pin, place, users, status))
print()
print("u1_table: %d rows of U1" % n)
