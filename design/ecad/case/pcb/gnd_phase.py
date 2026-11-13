#!/usr/bin/env python3
"""Second routing phase: ground.  Run with KiCad's Python:
   run_kipy.sh gnd_phase.py <board with the phase 1 tracks> <out board>
Phase 1 (grid_router with GND_MODE=skip) routed every net except ground pads.  Here the ground pours are added on F.Cu, In2.Cu and B.Cu (the plane on In1.Cu is already
in the board), the zones are filled, and every ground pad that is still not connected (kicad-cli drc unconnected items) is routed to a via by grid_router
(GND_MODE=only:<list>), up to 5 rounds.  Reports the unconnected count after every round."""
import json, os, shutil, subprocess, sys
import pcbnew
import build_boards as BB

HERE = os.path.dirname(os.path.abspath(__file__))
K = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pcb/run_kipy.sh")
src, dst = sys.argv[1], sys.argv[2]
W = os.path.join(HERE, "work")
tag = os.path.splitext(os.path.basename(dst))[0]
tmp = os.path.join(W, tag + "_gp.kicad_pcb")
pro = dst.replace(".kicad_pcb", ".kicad_pro")
BB.write_pro(BB.PCB1_CLASSES, pro)
b = pcbnew.LoadBoard(src)
cache = {n.GetNetname(): n for n in b.GetNetsByNetcode().values()}
BB.add_pcb1_outer_pours(b, cache)
BB.fill_all(b)
pcbnew.SaveBoard(tmp, b)
shutil.copy(pro, tmp.replace(".kicad_pcb", ".kicad_pro"))
for rnd in range(6):
    rc, nv, nu, rep = BB.drc(tmp, tmp + ".json")
    gp = set()
    for u in rep["unconnected_items"]:
        for it in u["items"]:
            d = it["description"]
            if d.startswith("Pad ") and "[GND]" in d:
                gp.add((d.split(" of ")[1].split(" on ")[0], d.split()[1]))
    print("round %d: violations %d unconnected %d, unconnected ground pads %d" % (rnd, nv, nu, len(gp)))
    if not gp:
        break
    lst = os.path.join(W, tag + "_gnd_list.txt")
    open(lst, "w").write("\n".join("%s %s" % p for p in sorted(gp)) + "\n")
    inp = os.path.join(W, tag + "_gnd_in.txt")
    out = os.path.join(W, tag + "_gnd_out.txt")
    env = dict(os.environ, GND_MODE="only:" + lst)
    subprocess.check_call([K, "route_io.py", "export", tmp, inp], env=env, cwd=HERE, stdout=open(inp + ".log", "w"), stderr=subprocess.STDOUT)
    rc = subprocess.call([os.path.join(HERE, "grid_router"), inp, out, "60", "1"], cwd=HERE, stdout=open(out + ".log", "w"), stderr=subprocess.STDOUT)
    print("  grid_router exit", rc, open(out).read().strip().splitlines()[-1])
    nxt = os.path.join(W, tag + "_gp2.kicad_pcb")
    subprocess.check_call([K, "route_io.py", "import", tmp, out, nxt], cwd=HERE, stdout=open(nxt + ".log", "w"), stderr=subprocess.STDOUT)
    b = pcbnew.LoadBoard(nxt)
    BB.fill_all(b)
    pcbnew.SaveBoard(tmp, b)
pcbnew.SaveBoard(dst, pcbnew.LoadBoard(tmp))
print("saved", dst)
