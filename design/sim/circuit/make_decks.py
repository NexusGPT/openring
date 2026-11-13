#!/usr/bin/env python3
"""Writes the ngspice decks of the circuit bench from the circuit files netlist.csv and parts.csv.

    python make_decks.py [--ring-dir DIR] [--case-dir DIR] [--out DIR] [--set REF=VALUE ...]

--ring-dir / --case-dir : folder holding netlist.csv and parts.csv (default design/ecad/ring and design/ecad/case).
--set REF=VALUE         : replace one part value for this run (for example C60=2.2uF).
Part values and connections come from the two files.  Models come from models/.  The stimulus (cell, rails,
switch times, loads) is written here and every number has its source in SRC below or in the model header.
The last two comment lines of each deck list the parts it included and the parts it left out, with the reason.
"""
import argparse
import json
import os

import circuit_lib as cl
from circuit_lib import Deck, node

TMOT = 0.03   # s, time the motor pin goes high in test 1

# Numbers that are not in the circuit files, each with its source.
SRC = {
    "motor_start_a": (0.175, "Jinlong W0525AB001D spec p6 item 3-1-5: starting current below 175 mA at 3.0 V, rotor held"),
    "motor_run_a": (0.080, "Jinlong spec p6 item 3-1-4: rated current below 80 mA at 3.0 V"),
    "motor_v": (3.0, "Jinlong spec p6 item 3-1-1: rated voltage 3.0 V"),
    "motor_start_s": (0.010, "ESTIMATE of ecad/motor-drive/motor-drive.md line 153: start time 10 ms (the maker states none)"),
    "motor_run_s": (0.080, "firmware.md 3.1 pattern M1: 80 ms on"),
    "i_u1_a": (0.003, "architecture.md line 89: main chip 3.0 mA at 1.8 V, estimate"),
    "i_mic_a": (0.00063, "firmware.md 8.5: SPK0641HT4H-1 draws 0.63 mA at 1.8 V"),
    "i_sd_write_a": (0.025, "CS CSNP32GCR01-BOW datasheet p8 IOP write 25 mA max (motor-drive.md 2.4)"),
    "i_vci_a": (0.0032, "architecture.md line 101: screen VCI 3.2 mA"),
    "i_iovcc_a": (0.001, "architecture.md line 101: screen IOVCC 1 mA"),
    "p_screen_w": (0.055, "architecture.md line 101: screen on, full white, about 55 mW"),
    "i_standby_u1_a": (0.000005, "architecture.md line 89: main chip standby 0.005 mA, estimate"),
    "r_contact": (0.5, "Alps SKTAAAE010 spec 6.1 (design/datasheets/slim_alps-skta-aaae010-orwin.txt line 70): contact resistance 500 mohm max"),
}

PORTS_NPM = ["VBUS", "VBUSOUT", "VSYS", "VBAT", "VOUT1", "VOUT2",
             "LSIN1/VINLDO1", "LSOUT1/VOUTLDO1", "LSIN2/VINLDO2", "LSOUT2/VOUTLDO2", "VSET1", "VSET2",
             "@ls1en", "@ls2en", "@chgen"]

RING_POWER_NETS = ["VBAT", "VSYS", "VBUS", "VBUSOUT", "VDD_1V8", "VDD_3V0", "VDD_MIC", "VDD_SD", "VMOT", "MOT_EN",
                   "MOTOR", "VSET1", "VSET2", "NTC", "U1_VBUS"]
RING_SD_NETS = ["SDC_CS", "SDC_MISO", "SDC_MOSI", "SDC_SCK", "SD_DAT1", "SD_DAT2", "SD_CS", "SD_MISO", "SD_MOSI", "SD_SCK"]


def add_cell(dk, ocv_expr, rcell_expr):
    """BT1 as an open-circuit voltage with a series resistance (cell.md gives no resistance, so it is a parameter)."""
    d = dk.d
    pos = node(d.net_of("BT1", "+"))
    neg = node(d.net_of("BT1", "-"))
    dk.add("* BT1 cell: %s ; its capacity (read from parts.csv) is not used by a DC or short test; open-circuit voltage and series resistance are parameters" % d.parts["BT1"]["value"])
    dk.add("Vocv cell_i %s PWL(0 0 100u %s)" % (neg, ocv_expr))
    dk.add("Rcellx cell_i %s %s" % (pos, rcell_expr))
    dk.included.append(("BT1", "cell source + series resistance"))


def add_npm(dk, params=""):
    dk.lib("npm1304.lib")
    dk.ic("U2", "NPM1304" + ((" params: " + params) if params else ""), PORTS_NPM)


def gated(dk, name, nd, amps, t_on, why):
    dk.add("B%s %s 0 I = (time > %g) ? %g : 0 ; %s" % (name, nd, t_on, amps, why))


def ring_loads(dk, t_on, screen=True, sd=True, u1=True, mics=True):
    """Recording loads on the rails, nets from the netlist pins; they switch on at t_on (after the rails are up)."""
    d = dk.d
    n18 = node(d.net_of("U1", "A4"))
    n30 = node(d.net_of("DISP1", "VCI"))
    nmic = node(d.net_of("U5", "VDD"))
    nsd = node(d.net_of("U3", "VCC"))
    nbat = node(d.net_of("BT1", "+"))
    if u1:
        gated(dk, "u1", n18, SRC["i_u1_a"][0], t_on, "U1 " + SRC["i_u1_a"][1])
        dk.included.append(("U1", "load"))
    if mics:
        gated(dk, "mic5", nmic, SRC["i_mic_a"][0], t_on, "U5 " + SRC["i_mic_a"][1])
        gated(dk, "mic6", nmic, SRC["i_mic_a"][0], t_on, "U6, same")
        dk.included += [("U5", "load"), ("U6", "load")]
    if sd:
        gated(dk, "sd", nsd, SRC["i_sd_write_a"][0], t_on, "U3 " + SRC["i_sd_write_a"][1])
        dk.included.append(("U3", "load"))
    if screen:
        pw = SRC["p_screen_w"][0]
        pv = SRC["i_vci_a"][0] * 3.0 + SRC["i_iovcc_a"][0] * 1.8
        gated(dk, "vci", n30, SRC["i_vci_a"][0], t_on, "DISP1 VCI " + SRC["i_vci_a"][1])
        gated(dk, "iov", n18, SRC["i_iovcc_a"][0], t_on, "DISP1 IOVCC " + SRC["i_iovcc_a"][1])
        dk.add("Bscr %s 0 I = (time > %g) ? %g / max(v(%s), 1) : 0 ; U4 panel supply on PVIN (VBAT): %s, minus the VCI and IOVCC power above" % (nbat, t_on, pw - pv, nbat, SRC["p_screen_w"][1]))
        dk.included += [("U4", "constant power load on PVIN"), ("DISP1", "loads VCI, IOVCC")]


def rail_nodes(d):
    return {"vbat": node(d.net_of("BT1", "+")), "vsys": node(d.net_of("U2", "VSYS")),
            # rails are read where the consumers sit (U1 supply pin A4, screen VCI), not at the regulator pins, so that a wrong
            # regulator wiring shows as a wrong rail
            "v18": node(d.net_of("U1", "A4")), "v30": node(d.net_of("DISP1", "VCI")),
            "vmot": node(d.net_of("M1", "+")), "vsd": node(d.net_of("U3", "VCC")),
            "vmic": node(d.net_of("U5", "VDD")), "vbus": node(d.net_of("U2", "VBUS")),
            "vbusout": node(d.net_of("U2", "VBUSOUT"))}


def common_tail(dk, wave_nodes):
    dk.add("wrdata @WAVE@ " + " ".join("v(%s)" % n for n in wave_nodes))
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")


# ---------------------------------------------------------------------------------------------------
# ring test 1: motor start
# ---------------------------------------------------------------------------------------------------
def deck_motor(ring):
    dk = Deck(ring, "ring test 1: motor start 175 mA and run 80 mA with a recording running")
    r = rail_nodes(ring)
    dk.add(".param ocv=3.45")
    dk.add(".param rcell=1.9565")
    dk.add(".param icl=0.56")
    dk.add(".param rdo=0.65")
    dk.lib("tlv755p30.lib")
    dk.passives(RING_POWER_NETS)
    add_cell(dk, "{ocv}", "{rcell}")
    dk.add("Vvbus %s 0 DC 0 ; no case present" % r["vbus"])
    dk.add("Vls1 ls1en 0 PWL(0 0 10m 0 10.001m 1) ; host enables LDSW1 (microphones) at 10 ms")
    dk.add("Vls2 ls2en 0 PWL(0 0 5m 0 5.001m 1) ; host enables LDSW2 (storage) at 5 ms")
    dk.add("Vchg chgen 0 0")
    add_npm(dk)
    dk.ic("U11", "TLV755P30 params: icl={icl} rdo={rdo}", ["IN", "OUT", "EN", "GND"])
    nmotor = node(ring.net_of("U1", "P3.01"))
    run = SRC["motor_run_s"][0]
    dk.add("Vmotor %s 0 PWL(0 0 %g 0 %g 1.8 %g 1.8 %g 0) ; U1 pin P3.01 MOTOR, 1.8 V logic, one %g s pulse (firmware.md 3.1 M1)" % (nmotor, TMOT, TMOT + 1e-6, TMOT + run, TMOT + run + 1e-6, run))
    dk.add("* M1: %g ohm for the first %g s of the pulse (%s), then %g ohm (%s)" % (
        SRC["motor_v"][0] / SRC["motor_start_a"][0], SRC["motor_start_s"][0], SRC["motor_start_a"][1],
        SRC["motor_v"][0] / SRC["motor_run_a"][0], SRC["motor_run_a"][1]))
    dk.add("Bm %s 0 I = v(%s) / ((time < %g) ? %g : %g)" % (r["vmot"], r["vmot"], TMOT + SRC["motor_start_s"][0],
                                                           SRC["motor_v"][0] / SRC["motor_start_a"][0], SRC["motor_v"][0] / SRC["motor_run_a"][0]))
    dk.included.append(("M1", "resistive load"))
    ring_loads(dk, 0.015)
    a, b = TMOT, TMOT + run
    dk.add(".options reltol=1e-4 abstol=1e-12 vntol=1e-7 ; tmax below sets the time resolution; results were checked for convergence (sim-notes.md)")
    dk.add(".tran 1u %g 0 5u uic" % (b + 0.04))
    dk.add(".control")
    dk.add("run")
    m = [("vbat_min", "min", r["vbat"], 0.0305, b), ("v18_min", "min", r["v18"], a, b), ("v18_max", "max", r["v18"], a, b),
         ("v30_min", "min", r["v30"], a, b), ("v30_max", "max", r["v30"], a, b), ("vmot_min", "min", r["vmot"], a + 0.0011, b),
         ("vsys_min", "min", r["vsys"], a, b)]
    for nm, kind, nd, t0, t1 in m:
        dk.add("meas tran %s %s v(%s) from=%g to=%g" % (nm, kind, nd, t0, t1))
    dk.add("meas tran vbat_settled find v(%s) at=%g" % (r["vbat"], a + SRC["motor_start_s"][0] - 0.0001))
    dk.add("meas tran ibat_max max i(v.xu2.vsb) from=%g to=%g" % (a, b))
    dk.add("meas tran ildo_max max i(v.xu11.vs) from=%g to=%g" % (a, b))
    dk.add("meas tran icell_pk min i(vocv) from=%g to=%g" % (a, b))
    dk.add("meas tran ibuck2_max max i(v.xu2.vsn2) from=%g to=%g" % (a, b))
    for nm in ["vbat_min", "v18_min", "v18_max", "v30_min", "v30_max", "vmot_min", "vsys_min", "vbat_settled", "ibat_max", "ildo_max", "icell_pk", "ibuck2_max"]:
        dk.add("echo RESULT motor.%s = $&%s" % (nm, nm))
    common_tail(dk, [r["vbat"], r["vsys"], r["v18"], r["v30"], r["vmot"], r["vsd"]])
    return dk


# ---------------------------------------------------------------------------------------------------
# ring test 2: power-up
# ---------------------------------------------------------------------------------------------------
T_LS2, T_LS1 = 0.020, 0.040


def deck_powerup(ring):
    dk = Deck(ring, "ring test 2: power-up order and levels from a cell")
    r = rail_nodes(ring)
    dk.add(".param ocv=3.3")
    dk.add(".param rcell=1.0")
    dk.lib("tlv755p30.lib")
    dk.passives(RING_POWER_NETS)
    add_cell(dk, "{ocv}", "{rcell}")
    dk.add("Vvbus %s 0 DC 0 ; no case present" % r["vbus"])
    dk.add("Vls2 ls2en 0 PWL(0 0 %g 0 %g 1) ; host turns on LDSW2 (storage) in BOOT, firmware.md 8.2" % (T_LS2, T_LS2 + 1e-6))
    dk.add("Vls1 ls1en 0 PWL(0 0 %g 0 %g 1) ; host turns on LDSW1 (microphones) at the start of a recording" % (T_LS1, T_LS1 + 1e-6))
    dk.add("Vchg chgen 0 0")
    add_npm(dk)
    dk.ic("U11", "TLV755P30", ["IN", "OUT", "EN", "GND"])
    nmotor = node(ring.net_of("U1", "P3.01"))
    dk.add("Vmotor %s 0 0 ; U1 pin MOTOR is low (the chip drives nothing yet)" % nmotor)
    dk.add("Bm %s 0 I = v(%s) / 17.14 ; M1 at its stall resistance 3.0 V / 175 mA" % (r["vmot"], r["vmot"]))
    dk.included.append(("M1", "resistive load"))
    gated(dk, "u1", node(ring.net_of("U1", "A4")), SRC["i_u1_a"][0], 0.010, "U1 " + SRC["i_u1_a"][1])
    dk.add(".options reltol=1e-4 abstol=1e-12 vntol=1e-7 ; tmax below sets the time resolution; results were checked for convergence (sim-notes.md)")
    dk.add(".tran 2u 0.08 0 5u uic")
    dk.add(".control")
    dk.add("run")
    dk.add("meas tran t18 when v(%s)=1.71 rise=1" % r["v18"])
    dk.add("meas tran t30 when v(%s)=2.85 rise=1" % r["v30"])
    dk.add("meas tran tsd when v(%s)=2.7 rise=1" % r["vsd"])
    dk.add("meas tran tmic when v(%s)=1.6 rise=1" % r["vmic"])
    dk.add("meas tran v18_min min v(%s) from=0.01 to=0.08" % r["v18"])
    dk.add("meas tran v18_peak max v(%s) from=0 to=0.08" % r["v18"])
    dk.add("meas tran v30_min min v(%s) from=0.01 to=0.08" % r["v30"])
    dk.add("meas tran v30_peak max v(%s) from=0 to=0.08" % r["v30"])
    dk.add("meas tran vmot_peak max v(%s) from=0 to=0.08" % r["vmot"])
    dk.add("meas tran vsd_pre_peak max v(%s) from=0 to=%g" % (r["vsd"], T_LS2 - 1e-4))
    dk.add("meas tran vsd_min min v(%s) from=%g to=0.08" % (r["vsd"], T_LS2 + 0.005))
    dk.add("meas tran vsd_peak max v(%s) from=0 to=0.08" % r["vsd"])
    dk.add("meas tran vmic_min min v(%s) from=%g to=0.08" % (r["vmic"], T_LS1 + 0.005))
    dk.add("let order_sd = tsd - t30")
    for nm in ["t18", "t30", "tsd", "tmic", "v18_min", "v18_peak", "v30_min", "v30_peak", "vmot_peak", "vsd_pre_peak", "vsd_min", "vsd_peak", "vmic_min", "order_sd"]:
        dk.add("echo RESULT powerup.%s = $&%s" % (nm, nm))
    common_tail(dk, [r["vbat"], r["vsys"], r["v18"], r["v30"], r["vsd"], r["vmic"], r["vmot"]])
    return dk


# ---------------------------------------------------------------------------------------------------
# ring test 3: charge path
# ---------------------------------------------------------------------------------------------------
def deck_charge(ring):
    dk = Deck(ring, "ring test 3: charge path from the case VBUS 5 V through the pads and U9 to the power chip")
    r = rail_nodes(ring)
    dk.add(".param ocv=3.6")
    dk.add(".param rcell=1.0")
    dk.add(".param rpath=0.5")
    dk.add(".param ibuslim=1.5")
    dk.add(".param loads=0")
    dk.lib("tlv755p30.lib")
    dk.lib("tpd4e05u06.lib")
    nets = RING_POWER_NETS + ["USB_DP", "USB_DN"]
    dk.passives(nets)
    add_cell(dk, "{ocv}", "{rcell}")
    pad = node(ring.net_of("J_BAND_B", "VBUS"))
    dk.add("* case side: VBUS 5 V (case TPS2553 output, 5 V), path resistance spring pin + wire + pad + flex = rpath (no file gives it, swept 0 to 2 ohm)")
    dk.add("Vcase vcase 0 PWL(0 0 10m 0 11m 5)")
    dk.add("Rpathx vcase %s {rpath}" % pad)
    dk.add("Vls1 ls1en 0 {loads} ; the load switches are on when the recording loads are on")
    dk.add("Vls2 ls2en 0 {loads}")
    dk.add("Vchg chgen 0 PWL(0 0 5m 0 5.001m 1) ; charger enabled by the host before VBUS arrives")
    add_npm(dk, "ibuslim={ibuslim}")
    dk.ic("U9", "TPD4E05U06", ["D1+", "D1-", "D2+", "D2-", "GND"])
    dk.ic("U11", "TLV755P30", ["IN", "OUT", "EN", "GND"])
    dk.add("Vmotor %s 0 0" % node(ring.net_of("U1", "P3.01")))
    dk.add("* loads: a recording while charging (worst demand on VBUS); loads scale with the parameter 'loads' (0 or 1)")
    nsd = node(ring.net_of("U3", "VCC"))
    n18 = node(ring.net_of("U1", "A4"))
    n30 = node(ring.net_of("DISP1", "VCI"))
    nmic = node(ring.net_of("U5", "VDD"))
    nbat = node(ring.net_of("BT1", "+"))
    pw = SRC["p_screen_w"][0] - (SRC["i_vci_a"][0] * 3.0 + SRC["i_iovcc_a"][0] * 1.8)
    dk.add("Bl18 %s 0 I = loads * (%g + %g)" % (n18, SRC["i_u1_a"][0], SRC["i_iovcc_a"][0]))
    dk.add("Bl30 %s 0 I = loads * %g" % (n30, SRC["i_vci_a"][0]))
    dk.add("Blmic %s 0 I = loads * %g" % (nmic, 2 * SRC["i_mic_a"][0]))
    dk.add("Blsd %s 0 I = loads * %g" % (nsd, SRC["i_sd_write_a"][0]))
    dk.add("Blscr %s 0 I = loads * %g / max(v(%s), 1)" % (nbat, pw, nbat))
    dk.add(".options method=gear itl4=100 reltol=0.005 abstol=1e-10 vntol=1e-5 ; needed when VBUS becomes valid in the middle of the ramp (the default options abort)")
    dk.add(".tran 20u 0.12 0 50u uic")
    dk.add(".control")
    dk.add("run")
    dk.add("meas tran icc avg i(vocv) from=0.08 to=0.12")
    dk.add("meas tran vbat_t avg v(%s) from=0.08 to=0.12" % r["vbat"])
    dk.add("meas tran ibus avg i(v.xu2.vsv) from=0.08 to=0.12")
    dk.add("meas tran ibus_pk max i(v.xu2.vsv) from=0.03 to=0.12")
    dk.add("meas tran vbus_chip avg v(%s) from=0.08 to=0.12" % r["vbus"])
    dk.add("meas tran vsys avg v(%s) from=0.08 to=0.12" % r["vsys"])
    for nm in ["icc", "vbat_t", "ibus", "ibus_pk", "vbus_chip", "vsys"]:
        dk.add("echo RESULT charge.%s = $&%s" % (nm, nm))
    common_tail(dk, [r["vbat"], r["vsys"], r["vbus"], "vcase"])
    return dk


# ---------------------------------------------------------------------------------------------------
# storage block (tests 4 and 5)
# ---------------------------------------------------------------------------------------------------
def add_storage_parts(dk):
    dk.lib("sn74axc4t774.lib")
    dk.lib("csnp32gcr01.lib")
    dk.ic("U10", "SN74AXC4T774", ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "VCCA", "VCCB", "DIR1", "DIR2", "DIR3", "DIR4", "OE"])
    dk.ic("U3", "CSNP32GCR01", ["VCC", "DAT2", "DAT3", "CLK", "CMD", "DAT0", "DAT1", "@drv", "@drven"])


def deck_inrush(ring):
    dk = Deck(ring, "ring test 4: storage supply inrush when the power chip enables LDSW2")
    r = rail_nodes(ring)
    dk.add(".param ocv=3.45")
    dk.add(".param rcell=1.0")
    dk.add(".param ss=0.05")
    dk.add(".param ssdis=0")
    dk.lib("tlv755p30.lib")
    dk.passives(RING_POWER_NETS + RING_SD_NETS)
    add_cell(dk, "{ocv}", "{rcell}")
    dk.add("Vvbus %s 0 DC 0" % r["vbus"])
    dk.add("Vls1 ls1en 0 0")
    dk.add("Vls2 ls2en 0 PWL(0 0 10m 0 10.001m 1) ; host enables LDSW2 at 10 ms")
    dk.add("Vchg chgen 0 0")
    add_npm(dk, "ss2={ss} ssdis2={ssdis}")
    dk.ic("U11", "TLV755P30", ["IN", "OUT", "EN", "GND"])
    dk.add("Vmotor %s 0 0" % node(ring.net_of("U1", "P3.01")))
    add_storage_parts(dk)
    for pin in ("A9", "B10", "D9"):
        dk.add("Va_%s %s 0 0 ; chip pin %s driven low (idle)" % (pin, node(ring.net_of("U1", pin)), pin))
    dk.add("Vdrv drv 0 0")
    dk.add("Vdrven drven 0 0")
    dk.add("Bu1 %s 0 I = %g ; U1 supply load, %s" % (r["v18"], SRC["i_u1_a"][0], SRC["i_u1_a"][1]))
    dk.add(".options reltol=1e-4 abstol=1e-12 vntol=1e-7 ; tmax below sets the time resolution; results were checked for convergence (sim-notes.md)")
    dk.add(".tran 1u 0.15 0 5u uic")
    dk.add(".control")
    dk.add("run")
    dk.add("meas tran ils_peak min i(v.xu2.vsl2) from=0.0099 to=0.15")
    dk.add("meas tran ils_peak_p max i(v.xu2.vsl2) from=0.0099 to=0.15")
    dk.add("meas tran ibuck2_peak max i(v.xu2.vsn2) from=0.0099 to=0.15")
    dk.add("meas tran v30_min min v(%s) from=0.0099 to=0.15" % r["v30"])
    dk.add("meas tran vsd_final avg v(%s) from=0.13 to=0.15" % r["vsd"])
    dk.add("meas tran t90_abs when v(%s)=2.7 rise=1" % r["vsd"])
    dk.add("let t90 = t90_abs - 0.01")
    dk.add("let ils_abs = max(abs(ils_peak), abs(ils_peak_p))")
    for nm in ["ils_abs", "ibuck2_peak", "v30_min", "vsd_final", "t90"]:
        dk.add("echo RESULT inrush.%s = $&%s" % (nm, nm))
    common_tail(dk, [r["v30"], r["vsd"], r["vbat"]])
    return dk


def deck_shifter(ring):
    dk = Deck(ring, "ring test 5: level shifter U10 and the storage lines with the netlist pull-ups")
    d = ring
    n18 = node(d.net_of("U1", "A4"))
    nsd = node(d.net_of("U3", "VCC"))
    dk.add("* rails are ideal sources here: the test is about the logic levels. VDD_1V8 = 1.8 V (VSET1 47 kohm, nPM1304 p43), VDD_SD = LDSW2 output from VDD_3V0 = 3.0 V (VSET2 150 kohm, p43)")
    dk.add("Vr18 %s 0 1.8" % n18)
    dk.add("Vrsd %s 0 PWL(0 3.0 3.5m 3.0 3.5001m 0 3.9m 0) ; at 3.5 ms VDD_SD is switched off for the isolation phase" % nsd)
    dk.passives(["VDD_1V8", "VDD_SD"] + RING_SD_NETS)
    add_storage_parts(dk)
    # phase 1 (to 1 ms): chip outputs high, card drives DAT0 low
    # phase 2 (1 to 2 ms): chip outputs low, card drives DAT0 high
    # phase 3 (2 to 3.5 ms): chip outputs high, card released (DAT0 Hi-Z)
    # phase 4 (3.5 to 3.9 ms): VDD_SD off, chip outputs high
    hi = "PWL(0 1.8 0.999m 1.8 1m 0 1.999m 0 2m 1.8 3.999m 1.8)"
    for pin in ("A9", "B10", "D9"):
        dk.add("Va_%s %s 0 %s ; chip pin %s, 1.8 V logic" % (pin, node(d.net_of("U1", pin)), hi, pin))
    dk.add("Vdrv drv 0 PWL(0 0 0.999m 0 1m 1 1.999m 1 2m 0)")
    dk.add("Vdrven drven 0 PWL(0 1 1.999m 1 2m 0)")
    dk.add(".options reltol=1e-4 abstol=1e-12 vntol=1e-7 ; tmax below sets the time resolution; results were checked for convergence (sim-notes.md)")
    dk.add(".tran 1u 0.0039 0 2u uic")
    dk.add(".control")
    dk.add("run")
    nb = {k: node(d.net_of("U10", p)) for k, p in (("sck", "B1"), ("mosi", "B2"), ("cs", "B3"), ("miso_c", "B4"))}
    na = {"miso_a": node(d.net_of("U10", "A4"))}
    n1 = node(d.net_of("U3", "DAT1"))
    n2 = node(d.net_of("U3", "DAT2"))
    f = lambda nd, t: "find v(%s) at=%g" % (nd, t)
    pts = [("ab_h_sck", nb["sck"], 0.0009), ("ab_h_mosi", nb["mosi"], 0.0009), ("ab_h_cs", nb["cs"], 0.0009),
           ("ab_l_sck", nb["sck"], 0.0019), ("ab_l_mosi", nb["mosi"], 0.0019), ("ab_l_cs", nb["cs"], 0.0019),
           ("ba_l_chip", na["miso_a"], 0.0009), ("ba_l_shift", nb["miso_c"], 0.0009),
           ("ba_h_chip", na["miso_a"], 0.0019), ("ba_h_shift", nb["miso_c"], 0.0019),
           ("idle_chip", na["miso_a"], 0.0029), ("idle_shift", nb["miso_c"], 0.0029),
           ("pu1", n1, 0.0029), ("pu2", n2, 0.0029),
           ("iso_sck", nb["sck"], 0.0038), ("iso_mosi", nb["mosi"], 0.0038), ("iso_cs", nb["cs"], 0.0038), ("iso_miso", nb["miso_c"], 0.0038)]
    for nm, nd, t in pts:
        dk.add("meas tran %s %s" % (nm, f(nd, t)))
    dk.add("let ab_high = min(ab_h_sck, min(ab_h_mosi, ab_h_cs))")
    dk.add("let ab_low = max(ab_l_sck, max(ab_l_mosi, ab_l_cs))")
    dk.add("let pullup = min(pu1, pu2)")
    dk.add("let iso = max(iso_sck, max(iso_mosi, max(iso_cs, iso_miso)))")
    for q, v in (("ab_high_at_card_min", "ab_high"), ("ab_low_at_card_max", "ab_low"), ("ba_high_at_chip_min", "ba_h_chip"),
                 ("ba_low_at_chip_max", "ba_l_chip"), ("idle_high_at_chip_min", "idle_chip"), ("idle_high_at_shifter_min", "idle_shift"),
                 ("pullup_high_at_card_min", "pullup"), ("vcc_isolation_leak_max", "iso"),
                 ("card_low_at_shifter_max", "ba_l_shift"), ("card_high_at_shifter_min", "ba_h_shift")):
        dk.add("echo RESULT shifter.%s = $&%s" % (q, v))
    common_tail(dk, [nb["sck"], nb["miso_c"], na["miso_a"], n1, n2])
    return dk


# ---------------------------------------------------------------------------------------------------
# ring test 6: joystick and record lines
# ---------------------------------------------------------------------------------------------------
def deck_joystick(ring):
    dk = Deck(ring, "ring test 6: joystick and record lines, pressed and released, with the chip's internal pull-up")
    d = ring
    dk.add(".param rpu=13k")
    n18 = node(d.net_of("U1", "A4"))
    dk.add("Vr18 %s 0 1.8 ; VDD_1V8" % n18)
    sws = sorted(ref for ref, row in d.parts.items() if row["symbol"] == "SKTAAAE010")
    dk.add("* switches %s: contact resistance %g ohm closed (%s), open circuit released" % (" ".join(sws), SRC["r_contact"][0], SRC["r_contact"][1]))
    dk.add(".model swc SW(Ron=%g Roff=1e12 Vt=0.5 Vh=0.1)" % SRC["r_contact"][0])
    t0 = 0.001
    meas = []
    for i, sw in enumerate(sws):
        # a switch has several pins; the pins not on GND share the signal net (pin numbers differ between versions of the files)
        sig_nets = sorted({n for n, _, _ in d.pins[sw] if n != "GND"})
        if len(sig_nets) != 1 or not any(n == "GND" for n, _, _ in d.pins[sw]):
            raise SystemExit("switch %s: expected one signal net and GND, found %s" % (sw, sig_nets))
        net = sig_nets[0]
        sig = node(net)
        gnd = "0"
        u1pins = [pn for (rf, pn, nm) in d.nets[net] if rf == "U1"]
        if not u1pins:
            raise SystemExit("switch %s: net %s has no U1 pin" % (sw, net))
        ton, toff = t0 * (2 * i + 1), t0 * (2 * i + 2)
        dk.add("Vp_%s p_%s 0 PWL(0 0 %g 0 %g 1 %g 1 %g 0)" % (sw, sw, ton - 1e-6, ton, toff, toff + 1e-6))
        dk.add("S%s %s %s p_%s 0 swc" % (sw, sig, gnd, sw))
        dk.add("Rpu_%s %s %s {rpu} ; U1 pin %s internal pull-up (value NOT FOUND in any file, swept)" % (sw, n18, sig, u1pins[0]))
        dk.included.append((sw, "switch"))
        meas.append((sw, sig, ton, toff))
    dk.add(".options reltol=1e-4 abstol=1e-12 vntol=1e-7 ; tmax below sets the time resolution; results were checked for convergence (sim-notes.md)")
    dk.add(".tran 1u %g 0 2u uic" % (t0 * (2 * len(sws) + 1)))
    dk.add(".control")
    dk.add("run")
    for sw, sig, ton, toff in meas:
        dk.add("meas tran pr_%s find v(%s) at=%g" % (sw, sig, ton + 0.8 * t0))
        dk.add("meas tran rl_%s find v(%s) at=%g" % (sw, sig, toff + 0.8 * t0))
        dk.add("meas tran ip_%s find i(Vr18) at=%g" % (sw, ton + 0.8 * t0))

    def fold(fn, names):
        s = names[-1]
        for n in reversed(names[:-1]):
            s = "%s(%s, %s)" % (fn, n, s)
        return s
    dk.add("let pressed_max = %s" % fold("max", ["pr_%s" % m[0] for m in meas]))
    dk.add("let released_min = %s" % fold("min", ["rl_%s" % m[0] for m in meas]))
    dk.add("let ipress = %s" % fold("max", ["abs(ip_%s)" % m[0] for m in meas]))
    dk.add("let ipress_min = %s" % fold("min", ["abs(ip_%s)" % m[0] for m in meas]))
    dk.add("echo RESULT joy.pressed_max = $&pressed_max")
    dk.add("echo RESULT joy.released_min = $&released_min")
    dk.add("echo RESULT joy.pressed_current_max = $&ipress")
    dk.add("echo RESULT joy.pressed_current_min = $&ipress_min")
    dk.add("echo RESULT joy.nswitches = %d" % len(sws))
    common_tail(dk, [m[1] for m in meas])
    return dk


# ---------------------------------------------------------------------------------------------------
# ring test 7: pads on the finger
# ---------------------------------------------------------------------------------------------------
def deck_pads(ring):
    dk = Deck(ring, "ring test 7: voltage between the four charging pads after VBUS is removed")
    r = rail_nodes(ring)
    d = ring
    dk.add(".param ocv=3.8")
    dk.add(".param rcell=1.0")
    dk.add(".param rbleed=0")
    dk.lib("tlv755p30.lib")
    dk.lib("tpd4e05u06.lib")
    dk.passives(RING_POWER_NETS + ["USB_DP", "USB_DN"])
    add_cell(dk, "{ocv}", "{rcell}")
    pv = node(d.net_of("J_BAND_B", "VBUS"))
    pdn = node(d.net_of("J_BAND_B", "D-"))
    pdp = node(d.net_of("J_BAND_B", "D+"))
    dk.add(".model swc SW(Ron=0.01 Roff=1e13 Vt=0.5 Vh=0.1)")
    dk.add("Vcase vcase 0 PWL(0 0 1m 5)")
    dk.add("Vsw ctl 0 PWL(0 1 0.05 1 0.050001 0) ; the ring leaves the case at 50 ms")
    dk.add("Scase vcase %s ctl 0 swc ; the spring pin leaves the pad: open circuit" % pv)
    dk.add("Vls1 ls1en 0 0")
    dk.add("Vls2 ls2en 0 0")
    dk.add("Vchg chgen 0 PWL(0 0 5m 0 5.001m 1)")
    add_npm(dk)
    dk.ic("U9", "TPD4E05U06", ["D1+", "D1-", "D2+", "D2-", "GND"])
    dk.ic("U11", "TLV755P30", ["IN", "OUT", "EN", "GND"])
    dk.add("Vmotor %s 0 0" % node(d.net_of("U1", "P3.01")))
    dk.add("Bu1 %s 0 I = %g ; U1 standby, %s" % (r["v18"], SRC["i_standby_u1_a"][0], SRC["i_standby_u1_a"][1]))
    dk.add(".if (rbleed > 0)")
    dk.add("Rbleedx %s 0 {rbleed} ; WHAT-IF only: a bleeder on VBUS, not in the design" % pv)
    dk.add(".endif")
    dk.add(".options method=gear itl4=100 reltol=0.005 abstol=1e-10 vntol=1e-5")
    dk.add(".tran 100u 10.06 0 20m uic")
    dk.add(".control")
    dk.add("run")
    dk.add("meas tran v_vbus find v(%s) at=10.05" % pv)
    dk.add("meas tran v_dn find v(%s) at=10.05" % pdn)
    dk.add("meas tran v_dp find v(%s) at=10.05" % pdp)
    dk.add("meas tran v_vbus_early find v(%s) at=0.049" % pv)
    dk.add("meas tran v_vbus_1s find v(%s) at=1.05" % pv)
    dk.add("let vbus_dp = abs(v_vbus - v_dp)")
    dk.add("let vbus_dn = abs(v_vbus - v_dn)")
    for nm in ["v_vbus", "v_dn", "v_dp", "vbus_dp", "vbus_dn", "v_vbus_early", "v_vbus_1s"]:
        dk.add("echo RESULT pads.%s = $&%s" % (nm, nm))
    common_tail(dk, [pv, pdp, pdn])
    return dk


def deck_mic(ring):
    dk = Deck(ring, "ring test 8: supply ripple at a microphone Vdd pin, pulsed microphone current")
    d = ring
    c_pin = d.value("C35")
    c_bulk = d.value("C31")
    c_out = d.value("C86")
    dk.add(".param lmm=2")
    dk.add("* track from the 1 uF part C31 to the Vdd pin: 0.5 nH per mm (lead's figure), copper 0.10 mm x 0.018 mm: 9.33 mohm per mm (resistivity 1.68e-8 ohm m, standard value)")
    dk.add("V18 rail 0 1.8 ; ideal 1.8 V behind the load switch")
    dk.add("Rsw rail nout 0.2 ; LDSW1 RDSONLS 200 mohm, nPM1304 p69")
    dk.add("Cc86 nout 0 %.6g ; C86 %s" % (c_out, d.parts["C86"]["value"]))
    dk.add("Cc31 nout 0 %.6g ; C31 %s" % (c_bulk, d.parts["C31"]["value"]))
    dk.add("Ltrk nout nmid {0.5n*lmm}")
    dk.add("Rtrk nmid pin {0.00933*lmm}")
    dk.add("Cc35 pin 0 %.6g ; C35 %s at the pin" % (c_pin, d.parts["C35"]["value"]))
    dk.add("Imic pin 0 PULSE(0 1.42m 0 1n 1n 325.5n 651n) ; 2 x 710 uA square at 1.536 MHz (period 651 ns), Knowles sheet")
    dk.included += [("C86", "value read"), ("C31", "value read"), ("C35", "value read"), ("U5", "load")]
    dk.add(".options reltol=1e-4 abstol=1e-12 vntol=1e-7")
    dk.add(".tran 1n 40u 0 5n uic")
    dk.add(".control")
    dk.add("run")
    dk.add("meas tran vmax max v(pin) from=30u to=40u")
    dk.add("meas tran vmin min v(pin) from=30u to=40u")
    dk.add("let pp = vmax - vmin")
    dk.add("echo RESULT mic.pp = $&pp")
    dk.add("quit")
    dk.add(".endc")
    dk.add(".end")
    return dk


RING_DECKS = {
    "ring1_motor": deck_motor,
    "ring2_powerup": deck_powerup,
    "ring3_charge": deck_charge,
    "ring4_inrush": deck_inrush,
    "ring5_shifter": deck_shifter,
    "ring6_joystick": deck_joystick,
    "ring7_pads": deck_pads,
    "ring8_mic": deck_mic,
}


def build_all(ring, case, out):
    os.makedirs(out, exist_ok=True)
    manifest = {}
    funcs = {k: (lambda f: (lambda: f(ring)))(v) for k, v in RING_DECKS.items()}
    try:
        import case_decks
        for k, v in case_decks.CASE_DECKS.items():
            funcs[k] = (lambda f: (lambda: f(case)))(v)
    except ImportError:
        pass
    for name, fn in funcs.items():
        dk = fn()
        path = os.path.join(out, name + ".cir")
        with open(path, "w") as f:
            f.write(dk.text())
        manifest[name] = {"deck": path, "included": dk.included, "excluded": dk.excluded}
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ring-dir", default=cl.RING_DIR)
    ap.add_argument("--case-dir", default=cl.CASE_DIR)
    ap.add_argument("--out", default=os.path.join(cl.HERE, "decks"))
    ap.add_argument("--set", action="append", default=[])
    a = ap.parse_args()
    ov = dict(s.split("=", 1) for s in a.set)
    ring0 = cl.Design(a.ring_dir)
    ring = cl.Design(a.ring_dir, {k: v for k, v in ov.items() if k in ring0.parts})
    case0 = cl.Design(a.case_dir)
    case = cl.Design(a.case_dir, {k: v for k, v in ov.items() if k in case0.parts and k not in ring0.parts})
    m = build_all(ring, case, a.out)
    print("wrote %d decks to %s" % (len(m), a.out))
    for name in m:
        print("  %-16s included %3d parts, excluded %3d" % (name, len(m[name]["included"]), len(m[name]["excluded"])))


if __name__ == "__main__":
    main()
