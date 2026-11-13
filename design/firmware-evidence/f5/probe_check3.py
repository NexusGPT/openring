"""Which signal-like names of firmware.md (outside the change lists) check 3 accepts as board nets."""
import importlib.util
import re
import sys

spec = importlib.util.spec_from_file_location("fc", sys.argv[1])
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)
fw = open(sys.argv[2], encoding="utf-8").read()
arch = open(sys.argv[3], encoding="utf-8").read()
rows = fc.read_netlist(sys.argv[4])
a, b = fc.change_list_span(fw)
body = fw[:a] + fw[b:]
signals, pins, pairs, spares = fc.arch_pins(arch)
prefixes = sorted({s.split("_")[0] for s in signals if "_" in s} | {"LED", "MOTOR"})
sig_re = re.compile(r"(?<![A-Za-z0-9_])((?:" + "|".join(map(re.escape, prefixes)) + r")_[A-Z0-9_]+)(?![A-Za-z0-9_])")
fw_sigs = set(sig_re.findall(body))
board = {n for n, r, pn, pname in rows} - {n for n, r, pn, pname in rows if r == "U1"}
print("prefixes:", prefixes)
print("names not in architecture section 7, accepted as board nets:", sorted((fw_sigs - signals) & board))
print("names not in architecture section 7 and not board nets:", sorted((fw_sigs - signals) - board))
