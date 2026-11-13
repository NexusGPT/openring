#!/usr/bin/env python3
"""Draw design/wiring/product-wiring.csv as one A3 sheet: product-wiring.svg and product-wiring.pdf.

Each joint is a panel; in it each board or off-board part is a block (end A blocks on the left, end B blocks on the
right) and each csv line is one conductor drawn between them, named at both ends (signal, reference.pin).
Line style shows the state: solid black = drawn and routed (copper); solid green = specified and landed (lead, wire,
cable, pin: ends landed and carrier fully specified); dashed blue = drawn, not routed;
dash-dot orange = stated in text only; red = not drawn.
Prints the number of csv lines and the number of conductors drawn.

Run: design/.venv/bin/python design/wiring/draw_wiring.py
"""
import csv
import os
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
HERE = os.path.join(ROOT, "design/wiring")
CSV = os.path.join(HERE, "product-wiring.csv")
STYLE = {
    "drawn and routed": dict(color="black", ls="-", lw=0.6),
    "specified and landed": dict(color="#1a7a2e", ls="-", lw=0.8),
    "drawn, not routed": dict(color="#1f5fbf", ls=(0, (4, 2)), lw=0.7),
    "stated in text only": dict(color="#d07000", ls=(0, (5, 2, 1, 2)), lw=0.7),
    "not drawn": dict(color="red", ls="-", lw=1.0),
}
JOINT_TITLE = {
    "R1": "R1 ring board J_BAND_A to FLEX1", "R2": "R2 ring board J_BAND_B to FLEX2",
    "R3": "R3 joystick switch lines (FLEX1)", "R4": "R4 joystick switch grounds (FLEX1)",
    "R5": "R5 motor M1: FLEX1 lines and motor leads", "R6": "R6 cell lines on FLEX2 (to the PRT1 tab lands)",
    "R7": "R7 thermistor line on FLEX2", "R8": "R8 thermistor ground on the PRT1 board",
    "R9": "R9 charging pads CP1 to CP4 on FLEX2", "R10": "R10 cell protection circuit PRT1: output tabs",
    "R11": "R11 antenna feed (main board copper)", "R12": "R12 antenna ground and trim terminals",
    "R13": "R13 screen cable into J1", "R15": "R15 ring pads to case spring pins P1 to P4",
    "R16": "R16 band metal to case touch electrode E1 (no conductor)",
    "C1": "C1 case cell lead +", "C2": "C2 case cell lead -", "C3": "C3 case thermistor TH1 leads",
    "C4": "C4 spring pins on the pin board", "C5": "C5 case wires pin board to main board", "C6": "C6 USB-C socket",
}

ROW = 3.25       # mm between conductors
HEAD = 5.5       # mm for a panel title
GAP = 2.5        # mm between panels
FS = 6.0         # font size, points (about 1.8 mm cap height): readable on A3
W, H = 420.0, 297.0
MARGIN = 8.0


def jkey(j):
    return (0 if j.startswith("R") else 1, int(j[1:]) if j[1:].isdigit() else 99)


def end_label(r, e):
    ref, pin, sig = r["end_%s_ref" % e], r["end_%s_pin" % e].split(" ")[0], r["signal_%s" % e]
    if r["end_%s_kind" % e] == "node":
        return "%s (%s)" % (sig, r["end_%s_pin" % e].replace("reaches land ", "via land "))
    if r["end_%s_kind" % e] == "none":
        return "band metal (no terminal)"
    return "%s.%s  %s" % (ref, pin, sig)


def short_board(b):
    return (b.replace("off board ", "").replace("(", "").replace(")", "")
            .replace("ring main board", "ring main board").strip())


def carrier_label(r):
    k = r["carrier_kind"]
    if k == "copper":
        lo = [r["copper_mm_us%d" % s] for s in (7, 8, 9, 10, 11, 12, 13) if r.get("copper_mm_us%d" % s)]
        if lo:   # true range over the seven sizes (the length is not monotonic in the size), written as in the csv
            lo = [min(lo, key=float), max(lo, key=float)]
        base = r["carrier"].split(",")[0].replace(" band circuit (flex1/flex2 board per size)", "")
        if "main board copper" in r["carrier"]:
            base = "main board copper"
        if "PRT1 board" in r["carrier"]:
            base = "PRT1 board copper"
        return base + (" %s-%s mm" % (lo[0], lo[1]) if len(lo) == 2 else "")
    if k in ("lead", "wire"):
        cuts = [r["cut_mm_us%d" % s] for s in (7, 8, 9, 10, 11, 12, 13) if r.get("cut_mm_us%d" % s)]
        a, b = (min(cuts, key=float), max(cuts, key=float)) if cuts else ("", "")   # true range over the seven sizes
        cut = a if float(a or 0) == float(b or 0) else "%s-%s" % (a, b)
        mark = r.get("carrier_marking", "")      # the colour of the wire or lead is drawn with it
        first = r["carrier"].split(",")[0]
        if mark and mark.split()[0] in first:    # colour already in the carrier text
            mark = ""
        return "%s%s, cut %s mm" % (first, (", " + mark) if mark else "", cut)
    if k == "part cable":
        return "screen's own cable, contact %s" % r["end_A_pin"].split(" ")[0]
    if k == "spring pin":
        return "spring pin (pressed)"
    if k == "tab":
        return "PRT1 tab (nickel strip)"
    if k == "inside the part":
        return "inside the cell pack" if "pack" in r["end_A_board"] else "inside the switch"
    if k == "none":
        return "no conductor, gap 2.28-2.42 mm"
    return r["carrier"][:30]


def main():
    rows = list(csv.DictReader(open(CSV, newline="", encoding="utf-8")))
    groups = {}
    for r in rows:
        # a sensing gap (carrier_kind none, no conductor) is drawn apart, in its own panel
        groups.setdefault("GAP" if r["carrier_kind"] == "none" else r["joint"], []).append(r)
    order = sorted((g for g in groups if g != "GAP"), key=jkey) + (["GAP"] if "GAP" in groups else [])
    # split panels into two columns of about equal height
    heights = [HEAD + ROW * len(groups[j]) + GAP for j in order]
    total = sum(heights)
    col_of, acc = {}, 0.0
    for j, h in zip(order, heights):
        col_of[j] = 0 if acc + h / 2 <= total / 2 else 1
        acc += h
    global ROW
    avail = H - 11.0 - 8.0
    need = []
    for c in (0, 1):
        js = [j for j in order if col_of[j] == c]
        need.append((avail - len(js) * (HEAD + GAP)) / max(1, sum(len(groups[j]) for j in js)))
    ROW = min(5.0, min(need))
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    ax.text(MARGIN, 6.5, "Ring and case: every conductor, one line each (from design/wiring/product-wiring.csv, %d lines)"
            % len(rows), fontsize=8.5, weight="bold", va="center")
    lx = 222
    for i, (st, sty) in enumerate(STYLE.items()):
        x0 = lx + i * 39
        ax.plot([x0, x0 + 9], [6.5, 6.5], **sty)
        ax.text(x0 + 10.5, 6.5, st, fontsize=FS, va="center")
    colw = (W - 2 * MARGIN - 6) / 2
    ybase = 11.0
    y = [ybase, ybase]
    drawn = 0
    gaps_drawn = 0
    for j in order:
        c = col_of[j]
        x0 = MARGIN + c * (colw + 6)
        rs = sorted(groups[j], key=lambda r: (r["end_A_board"], r["end_B_board"], r["id"]))
        y0 = y[c]
        ax.add_patch(Rectangle((x0, y0), colw, HEAD + ROW * len(rs), fill=False, lw=0.3, ec="#888888"))
        ends = sorted({e for r in rs for e in (r.get("end_joints") or "").split(";") if e})
        title = ("SENSING GAP, NO CONDUCTOR (counted apart from the conductors): " + ", ".join(
            JOINT_TITLE.get(r["joint"], r["joint"]) for r in rs)) if j == "GAP" else JOINT_TITLE.get(j, j)
        ax.text(x0 + 1.5, y0 + HEAD / 2, title + ("   (ends also in " + ", ".join(ends) + ")" if ends else "")
                + "   %d line%s" % (len(rs), "" if len(rs) == 1 else "s"), fontsize=FS + 0.8, weight="bold", va="center")
        bA = (x0 + 1.5, x0 + 38)       # end A block
        bB = (x0 + colw - 38, x0 + colw - 1.5)
        top = y0 + HEAD
        # blocks: consecutive rows with the same board form one block
        for side, (bx0, bx1) in (("A", bA), ("B", bB)):
            k = 0
            while k < len(rs):
                b = rs[k]["end_%s_board" % side]
                k2 = k
                while k2 + 1 < len(rs) and rs[k2 + 1]["end_%s_board" % side] == b:
                    k2 += 1
                yy0, yy1 = top + ROW * k + 0.3, top + ROW * (k2 + 1) - 0.3
                ax.add_patch(Rectangle((bx0, yy0), bx1 - bx0, yy1 - yy0, fill=True, fc="#eef2f7", ec="#334455", lw=0.4))
                refs = []
                for rr in rs[k:k2 + 1]:
                    if rr["end_%s_kind" % side] in ("terminal", "land", "face") and rr["end_%s_ref" % side] not in refs:
                        refs.append(rr["end_%s_ref" % side])
                nlines = max(1, int((yy1 - yy0) / 2.3))
                parts = textwrap.wrap(short_board(b), 30)
                if refs:
                    parts += textwrap.wrap(", ".join(refs[:8]) + (" ..." if len(refs) > 8 else ""), 30)
                label = "\n".join(parts[:nlines])
                ax.text((bx0 + bx1) / 2, (yy0 + yy1) / 2, label,
                        fontsize=FS - 0.4, ha="center", va="center", color="#223344")
                k = k2 + 1
        for k, r in enumerate(rs):
            yy = top + ROW * k + ROW / 2
            xa, xb = bA[1] + 1.0, bB[0] - 1.0
            if j == "GAP":
                ax.plot([xa, xb], [yy, yy], color="#888888", ls=(0, (1, 2)), lw=0.8)
                gaps_drawn += 1
            else:
                ax.plot([xa, xb], [yy, yy], **STYLE.get(r["state"], STYLE["not drawn"]))
                drawn += 1
            ax.text(xa + 0.6, yy - 0.35, end_label(r, "A"), fontsize=FS, va="bottom", ha="left")
            ax.text(xb - 0.6, yy - 0.35, end_label(r, "B"), fontsize=FS, va="bottom", ha="right")
            ax.text((xa + xb) / 2, yy + 0.35, "%s  %s" % (r["id"], carrier_label(r)), fontsize=FS - 0.8, va="top",
                    ha="center", color="#444444")
        y[c] = y0 + HEAD + ROW * len(rs) + GAP
    ax.text(MARGIN, H - 3.5, "Line style = state of the line in the csv (column state). Copper lengths are the shortest copper "
            "path pad to pad in the band boards (smallest to largest over US 7 to 13); cut lengths are the lead or wire cut length (smallest to largest over US 7 to 13). "
            "Made by design/wiring/draw_wiring.py.", fontsize=FS - 0.5, va="center")
    for ext in ("svg", "pdf"):
        fig.savefig(os.path.join(HERE, "product-wiring." + ext), format=ext, metadata={"Date": None} if ext == "pdf" else None)
    n_gap = sum(1 for r in rows if r["carrier_kind"] == "none")
    print("csv lines:", len(rows), "=", len(rows) - n_gap, "conductors +", n_gap, "sensing gap")
    print("conductors drawn:", drawn, "; sensing gaps drawn apart:", gaps_drawn)
    print("columns used: heights %.1f and %.1f mm of %.1f" % (y[0], y[1], H))
    if drawn != len(rows) - n_gap or gaps_drawn != n_gap:
        print("MISMATCH")
        sys.exit(1)


if __name__ == "__main__":
    main()
