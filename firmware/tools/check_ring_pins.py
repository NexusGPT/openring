#!/usr/bin/env python3
"""check_ring_pins.py: the ring's built devicetree against the circuit's netlist (software step 7).

Usage (in the toolchain container, after the ring build):
  python3 tools/check_ring_pins.py <zephyr.dts of the ring build> <netlist.csv> [--source-netlist <path>]

Reads the netlist rows of U1 (the nRF54LM20A) and the built devicetree (zephyr.dts, parsed with Zephyr's own dtlib),
and for every U1 signal finds the devicetree place that carries it (the table SIGNALS below: a GPIO property or a
pin-control function of a node; or, for a pin with a fixed function, the node of that function). It prints one line per
signal:
  SAME <signal> netlist <pin> devicetree <where> <pin>
  DIFFERENT <signal> netlist <pin> devicetree <where> <pin>     (fails)
  NO NODE <signal> netlist <pin>: <why>                        (fails: the node, the property or the function is missing,
                                                                 or the node is not enabled)
  NO NODE BY NATURE <net> <ball> <pin name>: <why>             (power, ground, decoupling, debug, reset: no devicetree node)
for a GPIO-kind signal also its flags (active level, pull) against the table FLAGS and the source it names:
  SAME FLAGS / DIFFERENT FLAGS (fails) / FLAGS ... no source (no source states them: printed, not compared)
and, the other way round, every GPIO and pin-control pin of an enabled node that the table does not name:
  UNEXPECTED <where> <pin> (netlist net <net or none>)           (fails; also a gpio hog, and a property ending in
                                                                 "gpios" that cannot be read as GPIOs)
  UNSEEN <node>                                                  (fails: an enabled ADC, comparator or NFC node, whose
                                                                 pins this check cannot see)
Not seen: a pin a driver selects in code without the devicetree. The fixed-function pins (crystals, USB, antenna)
come from the chip, not from the devicetree, which names no pin for them; the check proves only that their node is
enabled.
A U1 row whose net is in no list fails too (UNLISTED). Last line: "check_ring_pins: RESULT PASS ..." (exit 0) or
"check_ring_pins: RESULT FAIL ..." (exit 1). Exit 2: the inputs could not be read.

--production: the production build (fix round 2, S7R-08): DBG_TX must be a gpio hog on its netlist pin, an input with
the chip's pull-down and no other compared flag (design/firmware.md l.1061), and uart20 must not name it.

--source-netlist: when that file exists (the design copy, design/ecad/ring/netlist.csv, present on the Mac but not on
the build server, which receives firmware/ only), the given netlist must be byte-identical to it, else the check fails.
"""
import csv
import hashlib
import os
import re
import sys

ZEPHYR_BASE = os.environ.get("ZEPHYR_BASE", "/ws/zephyr")
sys.path.insert(0, os.path.join(ZEPHYR_BASE, "scripts", "dts", "python-devicetree", "src"))

# signal -> (kind, node label or path, property or pin-control function)
#   gpio: the node's <property> (a phandle-array of a GPIO controller), first entry, unless an index is given
#   psel: the node's pin-control states: the <function> in every state (default, sleep) must name the pin
#   fixed: a pin with one function on this chip: the node must exist and be enabled; the pin comes from the chip
SIGNALS = {
    "BTN_REC": ("gpio", "ring_btn_rec", "gpios"),
    "JOY_UP": ("gpio", "ring_joy_up", "gpios"),
    "JOY_DOWN": ("gpio", "ring_joy_down", "gpios"),
    "JOY_LEFT": ("gpio", "ring_joy_left", "gpios"),
    "JOY_RIGHT": ("gpio", "ring_joy_right", "gpios"),
    "MOTOR": ("gpio", "ring_motor", "gpios"),
    "LCD_CS": ("gpio", "spi21", "cs-gpios"),
    "LCD_DCX": ("gpio", "ring_lcd_dbi", "dc-gpios"),
    "LCD_RST": ("gpio", "ring_lcd_dbi", "reset-gpios"),
    "LCD_TE": ("gpio", "ring_lcd_dbi", "te-gpios"),
    "OLED_PWR_EN": ("gpio", "/zephyr,user", "oled-pwr-en-gpios"),
    "PMIC_INT": ("gpio", "ring_pmic", "host-int-gpios"),
    "SD_CS": ("gpio", "spi00", "cs-gpios"),
    "MIC_B_DATA": ("gpio", "/zephyr,user", "mic-b-data-gpios"),
    "SPARE_P1_00": ("gpio", "/zephyr,user", "spare-p1-00-gpios"),
    "SPARE_P2_00": ("gpio", "/zephyr,user", "spare-p2-00-gpios"),
    "SPARE_P3_03": ("gpio", "/zephyr,user", "spare-p3-03-gpios"),
    "SPARE_P3_04": ("gpio", "/zephyr,user", "spare-p3-04-gpios"),
    "DBG_TX": ("psel", "uart20", "UART_TX"),
    "SD_SCK": ("psel", "spi00", "SPIM_SCK"),
    "SD_MOSI": ("psel", "spi00", "SPIM_MOSI"),
    "SD_MISO": ("psel", "spi00", "SPIM_MISO"),
    "LCD_SCK": ("psel", "spi21", "SPIM_SCK"),
    "LCD_MOSI": ("psel", "spi21", "SPIM_MOSI"),
    "PMIC_SDA": ("psel", "i2c22", "TWIM_SDA"),
    "PMIC_SCL": ("psel", "i2c22", "TWIM_SCL"),
    "MIC_A_CLK": ("psel", "pdm20", "PDM_CLK"),
    "MIC_A_DATA": ("psel", "pdm20", "PDM_DIN"),
    # fixed-function pins: the chip pin each must be on (design/firmware.md peripheral table, lines 86 and 87; the
    # chip's own pin list is not in the SDK files read here) and the node of the function
    "XL1": ("fixed", "lfxo", "P1.20"),
    "XL2": ("fixed", "lfxo", "P1.21"),
    "XC1": ("fixed", "hfxo", "XC1"),
    "XC2": ("fixed", "hfxo", "XC2"),
    "USB_DP": ("fixed", "zephyr_udc0", "D+"),
    "USB_DN": ("fixed", "zephyr_udc0", "D-"),
    "U1_VBUS": ("fixed", "zephyr_udc0", "VBUS"),
    "ANT1_NODE": ("fixed", "radio", "ANT"),
}

# nets of U1 with no devicetree node by their nature
NO_NODE_BY_NATURE = {
    "GND": "ground",
    "VDD_1V8": "supply",
    "VDD_USB_3V3": "the chip's USB regulator output (DECUSB), a capacitor only",
    "DCC": "the DC/DC converter's inductor L1 (vregmain's mode is set in the devicetree, no pin)",
    "DECA": "decoupling",
    "DECD": "decoupling",
    "TXRTUNE": "radio tuning resistor R2",
    "NRESET": "reset, test pad TP5",
    "SWDCLK": "debug, test pad TP3",
    "SWDIO": "debug, test pad TP4",
}


# expected GPIO flags of the GPIO-kind signals: (names of the gpio.h flags that must be set, source); None = no source
# states the flags, printed as "no source" and not compared. Only ACTIVE_LOW, PULL_UP and PULL_DOWN are compared.
FLAGS = {
    "BTN_REC": (("GPIO_PULL_UP", "GPIO_ACTIVE_LOW"), "design/firmware.md l.82"),
    "JOY_UP": (("GPIO_PULL_UP", "GPIO_ACTIVE_LOW"), "design/firmware.md l.82"),
    "JOY_DOWN": (("GPIO_PULL_UP", "GPIO_ACTIVE_LOW"), "design/firmware.md l.82"),
    "JOY_LEFT": (("GPIO_PULL_UP", "GPIO_ACTIVE_LOW"), "design/firmware.md l.82"),
    "JOY_RIGHT": (("GPIO_PULL_UP", "GPIO_ACTIVE_LOW"), "design/firmware.md l.82"),
    "MOTOR": ((), "design/firmware.md l.83 (output, active high)"),
    "PMIC_INT": ((), "design/firmware.md l.865 (active high)"),
    "OLED_PWR_EN": ((), "design/firmware.md l.381 (high = screen supply on)"),
    "LCD_RST": (("GPIO_ACTIVE_LOW",), "design/firmware.md l.381 (low = reset, high = run)"),
    "LCD_TE": ((), "design/firmware.md l.84 (input, rising edge)"),
    "SD_CS": (("GPIO_ACTIVE_LOW",), "design/firmware.md l.506 (SD_CS high when idle)"),
    "LCD_CS": None,
    "LCD_DCX": None,
    "MIC_B_DATA": None,
    "SPARE_P1_00": None,
    "SPARE_P2_00": None,
    "SPARE_P3_03": None,
    "SPARE_P3_04": None,
}
COMPARED_FLAGS = ("GPIO_ACTIVE_LOW", "GPIO_PULL_UP", "GPIO_PULL_DOWN")
# enabled nodes whose pins this check cannot see (analog inputs, NFC pads): any of them fails the check
UNSEEN_COMPATS = ("nordic,nrf-saadc", "nordic,nrf-comp", "nordic,nrf-lpcomp", "nordic,nrf-nfct")


def load_gpio_flags():
    hdr = os.path.join(ZEPHYR_BASE, "include", "zephyr", "dt-bindings", "gpio", "gpio.h")
    vals = {}
    with open(hdr) as f:
        for line in f:
            m = re.match(r"#define\s+(GPIO_ACTIVE_LOW|GPIO_PULL_UP|GPIO_PULL_DOWN)\s+\(1 << (\d+)\)", line)
            if m:
                vals[m.group(1)] = 1 << int(m.group(2))
    for k in COMPARED_FLAGS:
        if k not in vals:
            raise RuntimeError("%s not found in %s" % (k, hdr))
    return vals


def load_netlist(path):
    """U1 rows: list of (net, ball, pin_name, pin_type)."""
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["reference"] == "U1":
                rows.append((r["net"], r["pin_number"], r["pin_name"], r["pin_type"]))
    return rows


def load_psel_macros():
    """NRF_FUN_* values and the NRF_PSEL bit layout, read from the kit's own header."""
    hdr = os.path.join(ZEPHYR_BASE, "include", "zephyr", "dt-bindings", "pinctrl", "nrf-pinctrl.h")
    vals = {}
    with open(hdr) as f:
        for line in f:
            m = re.match(r"#define\s+(NRF_FUN_\w+|NRF_PIN_\w+)\s+(0x[0-9A-Fa-f]+|\d+)U?\b", line)
            if m:
                vals[m.group(1)] = int(m.group(2), 0)
    for k in ("NRF_FUN_POS", "NRF_FUN_MSK", "NRF_PIN_POS", "NRF_PIN_MSK"):
        if k not in vals:
            raise RuntimeError("%s not found in %s" % (k, hdr))
    return hdr, vals


def pin_text(port, pin):
    return "P%d.%02d" % (port, pin)


def norm_netlist_pin(name):
    m = re.match(r"P(\d+)\.(\d+)$", name)
    return pin_text(int(m.group(1)), int(m.group(2))) if m else name


def enabled(node):
    """True when the node and every parent is enabled (no status, "okay" or "ok")."""
    while node is not None:
        st = node.props.get("status")
        if st is not None and st.to_string() not in ("okay", "ok"):
            return False
        node = node.parent
    return True


def gpio_port(node):
    p = node.props.get("port")
    if p is not None:
        return p.to_num()
    m = re.match(r"gpio(\d+)$", node.labels[0] if node.labels else "")
    return int(m.group(1)) if m else None


def gpio_entries(dt, prop):
    """[(controller node, pin, flags)] of a GPIO phandle-array property."""
    cells = [int.from_bytes(prop.value[i:i + 4], "big") for i in range(0, len(prop.value), 4)]
    out = []
    i = 0
    while i < len(cells):
        ctl = dt.phandle2node.get(cells[i])
        if ctl is None:
            raise RuntimeError("%s: phandle %d unknown" % (prop.name, cells[i]))
        n = ctl.props["#gpio-cells"].to_num()
        args = cells[i + 1:i + 1 + n]
        out.append((ctl, args[0], args[1] if len(args) > 1 else 0))
        i += 1 + n
    return out


def find_node(dt, where):
    if where.startswith("/"):
        try:
            return dt.get_node(where)
        except Exception:
            return None
    return dt.label2node.get(where)


def node_name(node):
    return node.labels[0] if node.labels else node.path


def psel_states(dt, node):
    """{state name: [(function value, port, pin)]} of a node's pinctrl-N properties."""
    names = node.props["pinctrl-names"].to_strings() if "pinctrl-names" in node.props else []
    out = {}
    for idx, sname in enumerate(names):
        prop = node.props.get("pinctrl-%d" % idx)
        if prop is None:
            continue
        entries = []
        for st in prop.to_nodes():
            for grp in st.nodes.values():
                if "psels" in grp.props:
                    for v in grp.props["psels"].to_nums():
                        entries.append(v)
        out[sname] = entries
    return out


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    production = "--production" in argv
    signals = dict(SIGNALS)
    if production:
        signals["DBG_TX"] = ("hog", "gpio-hog", "input, GPIO_PULL_DOWN")
    src = None
    if "--source-netlist" in argv:
        src = argv[argv.index("--source-netlist") + 1]
        args = [a for a in args if a != src]
    if len(args) != 2:
        print(__doc__)
        return 2
    dts_path, net_path = args
    failures = []
    try:
        from devicetree import dtlib
        dt = dtlib.DT(dts_path)
        rows = load_netlist(net_path)
        hdr, mac = load_psel_macros()
        gflags = load_gpio_flags()
    except Exception as e:  # inputs unreadable: not a pass and not a pin failure
        print("check_ring_pins: cannot read the inputs: %s" % e)
        return 2
    with open(net_path, "rb") as f:
        net_sha = hashlib.sha256(f.read()).hexdigest()
    print("check_ring_pins: devicetree %s" % dts_path)
    print("check_ring_pins: netlist %s sha256 %s, %d rows of U1" % (net_path, net_sha, len(rows)))
    print("check_ring_pins: pin-control layout from %s" % hdr)
    if src is not None:
        if os.path.exists(src):
            with open(src, "rb") as f:
                s = hashlib.sha256(f.read()).hexdigest()
            if s != net_sha:
                print("DIFFERENT NETLIST %s sha256 %s is not the source %s sha256 %s" % (net_path, net_sha, src, s))
                failures.append("netlist-copy")
            else:
                print("check_ring_pins: netlist copy equals the source %s" % src)
        else:
            print("check_ring_pins: source netlist %s not present here (the build server receives firmware/ only): "
                  "the copy's sha256 above is the one checked" % src)

    fun_pos, fun_msk, pin_pos, pin_msk = mac["NRF_FUN_POS"], mac["NRF_FUN_MSK"], mac["NRF_PIN_POS"], mac["NRF_PIN_MSK"]
    fun_by_val = {v: k[len("NRF_FUN_"):] for k, v in mac.items()
                  if k.startswith("NRF_FUN_") and k not in ("NRF_FUN_POS", "NRF_FUN_MSK")}

    def decode(v):
        f = (v >> fun_pos) & fun_msk
        p = (v >> pin_pos) & pin_msk
        return fun_by_val.get(f, "FUN%d" % f), p // 32, p % 32

    by_net = {}
    for net, ball, pname, ptype in rows:
        by_net.setdefault(net, []).append((ball, pname, ptype))
    pin_to_net = {}
    for net, ball, pname, ptype in rows:
        pin_to_net[norm_netlist_pin(pname)] = net if net else None

    expected_places = set()   # (node path, property or function, pin) the table accounts for
    checked = 0
    for net in sorted(by_net):
        for ball, pname, ptype in by_net[net]:
            if net == "":
                continue
            npin = norm_netlist_pin(pname)
            if net in NO_NODE_BY_NATURE:
                print("NO NODE BY NATURE %s %s %s: %s" % (net, ball, pname, NO_NODE_BY_NATURE[net]))
                continue
            if net not in signals:
                print("UNLISTED %s %s %s: a U1 net this check has no rule for" % (net, ball, pname))
                failures.append(net)
                continue
            kind, where, what = signals[net]
            if kind == "hog":
                checked += 1
                hogs = []
                for hn in dt.node_iter():
                    if "gpio-hog" in hn.props and enabled(hn):
                        hport = gpio_port(hn.parent)
                        hcells = hn.props["gpios"].to_nums() if "gpios" in hn.props else []
                        hn_cells = hn.parent.props["#gpio-cells"].to_num()
                        for k in range(0, len(hcells), hn_cells):
                            if pin_text(hport, hcells[k]) == npin:
                                hogs.append((hn, hcells[k + 1] if hn_cells > 1 else 0))
                if len(hogs) != 1:
                    print("NO NODE %s netlist %s: %d gpio hogs on this pin (1 wanted)" % (net, npin, len(hogs)))
                    failures.append(net)
                    continue
                hn, hflags = hogs[0]
                expected_places.add((hn.path, "gpio-hog", npin))
                mask = gflags["GPIO_ACTIVE_LOW"] | gflags["GPIO_PULL_UP"] | gflags["GPIO_PULL_DOWN"]
                if "input" not in hn.props or hflags & mask != gflags["GPIO_PULL_DOWN"]:
                    print("DIFFERENT FLAGS %s hog %s %s flags 0x%x, design/firmware.md l.1061 wants an input with "
                          "GPIO_PULL_DOWN" % (net, hn.path, "input" if "input" in hn.props else "not input",
                                               hflags & mask))
                    failures.append(net)
                else:
                    print("SAME %s netlist %s devicetree hog %s input, GPIO_PULL_DOWN (design/firmware.md l.1061)" %
                          (net, npin, hn.path))
                continue
            node = find_node(dt, where)
            checked += 1
            if node is None:
                print("NO NODE %s netlist %s: no node %s in the devicetree" % (net, npin, where))
                failures.append(net)
                continue
            if not enabled(node):
                print("NO NODE %s netlist %s: node %s is not enabled" % (net, npin, where))
                failures.append(net)
                continue
            if kind == "fixed":
                if npin != what:
                    print("DIFFERENT %s netlist %s devicetree %s (fixed function) %s" % (net, npin, node_name(node), what))
                    failures.append(net)
                else:
                    print("SAME %s netlist %s devicetree %s enabled; pin %s from the chip's fixed function (the "
                          "devicetree names no pin for this node)" % (net, npin, node_name(node), what))
                continue
            if kind == "gpio":
                prop = node.props.get(what)
                if prop is None:
                    print("NO NODE %s netlist %s: node %s has no property %s" % (net, npin, where, what))
                    failures.append(net)
                    continue
                ents = gpio_entries(dt, prop)
                ctl, pin, flags = ents[0]
                port = gpio_port(ctl)
                dpin = pin_text(port, pin)
                expected_places.add((node.path, what, dpin))
                place = "%s/%s" % (node_name(node), what)
                if dpin != npin:
                    print("DIFFERENT %s netlist %s devicetree %s %s" % (net, npin, place, dpin))
                    failures.append(net)
                else:
                    print("SAME %s netlist %s devicetree %s %s (flags 0x%x)" % (net, npin, place, dpin, flags))
                exp = FLAGS.get(net)
                mask = 0
                for k in COMPARED_FLAGS:
                    mask |= gflags[k]
                if exp is None:
                    print("FLAGS %s 0x%x: no source" % (net, flags & mask))
                else:
                    want = 0
                    for k in exp[0]:
                        want |= gflags[k]
                    names = lambda v: "|".join(k for k in COMPARED_FLAGS if v & gflags[k]) or "ACTIVE_HIGH, no pull"
                    if flags & mask != want:
                        print("DIFFERENT FLAGS %s devicetree %s, %s wants %s" % (net, names(flags & mask), exp[1],
                                                                              names(want)))
                        if net not in failures:
                            failures.append(net)
                    else:
                        print("SAME FLAGS %s %s (%s)" % (net, names(want), exp[1]))
                continue
            # psel
            states = psel_states(dt, node)
            if not states:
                print("NO NODE %s netlist %s: node %s has no pin-control state" % (net, npin, where))
                failures.append(net)
                continue
            ok = True
            seen = False
            for sname, ents in states.items():
                pins = [pin_text(po, pi) for (fn, po, pi) in map(decode, ents) if fn == what]
                if not pins:
                    print("NO NODE %s netlist %s: state %s of %s has no %s" % (net, npin, sname, where, what))
                    ok = False
                    continue
                seen = True
                for dpin in pins:
                    expected_places.add((node.path, what, dpin))
                    place = "%s/%s/%s" % (node_name(node), sname, what)
                    if dpin != npin:
                        print("DIFFERENT %s netlist %s devicetree %s %s" % (net, npin, place, dpin))
                        ok = False
                    else:
                        print("SAME %s netlist %s devicetree %s %s" % (net, npin, place, dpin))
            if not ok or not seen:
                if not seen:
                    print("NO NODE %s netlist %s: no pin-control state of %s names %s" % (net, npin, where, what))
                failures.append(net)

    # the other way round: every pin an enabled node names must be one the table accounts for
    unexpected = 0
    for node in dt.node_iter():
        if not enabled(node):
            continue
        compats = node.props["compatible"].to_strings() if "compatible" in node.props else []
        for c in compats:
            if c in UNSEEN_COMPATS:
                print("UNSEEN %s (%s) is enabled: its pins (analog inputs or NFC pads) are not checked" %
                      (node_name(node), c))
                unexpected += 1
        if "gpio-hog" in node.props:
            port = gpio_port(node.parent)
            cells = node.props["gpios"].to_nums() if "gpios" in node.props else []
            n = node.parent.props["#gpio-cells"].to_num()
            for k in range(0, len(cells), n):
                dpin = pin_text(port, cells[k])
                if (node.path, "gpio-hog", dpin) in expected_places:
                    continue
                print("UNEXPECTED %s gpio-hog %s (netlist net %s)" % (node.path, dpin, pin_to_net.get(dpin) or "none"))
                unexpected += 1
            continue
        for pname, prop in node.props.items():
            if pname.endswith("gpios") and not pname.startswith("#") and pname != "ngpios":
                try:
                    ents = gpio_entries(dt, prop)
                except Exception as exc:
                    print("UNEXPECTED %s/%s cannot be read as GPIOs: %s" % (node_name(node), pname, exc))
                    unexpected += 1
                    continue
                for ctl, pin, flags in ents:
                    port = gpio_port(ctl)
                    if port is None:
                        continue   # a GPIO of another controller (none on the chip's ports)
                    dpin = pin_text(port, pin)
                    if (node.path, pname, dpin) not in expected_places:
                        print("UNEXPECTED %s/%s %s (netlist net %s)" % (node_name(node), pname, dpin,
                                                                       pin_to_net.get(dpin) or "none"))
                        unexpected += 1
        for sname, ents in psel_states(dt, node).items():
            for fn, po, pi in map(decode, ents):
                dpin = pin_text(po, pi)
                if (node.path, fn, dpin) not in expected_places:
                    print("UNEXPECTED %s/%s/%s %s (netlist net %s)" % (node_name(node), sname, fn, dpin,
                                                                      pin_to_net.get(dpin) or "none"))
                    unexpected += 1
    if unexpected:
        failures.append("unexpected-pins(%d)" % unexpected)

    if failures:
        print("check_ring_pins: RESULT FAIL %d signals checked; failing: %s" % (checked, " ".join(failures)))
        return 1
    print("check_ring_pins: RESULT PASS %d signals checked, every pin as in the netlist, no unexpected pin" % checked)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # a crash is reported as itself (exit 2), never as a pass or a pin failure
        print("check_ring_pins: CRASH %s: %s" % (type(exc).__name__, exc))
        sys.exit(2)
