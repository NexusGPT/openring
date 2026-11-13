"""Reads a KiCad-project netlist.csv and parts.csv (as written by ecad/*/make_netlist.py)
and helps write ngspice decks from them.  Part values and connections are never typed again:
a passive is written from its parts.csv value, an IC is wired from the netlist rows of its pins.
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
RING_DIR = os.path.join(DESIGN, "ecad", "ring")
CASE_DIR = os.path.join(DESIGN, "ecad", "case")
MODELS = os.path.join(HERE, "models")

_UNITS = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "M": 1e6, "G": 1e9, "R": 1.0}


def parse_value(text):
    """'10uF' -> 1e-5, '2.2R' -> 2.2, '47k' -> 47000, '100nF Class 1' -> 1e-7, '1.0uF 25V' -> 1e-6.
    Returns None when the text holds no value (for example 'DNP', 'pad', '10k NTC' returns 10000)."""
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*([pnumkMGR]?)\s*([FHR]?)", text or "")
    if not m:
        return None
    num = float(m.group(1))
    mult = _UNITS.get(m.group(2), 1.0)
    return num * mult


class Design:
    """One circuit: netlist.csv + parts.csv in a folder."""

    def __init__(self, folder, overrides=None):
        self.folder = folder
        self.parts = {}
        with open(os.path.join(folder, "parts.csv"), newline="") as f:
            for row in csv.DictReader(f):
                self.parts[row["reference"]] = row
        # value overrides from the command line: {'C60': '2.2uF'}
        self.overrides = dict(overrides or {})
        for ref, val in self.overrides.items():
            if ref not in self.parts:
                raise SystemExit("override for unknown part %s" % ref)
            self.parts[ref] = dict(self.parts[ref], value=val)
        self.nets = {}          # net -> list of (ref, pin_number, pin_name)
        self.pins = {}          # ref -> list of (net, pin_number, pin_name)
        with open(os.path.join(folder, "netlist.csv"), newline="") as f:
            for row in csv.DictReader(f):
                net = row["net"]
                if not net:
                    continue
                self.nets.setdefault(net, []).append((row["reference"], row["pin_number"], row["pin_name"]))
                self.pins.setdefault(row["reference"], []).append((net, row["pin_number"], row["pin_name"]))

    # --- lookups -------------------------------------------------------------
    def value(self, ref):
        return parse_value(self.parts[ref]["value"])

    def net_of(self, ref, pin):
        """Net of a pin given by pin number or pin name; all pins with that name must share one net."""
        found = set()
        for net, num, name in self.pins.get(ref, []):
            if pin == num or pin == name:
                found.add(net)
        if not found:
            raise KeyError("%s pin %s is not in the netlist" % (ref, pin))
        if len(found) > 1:
            raise KeyError("%s pin %s is on several nets %s" % (ref, pin, sorted(found)))
        return found.pop()

    def has_pin(self, ref, pin):
        return any(pin == num or pin == name for _, num, name in self.pins.get(ref, []))

    def passive_nets(self, ref):
        nets = sorted({net for net, _, _ in self.pins.get(ref, [])})
        return nets


def node(net):
    if net in ("GND", "0"):
        return "0"
    # '+' and '-' keep distinct names (USB_D+ and USB_D- are two nets)
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", net.replace("+", "p").replace("-", "n"))


class Deck:
    def __init__(self, design, title):
        self.d = design
        self.title = title
        self.lines = []
        self.included = []     # (ref, why)
        self.excluded = []     # (ref, why)
        self.libs = []

    def add(self, text):
        self.lines.append(text)

    def lib(self, name):
        self.libs.append(name)

    def passives(self, nets, skip=()):
        """Write every R, C, L, FB, NTC of parts.csv whose nets all lie in `nets` (or GND).
        Parts with no parseable value, DNP parts and `skip` are listed as excluded with the reason."""
        nets = set(nets) | {"GND"}
        for ref, row in self.d.parts.items():
            kind = row["symbol"]
            if kind not in ("R", "C", "L", "FB", "NTC"):
                continue
            pn = self.d.passive_nets(ref)
            if not pn:
                continue
            if ref in skip:
                self.excluded.append((ref, "skipped by the test"))
                continue
            if row.get("dnp", "no") == "yes":
                self.excluded.append((ref, "DNP"))
                continue
            if not all(n in nets for n in pn):
                self.excluded.append((ref, "net outside this test: " + ",".join(n for n in pn if n not in nets)))
                continue
            if len(pn) != 2 and not (len(pn) == 1):
                self.excluded.append((ref, "not a two-pin part on two nets"))
                continue
            val = parse_value(row["value"])
            if val is None:
                self.excluded.append((ref, "no value in parts.csv: " + row["value"]))
                continue
            # two pins: pin 1 and pin 2 nets
            n1 = self.d.net_of(ref, "1")
            n2 = self.d.net_of(ref, "2")
            if kind == "FB":
                self.add("R%s %s %s 0.1  ; ferrite bead, DC resistance not in files, 0.1 ohm placeholder" % (ref, node(n1), node(n2)))
            elif kind == "L":
                self.add("L%s %s %s %.6g ; %s" % (ref, node(n1), node(n2), val, row["value"]))
            elif kind == "C":
                self.add("C%s %s %s %.6g ; %s" % (ref, node(n1), node(n2), val, row["value"]))
            else:   # R, NTC
                self.add("R%s %s %s %.6g ; %s" % (ref, node(n1), node(n2), val, row["value"]))
            self.included.append((ref, row["value"]))

    def ic(self, ref, model, ports, extra=None):
        """Instance of a subcircuit: `ports` is a list of pin names (or numbers) of `ref` in subckt order.
        A port written '@name' is not a netlist pin: it is a stimulus node `name` of the deck."""
        nodes = []
        for p in ports:
            if p.startswith("@"):
                nodes.append(p[1:])
            else:
                nodes.append(node(self.d.net_of(ref, p)))
        self.add("X%s %s %s" % (ref, " ".join(nodes), model))
        self.included.append((ref, "model " + model))

    def text(self, params=None):
        out = ["* " + self.title, "* generated by make_decks.py from %s" % self.d.folder]
        for k, v in (self.d.overrides or {}).items():
            out.append("* override: %s = %s" % (k, v))
        for lib in self.libs:
            out.append('.include "%s"' % os.path.join(MODELS, lib))
        out += self.lines
        out.append("* included: " + " ".join(r for r, _ in self.included))
        out.append("* excluded: " + " ".join("%s(%s)" % (r, w) for r, w in self.excluded))
        return "\n".join(out) + "\n"
