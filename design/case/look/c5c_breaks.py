"""proof that test 11a and 11b can fail (C5c): a smooth lid, a lid with a crease scored across the dome, a lid with a sharp top edge. Output look/c5c_test11_breaks.log"""
import sys, json, math
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
sys.path.insert(0, D); sys.path.insert(0, D + "/look")
import case as C, case_check as K, pebble as PB
prm = json.load(open(D + "/out/case_params.json")); PB.PEB.update(prm["pebble"])
H = PB.PEB["H"]; zw1 = PB.PEB["ZW1"]; ax = (PB.PEB["XC"], 0.0)
def run(label, lid, vt):
    a, na = K.lid_crease(lid, zw1 + 0.7, ax, (18.5, 11.4, 6.0))
    b, nb = K.lid_crease(lid, zw1 - 0.15, ax, (18.5, 11.4, 6.0), zmax=zw1 + 0.7)
    redge = vt ** 2 / PB.PEB["ET"]
    print(f"{label}: 11a dome angle {a:.2f} deg (limit 2): {'OK' if a <= 2 else 'FAIL'}; 11b edge radius {redge:.3f} mm (limit 0.30), band angle {b:.2f} deg (limit 10): {'OK' if redge >= 0.3 and b <= 10 else 'FAIL'}", flush=True)
smooth = C.skin_part(H, prm["z_lid0"], H)
run("smooth lid (no dimple)", smooth, PB.PEB["VT"])
creased = smooth - C.box(0, 8, -0.2, 0.2, 40.9, 42.0)
run("lid with a 0.4 mm wide score across the dome (crease)", creased, PB.PEB["VT"])
vt0 = PB.PEB["VT"]; PB.PEB["VT"] = 0.15
sharp = C.skin_part(H, prm["z_lid0"], H)
run("lid with a sharp top edge (edge height 0.15 mm)", sharp, 0.15)
PB.PEB["VT"] = vt0
