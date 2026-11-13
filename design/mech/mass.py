#!/usr/bin/env python3
"""Mass estimate: model volumes x densities. Writes out/mass-estimate.csv and prints the total."""
import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring  # noqa: E402

# density g/cm3, source. None of these was fetched in this run: handbook values, UNVERIFIED.
DENS = {
    "pa12": (1.01, "HP MJF PA12 part density 1.01 g/cm3 (handbook value, not fetched: unverified)"),
    "glass": (2.42, "aluminosilicate cover glass about 2.4 g/cm3 (handbook, unverified)"),
    "fr4": (1.85, "FR-4 laminate about 1.85 g/cm3 (handbook, unverified)"),
    "cell": (2.0, "ASSUMED: Li-polymer pouch about 2 g/cm3 overall; replace with the Grepow sample weight"),
    "silicon_pkg": (2.3, "ASSUMED: chip packages taken as silicon 2.33 g/cm3"),
    "screen": (2.5, "ASSUMED: AMOLED module mostly glass"),
    "steel": (7.9, "steel about 7.9 g/cm3 (handbook, unverified)"),
    "silicone": (1.1, "silicone about 1.1 g/cm3 (handbook, unverified)"),
    "foam": (0.3, "ASSUMED: foam pad"),
    "mic": (2.0, "ASSUMED: MEMS mic with metal lid, overall"),
    "switch": (2.0, "ASSUMED: switch overall"),
    "pa12_clear": (1.2, "ASSUMED: clear window / key / adhesive"),
}
MAT = {"cover_glass": "glass", "clear_adhesive": "pa12_clear", "screen": "screen", "foam_pad": "foam",
       "main_board": "fr4", "joystick_board": "fr4", "contact_board": "fr4", "joystick_body": "switch",
       "joystick_stem": "pa12_clear", "record_button": "switch", "record_button_plate": "switch",
       "record_key": "pa12_clear", "recording_light": "silicon_pkg", "clear_window": "pa12_clear",
       "antenna": "silicon_pkg", "cell": "cell", "contact_board_": "fr4", "screen_cable_fold": "pa12_clear",
       "gasket": "silicone"}
SKIP = {"motor_sleeve", "cell_swelling"}   # clearance volumes, no mass
FIXED = {"motor": (0.7, "architecture.md s2 motor 0.7 g [DS]")}


def main():
    m = ring.build(size=9)
    rows = []
    total = 0.0
    for name, solid in [("top_shell", m["top_shell"]), ("base_size9", m["bases"][9])]:
        v = solid.volume
        g = v / 1000 * DENS["pa12"][0]
        rows.append([name, f"{v:.2f}", "pa12", f"{g:.3f}", DENS["pa12"][1]])
        total += g
    for p in m["parts"]:
        n = p["name"]
        if n in SKIP:
            continue
        v = p["solid"].volume
        if n in FIXED:
            g, src = FIXED[n]
            rows.append([n, f"{v:.2f}", "fixed", f"{g:.3f}", src])
        else:
            mat = MAT.get(n) or ("mic" if n.startswith("mic") else "steel" if n.startswith("screw") else "silicon_pkg")
            g = v / 1000 * DENS[mat][0]
            rows.append([n, f"{v:.2f}", mat, f"{g:.3f}", DENS[mat][1]])
        total += g
    out = ring.OUT / "mass-estimate.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "volume_mm3", "material", "mass_g", "density_source"])
        w.writerows(rows)
        w.writerow(["TOTAL size 9", "", "", f"{total:.2f}", "sum"])
    for r in rows:
        print(",".join(r[:4]))
    print(f"TOTAL size 9 mass_g {total:.2f}")


if __name__ == "__main__":
    main()
