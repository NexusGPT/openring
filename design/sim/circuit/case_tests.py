"""Test functions of the case tests (run by run_tests.py with the same pass-line engine as the ring tests)."""
from circuit_lib import parse_value


def merge_max(vals):
    vals = [v for v in vals if isinstance(v, float)]
    return max(vals) if vals else None


def merge_min(vals):
    vals = [v for v in vals if isinstance(v, float)]
    return min(vals) if vals else None


def t_case1(c):
    r = c.run("case1_boost", {"ocv": 4.2, "acc": 0.03, "corner": 1, "load": 0}, tag="noload_hi", test="C1")
    c.values["vring.noload_max"] = r.get("vring.vring")
    c.values["vring.sense_max"] = r.get("vring.vsense")
    r = c.run("case1_boost", {"ocv": 3.0, "acc": -0.03, "corner": 1, "load": 0}, tag="noload_lo", test="C1")
    c.values["vring.noload_min"] = r.get("vring.vring")
    r = c.run("case1_boost", {"ocv": 3.7, "acc": 0.0, "corner": 0, "load": 0, "rshort": 0.001}, tag="short_min", test="C1")
    c.values["vring.ilimit_short_min"] = r.get("vring.iout")
    r2 = c.run("case1_boost", {"ocv": 3.7, "acc": 0.0, "corner": 2, "load": 0, "rshort": 0.001}, tag="short_max", test="C1")
    c.values["vring.ilimit_short_max"] = r2.get("vring.iout")
    r3 = c.run("case1_boost", {"ocv": 3.7, "acc": 0.0, "corner": 1, "load": 0, "rshort": 0.001}, tag="short_nom", test="C1")
    c.note("case1 info: current into a short on VRING: minimum corner %.1f mA, nominal %.1f mA, maximum corner %.1f mA (R5 at its nominal value from parts.csv)" % (
        1000 * r.get("vring.iout", float("nan")), 1000 * r3.get("vring.iout", float("nan")), 1000 * r2.get("vring.iout", float("nan"))))
    r = c.run("case1_boost", {"ocv": 3.0, "acc": -0.03, "corner": 0, "load": 0.39}, tag="load390", test="C1")
    c.values["vring.v_at_load_min"] = r.get("vring.vring")


def _case_text(c, name):
    """Text of a case file (sch-notes.md): from the folder of the case files being tested, else from design/ecad/case."""
    import os
    import circuit_lib as cl
    for fol in (c.case.folder, cl.CASE_DIR):
        pth = os.path.join(fol, name)
        if os.path.exists(pth):
            return open(pth).read()
    raise FileNotFoundError(name)


def _register_facts(c):
    """DATASHEET FACT values. The codes the case software writes are read from sch-notes.md section 9; the step sizes and the defaults are
    BQ25895 numbers: ICHG = code x 64 mA, offset 0, default code 0100000 (REG04, p36); VREG = 3.840 V + code x 16 mV, default code 010111 (REG06, p38)."""
    import re
    txt = _case_text(c, "sch-notes.md")
    sec = txt[txt.index("## 9."):]
    m1 = re.search(r"write (\d{7}) = (\d+) mA", sec)
    m2 = re.search(r"never write a code above (\d{7}) = (\d+) mA", sec, re.I)
    m3 = re.search(r"4\.192 V = (\d{6})", sec)
    if not (m1 and m2 and m3):
        return None
    ichg = lambda code: int(code, 2) * 0.064
    vreg = lambda code: 3.840 + int(code, 2) * 0.016
    f = {
        "ichg_written": ichg(m1.group(1)), "ichg_code_max_written": ichg(m2.group(1)), "vreg_written": vreg(m3.group(1)),
        "ichg_default": ichg("0100000"), "vreg_default": vreg("010111"),
    }
    f["text_check"] = (abs(f["ichg_written"] * 1000 - int(m1.group(2))) < 1e-6 and abs(f["ichg_code_max_written"] * 1000 - int(m2.group(2))) < 1e-6)
    return f


def t_case2(c):
    f = _register_facts(c)
    # SIMULATED: CE level at power-on, module pin not driven, worst case
    r = c.run("case2_charger", {}, tag="poweron", test="C2")
    c.values["charge.ce_poweron_min"] = r.get("charge.ce_v")
    c.values["charge.icc_poweron_max"] = r.get("charge.icc")
    c.note("case2 info: power-on, CE pin not driven, 3V3 at 3.0 V: V(CE) = %.4f V (the charger's VIH is 1.3 V, p10); charge current with the defaults %.6f A" % (r.get("charge.ce_v", float("nan")), r.get("charge.icc", float("nan"))))
    # SIMULATED: CE level when the software drives IO18 low (VOL at most 0.1 x VDD at VDD 3.6 V)
    r = c.run("case2_charger", {"rdrv": 1.0, "vpin": 0.1 * 3.6, "v33": 3.6}, tag="driven_low", test="C2")
    c.values["charge.ce_low_max"] = r.get("charge.ce_v")
    c.note("case2 info: IO18 driven low (VOL 0.36 V, 3V3 at 3.6 V): V(CE) = %.4f V (the charger's VIL is 0.4 V, p10)" % r.get("charge.ce_v", float("nan")))
    # SIMULATED (model choice efficiency): what would be pushed into the cell with the defaults if CE were low
    r = c.run("case2_charger", {"rdrv": 1.0, "vpin": 0.0, "v33": 3.3}, tag="defaults_ce_low", test="C2")
    c.values["charge.icc_default_ce_low"] = r.get("charge.icc")
    c.values["charge.ilim_pin_min"] = r.get("charge.ilim_pin_min")
    c.note("case2 info: if CE were low with the power-on defaults the charger would push %.0f mA into the 700 mAh cell (%.2f C; the cell sheet allows 0.5 C) and aim at %.3f V (the cell's charge voltage is 4.2 V); this is what the pull-up R21 prevents" % (
        1000 * r.get("charge.icc", float("nan")), r.get("charge.icc", float("nan")) / 0.7, r.get("charge.vreg_default", float("nan"))))
    r = c.run("case2_charger", {"rdrv": 1.0, "vpin": 0.0, "v33": 3.3, "psys": 0.9}, tag="sys_load", test="C2")
    c.note("case2 info: with 0.9 W taken by the rest of the case (CE low, defaults) the charge current would be %.0f mA" % (1000 * r.get("charge.icc", float("nan"))))
    # DATASHEET FACT rows
    if f is None:
        c.errors.setdefault("C2", []).append("sch-notes.md section 9: register codes not found")
        return
    c.values["charge.ichg_written"] = f["ichg_written"]
    c.values["charge.ichg_code_max_written"] = f["ichg_code_max_written"]
    c.values["charge.vreg_written"] = f["vreg_written"]
    c.values["charge.vreg_default"] = f["vreg_default"]
    c.values["charge.ichg_reg_default"] = f["ichg_default"]
    c.note("case2 info (datasheet facts, not circuit results): software writes ICHG %.3f A (highest allowed %.3f A) and VREG %.3f V; power-on defaults %.3f A and %.3f V (decoded from codes 0100000 and 010111, p36 and p38; deck parameters %.3f A and %.3f V); codes and mA in sch-notes.md agree: %s" % (
        f["ichg_written"], f["ichg_code_max_written"], f["vreg_written"], f["ichg_default"], f["vreg_default"], r.get("charge.ichg_reg_default", float("nan")), r.get("charge.vreg_default", float("nan")), f["text_check"]))
    if not f["text_check"]:
        c.errors.setdefault("C2", []).append("sch-notes.md: the code and the mA it names disagree")
        c.values.pop("charge.ichg_written", None)


def t_case3(c):
    r = c.run("case3_ts", {}, tag="sweep", test="C3")
    c.values["ts.cold_edge_rth_low"] = r.get("ts.cold_edge_rth")
    c.values["ts.cold_edge_rth_high"] = r.get("ts.cold_edge_rth")
    c.values["ts.hot_edge_rth_low"] = r.get("ts.hot_edge_rth")
    c.values["ts.hot_edge_rth_high"] = r.get("ts.hot_edge_rth")
    c.values["ts.vts_25c_min"] = r.get("ts.vts_25c")
    c.values["ts.vts_25c_max"] = r.get("ts.vts_25c")
    c.note("case3 info: cold edge (charge stops) at TH1 = %.0f ohm, hot cut-off at TH1 = %.0f ohm, hot start limit V(HTF) at TH1 = %.0f ohm; TI's example values are 27280 and 4910 ohm" % (
        r.get("ts.cold_edge_rth", float("nan")), r.get("ts.hot_edge_rth", float("nan")), r.get("ts.htf_edge_rth", float("nan"))))


def t_case4(c):
    rail = 0.5 * (1 + parse_value(c.case.parts["R3"]["value"]) / parse_value(c.case.parts["R4"]["value"]))
    cols = (("red", "R"), ("green", "G"), ("blue", "B"))
    # weakest corner: SYS 3.5 V, curves shifted up by 0.15 V
    r = c.run("case4_led", {"vsys": 3.5, "vshift": 0.15}, tag="lit_min", test="C4")
    for k, _ in cols:
        c.values["led.%s_current_min" % k] = r.get("led." + k)
    c.note("case4 info: SYS 3.5 V, curves +0.15 V (weakest corner): red %.2f mA, green %.2f mA, blue %.2f mA" % tuple(1000 * r.get("led." + k, float("nan")) for k, _ in cols))
    # strongest corner: SYS 4.35 V, curves shifted down by 0.15 V
    r = c.run("case4_led", {"vsys": 4.35, "vshift": -0.15}, tag="lit_max", test="C4")
    c.values["led.max_current"] = merge_max([r.get("led." + k) for k, _ in cols])
    c.note("case4 info: SYS 4.35 V, curves -0.15 V (strongest corner): red %.2f mA, green %.2f mA, blue %.2f mA" % tuple(1000 * r.get("led." + k, float("nan")) for k, _ in cols))
    # off: pins high
    r = c.run("case4_led", {"vsys": 4.35, "vshift": -0.15, "vdrv": rail}, tag="off", test="C4")
    c.values["led.off_current_max"] = merge_max([r.get("led." + k) for k, _ in cols])
    c.note("case4 info: pins driven high (%.4f V), SYS 4.35 V, curves -0.15 V: currents %s A" % (rail, ", ".join("%.3g" % r.get("led." + k, float("nan")) for k, _ in cols)))
    # information only, no row
    for vs in (3.5, 4.35):
        r = c.run("case4_led", {"vsys": vs, "vshift": 0.0}, tag="nom_%g" % vs, test="C4")
        c.note("case4 info: SYS %.2f V, typical curves: red %.2f mA, green %.2f mA, blue %.2f mA (the case sch-notes table gives 3.0 to 4.6, 2.2 to 4.7, 2.2 to 4.7 mA)" % ((vs,) + tuple(1000 * r.get("led." + k, float("nan")) for k, _ in cols)))
    r = c.run("case4_led", {"vsys": 3.0, "vshift": 0.15}, tag="batt_only", test="C4")
    c.note("case4 info, not a row: SYS 3.0 V (cell only at its low end, if SYS follows the cell; the lead's range starts at 3.5 V), curves +0.15 V: red %.2f mA, green %.2f mA, blue %.2f mA" % tuple(1000 * r.get("led." + k, float("nan")) for k, _ in cols))
    for (k, _), dv, lab in zip(cols, (0.5, 0.8, 0.7), ("2.5 V", "4.1 V", "4.0 V")):
        r = c.run("case4_led", {"vsys": 4.35, "vshift": dv}, tag="vfmax_%s" % k, test="C4")
        c.note("case4 info, not a row: %s die at the sheet's maximum VF at 20 mA (%s, p2) and SYS 4.35 V: %.2f mA" % (k, lab, 1000 * r.get("led." + k, float("nan"))))


def t_case5(c):
    lo = c.run("case5_rail", {"vfb": 0.495}, tag="vfb_lo", test="C5")
    hi = c.run("case5_rail", {"vfb": 0.505}, tag="vfb_hi", test="C5")
    c.values["boost3v3.vout_min"] = lo.get("boost3v3.vout")
    c.values["boost3v3.vout_max"] = hi.get("boost3v3.vout")
    nom = c.run("case5_rail", {"vfb": 0.5}, tag="vfb_nom", test="C5")
    c.note("case5 info: 3V3 rail with R3 and R4 from parts.csv: %.4f V nominal (the cell sheet and the ESP32 want 3.0 to 3.6 V)" % nom.get("boost3v3.vout", float("nan")))


CASE_TESTS = [("C1", t_case1), ("C2", t_case2), ("C3", t_case3), ("C4", t_case4), ("C5", t_case5)]
