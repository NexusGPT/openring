"""Decks of the case tests, written from the case netlist.csv and parts.csv (same rules as make_decks.py)."""
from circuit_lib import Deck, node, parse_value

OPT = ".options reltol=1e-4 abstol=1e-12 vntol=1e-7"

# numbers not in the circuit files, each with its source
# Forward current against forward voltage of the three dies, read by me from the typical curves of design/datasheets/case_kb_aptf1616.pdf page 3
# (graphs "Forward Current vs. Forward Voltage", Ta 25 C; reading error about plus or minus 0.15 V). Pairs (volt, ampere); the first pair
# (0, 0) and the second (the start of conduction) make the current exactly zero below the start of the curve.
# Cross-check with the table of page 2: the curves pass through the typical VF at 20 mA (red 2.0 V, green 3.3 V, blue 3.3 V).
LED_CURVE = {
    "R": [(0.0, 0.0), (1.70, 0.0), (1.85, 0.002), (1.93, 0.005), (2.00, 0.020), (2.06, 0.030)],
    "G": [(0.0, 0.0), (2.50, 0.0), (2.75, 0.002), (3.00, 0.005), (3.30, 0.020), (3.45, 0.025)],
    "B": [(0.0, 0.0), (2.40, 0.0), (2.70, 0.002), (2.85, 0.005), (3.30, 0.020), (3.50, 0.030)],
}
# ESP32-S3-MINI-1 datasheet p27 (case_esp32s3_mini1.pdf): VOL 0.495 V at IOL 28 mA (VDD 3.3 V, PAD_DRIVER 3) gives the pin's low-side resistance
PIN_R_LOW = 0.495 / 0.028
VT = 0.02585   # thermal voltage at 300 K, volts


def case_cell(dk, ocv, rcell):
    d = dk.d
    pos = node(d.net_of("BT1", "+"))
    neg = node(d.net_of("BT1", "-"))
    dk.add("* BT1 cell %s: open-circuit voltage and series resistance are parameters; internal impedance below 60 mohm (cell sheet p1)" % d.parts["BT1"]["value"])
    dk.add("Vocv cell_i %s DC %s" % (neg, ocv))
    dk.add("Rcellx cell_i %s %s" % (pos, rcell))
    dk.included.append(("BT1", "cell source + series resistance"))


def deck_boost(case):
    dk = Deck(case, "case test 1: cell to PMID boost (BQ25895 boost mode) to VRING through the current limit part U5")
    d = case
    dk.add(".param ocv=3.7")
    dk.add(".param acc=0")
    dk.add(".param corner=1")
    dk.add(".param load=0")
    dk.add(".param rshort=1e9")
    dk.lib("bq25895_boost.lib")
    dk.lib("tps2553.lib")
    dk.lib("tpd4e05u06.lib")
    nets = ["PMID", "VRING", "VRING_SENSE", "U5_ILIM", "VRING_EN", "VRING_FAULT_N", "3V3", "BAT"]
    dk.passives(nets, skip=["R5"])
    case_cell(dk, "{ocv}", 0.06)
    rk = parse_value(d.parts["R5"]["value"]) / 1000.0
    dk.add("* R5 (U5 ILIM resistor) = %s from parts.csv: the model reads it as the parameter rk (kohm)" % d.parts["R5"]["value"])
    dk.included.append(("R5", "value passed to the U5 model as rk"))
    dk.ic("U2", "BQ25895BOOST params: acc={acc}", ["BAT", "PMID"])
    dk.ic("U5", "TPS2553 params: rk=%.6g corner={corner}" % rk, ["IN", "OUT", "EN", "GND"])
    dk.ic("U6", "TPD4E05U06", ["D1+", "D1-", "D2+", "D2-", "GND"])
    dk.add("V3v3 %s 0 3.3 ; ESP32 side logic rail (3V3), the R17 pull-up and the enable come from the netlist" % node(d.net_of("U1", "3V3")))
    dk.add("Ven %s 0 3.3 ; U1 pin IO15 drives VRING_EN high" % node(d.net_of("U1", "IO15")))
    dk.add("Bload %s 0 I = load ; ring side load, constant current (the ring draws a fixed current at 5 V in this test)" % node(d.net_of("U5", "OUT")))
    dk.add("Rshortx %s 0 {rshort} ; short circuit on VRING" % node(d.net_of("U5", "OUT")))
    dk.add(OPT)
    dk.add(".op")
    dk.add(".control")
    dk.add("run")
    vr = node(d.net_of("U5", "OUT"))
    dk.add("echo RESULT vring.vring = $&v(%s)" % vr)
    dk.add("echo RESULT vring.iout = $&i(v.xu5.vs)")
    dk.add("echo RESULT vring.vsense = $&v(%s)" % node(d.net_of("R12", "2")))
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")
    return dk


def deck_charger(case):
    dk = Deck(case, "case test 2: BQ25895 enable line CE (pulled up by R21 to 3V3) against the charger's input thresholds, and the charge current with the register defaults when CE is low")
    d = case
    rilim = parse_value(d.parts["R11"]["value"])
    ce_net = d.net_of("U2", "CE")
    if d.net_of("U1", "IO18") != ce_net:
        raise KeyError("U1 IO18 is not on the net of U2 CE (%s)" % ce_net)
    rail = d.net_of("U3", "VOUT")
    dk.passives([ce_net, rail])
    n_ce = node(ce_net)
    dk.add("* power-on level of CE: R21 (netlist, parts.csv) from CE to the 3V3 rail; 3V3 source from the test (3.0 V lowest allowed by the module, p27)")
    dk.add(".param v33=3.0")
    dk.add("V33x %s 0 {v33}" % node(rail))
    dk.add("* CE input leakage 1 uA (BQ25895 p10 IIN_BIAS) plus the module pin's input current 50 nA (ESP32-S3-MINI-1 p27 IIH), both worst case pulling CE down")
    dk.add(".param ileak=1.05e-6")
    dk.add("Ileakx %s 0 DC {ileak}" % n_ce)
    dk.add("* module pin IO18 before the software drives it: high impedance with the internal weak pull-down 45 kohm (p27 RPD, worst case)")
    dk.add(".param rpd=45e3")
    dk.add("Rpdx %s 0 {rpd}" % n_ce)
    dk.add("* module pin driven low by the software: a source at VOL (0.1 x VDD, p27) through rdrv; rdrv = 1e12 means not driven")
    dk.add(".param rdrv=1e12")
    dk.add(".param vpin=0")
    dk.add("Rdrvx %s pinsrc {rdrv}" % n_ce)
    dk.add("Vpinx pinsrc 0 {vpin}")
    dk.add(".param vih=1.3 ; BQ25895 p10 input high threshold of CE")
    dk.add("* defaults of the BQ25895 registers, each with its page in pass-lines.md section B: ICHG 2.048 A (p36), VREG 4.208 V (p38), IINLIM 0.5 A (p32), KILIM 320 / 355 / 390 (p9)")
    dk.add(".param ichg_reg=2.048")
    dk.add(".param vreg=4.208")
    dk.add(".param iinlim=0.5")
    dk.add(".param rilim=%.6g ; R11 from parts.csv" % rilim)
    dk.add(".param eta=0.90 ; MODEL CHOICE, converter efficiency")
    dk.add(".param psys=0 ; no other load, the largest charge current")
    dk.included.append(("R11", "ILIM resistor, value read"))
    dk.add("* case cell at 3.7 V nominal with 60 mohm; VBUS 5 V from a USB source; input limit = min(register, ILIM pin KILIM/RILIM)")
    dk.add("Vbus vbus 0 5")
    dk.add("Vocv cell_i 0 3.7")
    dk.add("Rcellx cell_i nbat 0.06")
    dk.add(".param ilim_pin_min = {320/rilim}")
    dk.add(".param iin = {min(iinlim, ilim_pin_min)}")
    dk.add("* charge current from the input power: (eta * 5 V * iin - psys) / Vbat, clamped by the register ICHG and by the CV limit; charging only while V(CE) is below VIH (p4 and p21: charging is enabled when CE is low; between VIL and VIH the level is undefined and counts as charging, the worst case)")
    dk.add("Bchg2 0 nbat I = (v(%s) < {vih}) * min(ichg_reg, min(max((eta*5*iin - psys)/max(v(nbat),2.5), 0), max((vreg - v(nbat))*1000, 0)))" % n_ce)
    dk.add("Vn_ichg n_ichg 0 {ichg_reg}")
    dk.add("Vn_vreg n_vreg 0 {vreg}")
    dk.add("Vn_pin n_pin 0 {ilim_pin_min}")
    dk.add(OPT)
    dk.add(".op")
    dk.add(".control")
    dk.add("run")
    dk.add("let ichg_in = i(vocv)")
    dk.add("echo RESULT charge.ce_v = $&v(%s)" % n_ce)
    dk.add("echo RESULT charge.ichg_reg_default = $&v(n_ichg)")
    dk.add("echo RESULT charge.vreg_default = $&v(n_vreg)")
    dk.add("echo RESULT charge.ilim_pin_min = $&v(n_pin)")
    dk.add("echo RESULT charge.icc = $&ichg_in")
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")
    return dk


def deck_ts(case):
    dk = Deck(case, "case test 3: BQ25895 TS pin window with RT1, RT2 and the thermistor TH1 swept")
    d = case
    nets = ["REGN", "TS"]
    dk.passives(nets, skip=["TH1"])
    n_regn = node(d.net_of("U2", "REGN"))
    n_ts = node(d.net_of("U2", "TS"))
    dk.add("Vregn %s 0 5 ; REGN, any value: the thresholds are ratios of REGN (p9)" % n_regn)
    dk.add("Vrs rsw 0 DC 10000")
    dk.add("* TH1 (%s in parts.csv) replaced by a resistor of the value on node rsw, swept in ohm" % d.parts["TH1"]["value"])
    dk.add("Bth %s 0 I = v(%s) / max(v(rsw), 1)" % (n_ts, n_ts))
    dk.included.append(("TH1", "swept resistor, nominal value %g read from parts.csv" % parse_value(d.parts["TH1"]["value"])))
    dk.add(".dc Vrs 1000 60000 10")
    dk.add(".control")
    dk.add("run")
    dk.add("meas dc rcold when v(%s)=3.6625 cross=1" % n_ts)
    dk.add("meas dc rhot when v(%s)=2.2375 cross=1" % n_ts)
    dk.add("meas dc rhtf when v(%s)=2.4125 cross=1" % n_ts)
    dk.add("meas dc vts25 find v(%s) when v(rsw)=%g" % (n_ts, parse_value(d.parts["TH1"]["value"])))
    dk.add("let vts25r = vts25 / 5")
    dk.add("echo RESULT ts.cold_edge_rth = $&rcold")
    dk.add("echo RESULT ts.hot_edge_rth = $&rhot")
    dk.add("echo RESULT ts.htf_edge_rth = $&rhtf")
    dk.add("echo RESULT ts.vts_25c = $&vts25r")
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")
    return dk


def deck_led(case):
    dk = Deck(case, "case test 4: RGB LED currents from SYS through R8, R9, R10 with the ESP32 pins low (lit) or high (off)")
    d = case
    anode = d.net_of("LED1", "A")
    sys_net = d.net_of("U2", "SYS")
    rail = d.net_of("U3", "VOUT")
    drv = {col: d.net_of(ref, "1") for col, ref in (("R", "R8"), ("G", "R9"), ("B", "R10"))}
    cath = {col: d.net_of("LED1", pin) for col, pin in (("R", "K_R"), ("G", "K_G"), ("B", "K_B"))}
    for col, ref in (("R", "R8"), ("G", "R9"), ("B", "R10")):
        if d.net_of(ref, "2") != cath[col]:
            raise KeyError("%s pin 2 is not on the cathode net of its colour" % ref)
    dk.passives(list(drv.values()) + list(cath.values()))
    r3 = parse_value(d.parts["R3"]["value"])
    r4 = parse_value(d.parts["R4"]["value"])
    dk.add(".param vsys=3.5 ; SYS, set by the test: 3.5 V minimum system voltage (BQ25895 p35) to 4.35 V (lead's range)")
    dk.add(".param v33=%.6g ; 3V3 rail = 0.5 V x (1 + R3 / R4) with R3 = %s and R4 = %s from parts.csv" % (0.5 * (1 + r3 / r4), d.parts["R3"]["value"], d.parts["R4"]["value"]))
    dk.add(".param vshift=0 ; shift of the LED curves in volt (plus 0.15 V weakest die, minus 0.15 V strongest die; the reading error of the graphs)")
    dk.add(".param vdrv=0 ; level the U1 pins drive: 0 V lit, v33 off (the software drives them high at start-up)")
    dk.add(".param rpin=%.6g ; pin low-side resistance: VOL 0.495 V at IOL 28 mA (ESP32-S3-MINI-1 p27)" % PIN_R_LOW)
    dk.add("Vsysx %s 0 {vsys}" % node(sys_net))
    dk.add("V3v3 %s 0 {v33}" % node(rail))
    for col, ref in (("R", "R8"), ("G", "R9"), ("B", "R10")):
        dk.add("Vdrv_%s drv%s 0 {vdrv}" % (col, col))
        dk.add("Rpin_%s drv%s %s {rpin} ; U1 pin of %s" % (col, col, node(drv[col]), ref))
        pts = ", ".join("%g, %g" % (v, i) for v, i in LED_CURVE[col])
        dk.add("Bled_%s %s %s I = pwl(v(%s) - v(%s) - {vshift}, %s) ; %s die: curve of the sheet p3" % (col, node(anode), node(cath[col]), node(anode), node(cath[col]), pts, col))
    dk.included.append(("LED1", "three dies as curves"))
    dk.add(OPT)
    dk.add(".op")
    dk.add(".control")
    dk.add("run")
    for col in "RGB":
        dk.add("let i_%s = abs(i(vdrv_%s))" % (col, col))
    dk.add("echo RESULT led.red = $&i_R")
    dk.add("echo RESULT led.green = $&i_G")
    dk.add("echo RESULT led.blue = $&i_B")
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")
    return dk


def deck_rail(case):
    dk = Deck(case, "case test 5: 3V3 rail set by the feedback divider R3, R4 of U3 (TPS63802)")
    d = case
    dk.add(".param vfb=0.5")
    n_out = node(d.net_of("U3", "VOUT"))
    n_fb = node(d.net_of("U3", "FB"))
    dk.passives(["3V3", "FB"])
    dk.add("* U3 as an error amplifier around the feedback pin: VOUT = clamp(1e5 x (VFB - V(FB))), VFB 500 mV (p6); loop closed by R3, R4 of the netlist")
    dk.add("Bu3 %s 0 V = max(0, min(5.2, 1e5*({vfb} - v(%s))))" % (n_out, n_fb))
    dk.included.append(("U3", "ideal error amplifier, VFB 0.5 V"))
    dk.add(OPT)
    dk.add(".op")
    dk.add(".control")
    dk.add("run")
    dk.add("echo RESULT boost3v3.vout = $&v(%s)" % n_out)
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")
    return dk


CASE_DECKS = {
    "case1_boost": deck_boost,
    "case2_charger": deck_charger,
    "case3_ts": deck_ts,
    "case4_led": deck_led,
    "case5_rail": deck_rail,
}
