"""Write design/mfg/assembly/hotbar-fixture.svg (the hot-bar fixture, top view and section A-A) from the numbers below.
usage: python3 -I make_fixture_svg.py <out.svg> <values.log>
Every number is printed to <values.log> with its source, so the drawing and hotbar-joint.md can be checked against one list."""
import sys

out, vlog = sys.argv[1], sys.argv[2]
S = 20.0                     # px per mm
V = []                       # (name, value, source)


def val(name, v, src):
    V.append((name, v, src))
    return v


BX = val("base length X", 40.0, "starting value, lead's to confirm (board 27.2 + 2 x 6.4 margin for the hands and tape)")
BY = val("base width Y", 26.0, "starting value, lead's to confirm (board 12.6 + 2 x 6.7 for the ribbon necks to lie on)")
BZ = val("base thickness", 5.0, "starting value, lead's to confirm")
BOARD_X = val("board length", 27.2, "design/mfg/specs/main-board.md line 27")
BOARD_Y = val("board width", 12.6, "design/mfg/specs/main-board.md line 28")
BOARD_T = val("board thickness", 0.30, "design/ecad/ring/pcb/fab/stackup.txt line 15 (0.30 mm +-0.025)")
PCL = val("pocket clearance per side", 0.05, "starting value, lead's to confirm")
PX, PY = BOARD_X + 2 * PCL, BOARD_Y + 2 * PCL
val("board pocket X", round(PX, 3), "arithmetic: 27.2 + 2 x 0.05")
val("board pocket Y", round(PY, 3), "arithmetic: 12.6 + 2 x 0.05")
PR = val("pocket corner radius", 0.85, "arithmetic: board corner 0.8 (design/mech/thin/thin.py line 473 rbox radius 0.8) + 0.05")
PD = val("pocket depth", BOARD_T, "arithmetic: equal to the board thickness 0.30, so the parts face lies flush with the base top")
CH_HALF = val("relief channel half width (|Y|)", 3.30, "arithmetic: J1 body reaches |Y| 3.093 (hotbar-work/logs/screen-face-parts.log), + 0.207 clearance; every screen face part lies within |Y| 3.093")
CH_D = val("relief channel depth below the pocket floor", 1.30, "arithmetic: J1 housing 0.9 high (design/wiring/screen-cable-study.md line 59, as cited in assembly.md line 96) + 0.40 clearance (starting value)")
LEDGE = (CH_HALF, PY / 2)
val("support ledges |Y|", f"{LEDGE[0]:.2f} to {LEDGE[1]:.2f}", "arithmetic: channel edge to pocket wall; the J_BAND lands lie at |Y| 3.60 to 5.05 and the feet at |Y| 3.40 to 5.145 (band-interface.md lines 23 to 26, 91), wholly on the ledges")
NOTCH_W = val("tweezer notch width at each X end", 3.0, "starting value, lead's to confirm")
NOTCH_L = val("tweezer notch length beyond the pocket", 1.5, "starting value, lead's to confirm")
FOOT = (-3.5, -1.0, 3.4, 5.145)
val("foot outline (X0, X1, |Y|0, |Y|1)", FOOT, "band-interface.md line 91 (X -3.5 to -1.0, u 0 to 1.745 from |Y| 3.4)")
BLADE = (-3.5, -1.0, 3.45, 5.05)
val("hot-bar blade face (X0, X1, |Y|0, |Y|1)", BLADE, "starting value, lead's to confirm: 2.5 x 1.6, the stiffener (thin.py line 81 foot_stiff_y 3.45 to 5.05); the 3 mm blade of band-interface.md line 137 overlaps R61 by 0.040 mm (hotbar-work/logs/geom_check.log)")
BARS = []   # no copper marks: no free place beside 3 of the 4 foot edges (hotbar-work/logs/scan_bars.log); the foot is aligned to the lands themselves
LANDS = [(-3.015, 3.875), (-2.505, 3.875), (-1.995, 3.875), (-1.485, 3.875), (-3.015, 4.775), (-2.505, 4.775), (-1.995, 4.775), (-1.485, 4.775)]
val("land centres (X, |Y|), 0.30 x 0.55", LANDS, "band-interface.md lines 23 to 26")

W, H = 1150, 1240
ox, oy = W / 2, 375.0        # top view: model (0, 0) at (ox, oy); X right, +Y down (the parts face seen from above, as the KiCad front view)


def tx(x):
    return ox + x * S


def ty(y):
    return oy + y * S


el = []
el.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')
el.append('<text x="20" y="28" font-size="18" font-family="Helvetica">Hot-bar fixture for the ribbon joints J_BAND_A and J_BAND_B (design/mfg/assembly/hotbar-joint.md, section 3). All sizes in mm.</text>')
el.append('<text x="20" y="50" font-size="13" font-family="Helvetica">TOP VIEW: the board lies PARTS FACE UP (KiCad F.Cu, the chips); its screen face and J1 hang down in the relief channel.</text>')
el.append('<text x="20" y="68" font-size="13" font-family="Helvetica">X to the right (+X = fingertip end), +Y down the page, as in the board file seen from the parts face.</text>')
# base
el.append(f'<rect x="{tx(-BX/2)}" y="{ty(-BY/2)}" width="{BX*S}" height="{BY*S}" fill="#e8e8e8" stroke="black" stroke-width="2"/>')
# notches
for sg in (-1, 1):
    x0 = PX / 2 if sg > 0 else -PX / 2 - NOTCH_L
    el.append(f'<rect x="{tx(x0)}" y="{ty(-NOTCH_W/2)}" width="{NOTCH_L*S}" height="{NOTCH_W*S}" fill="#cfcfcf" stroke="black"/>')
# pocket and channel
el.append(f'<rect x="{tx(-PX/2)}" y="{ty(-PY/2)}" width="{PX*S}" height="{PY*S}" rx="{PR*S}" fill="#d6d6d6" stroke="black" stroke-width="1.5"/>')
el.append(f'<rect x="{tx(-PX/2)}" y="{ty(-CH_HALF)}" width="{PX*S}" height="{2*CH_HALF*S}" fill="#b0b0b0" stroke="black" stroke-dasharray="6,3"/>')
# lands, feet, bars, blade on both joints
for sg, name in ((-1, "J_BAND_A / FLEX1"), (1, "J_BAND_B / FLEX2")):
    for (x, y) in LANDS:
        el.append(f'<rect x="{tx(x-0.15)}" y="{ty(sg*y-0.275)}" width="{0.30*S}" height="{0.55*S}" fill="#c08000" stroke="none"/>')
    fy0, fy1 = sorted((sg * FOOT[2], sg * FOOT[3]))
    el.append(f'<rect x="{tx(FOOT[0])}" y="{ty(fy0)}" width="{(FOOT[1]-FOOT[0])*S}" height="{(fy1-fy0)*S}" fill="none" stroke="#0050c0" stroke-width="1.5" stroke-dasharray="8,3,2,3"/>')
    by0, by1 = sorted((sg * BLADE[2], sg * BLADE[3]))
    el.append(f'<rect x="{tx(BLADE[0])}" y="{ty(by0)}" width="{(BLADE[1]-BLADE[0])*S}" height="{(by1-by0)*S}" fill="none" stroke="red" stroke-width="1"/>')
    for (x0, x1, y0, y1) in BARS:
        a, b = sorted((sg * y0, sg * y1))
        el.append(f'<rect x="{tx(x0)}" y="{ty(a)}" width="{(x1-x0)*S}" height="{(b-a)*S}" fill="#00a000"/>')
    # neck leaving over the board edge, outward
    ny0, ny1 = sorted((sg * FOOT[3], sg * (BY / 2)))
    el.append(f'<rect x="{tx(-3.4)}" y="{ty(ny0)}" width="{1.8*S}" height="{(ny1-ny0)*S}" fill="none" stroke="#0050c0" stroke-dasharray="4,3"/>')
    ly = ty(sg * 8.6)
    el.append(f'<text x="{tx(-12.0)}" y="{ly}" font-size="13" font-family="Helvetica">{name}: ribbon leaves over this board edge, lies flat on the base top; tape it here</text>')
# dimensions (text callouts with leader lines)
def dim_h(x0, x1, y, txt):
    el.append(f'<line x1="{tx(x0)}" y1="{ty(y)}" x2="{tx(x1)}" y2="{ty(y)}" stroke="black" marker-start="url(#a)" marker-end="url(#a)"/>')
    el.append(f'<text x="{(tx(x0)+tx(x1))/2}" y="{ty(y)-4}" font-size="12" text-anchor="middle" font-family="Helvetica">{txt}</text>')


def dim_v(x, y0, y1, txt):
    el.append(f'<line x1="{tx(x)}" y1="{ty(y0)}" x2="{tx(x)}" y2="{ty(y1)}" stroke="black" marker-start="url(#a)" marker-end="url(#a)"/>')
    el.append(f'<text x="{tx(x)+4}" y="{(ty(y0)+ty(y1))/2}" font-size="12" font-family="Helvetica">{txt}</text>')


dim_h(-BX / 2, BX / 2, -BY / 2 - 1.0, f"base {BX:.1f}")
dim_v(BX / 2 + 0.6, -BY / 2, BY / 2, f"base {BY:.1f}")
dim_h(-PX / 2, PX / 2, 7.4, f"pocket {PX:.2f} (board 27.20 + 2 x 0.05), corners R{PR:.2f}, {PD:.2f} deep")
dim_v(-PX / 2 - 2.5, -PY / 2, PY / 2, f"{PY:.2f}")
el.append(f'<text x="{tx(-PX/2-6.4)}" y="{ty(-PY/2-0.4)}" font-size="12" font-family="Helvetica">pocket width</text>')
dim_v(4.0, -CH_HALF, CH_HALF, f"{2*CH_HALF:.2f}")
el.append(f'<text x="{tx(-13.0)}" y="{ty(2.6)}" font-size="12" font-family="Helvetica">relief channel {2*CH_HALF:.2f} wide (|Y| up to {CH_HALF:.2f}), {CH_D:.2f} deeper than the pocket floor, full pocket length</text>')
dim_h(FOOT[0], FOOT[1], 5.9, "foot 2.50 (X -3.50 to -1.00)")
el.append(f'<text x="{tx(-13.0)}" y="{ty(-2.2)}" font-size="12" font-family="Helvetica">ledges |Y| {LEDGE[0]:.2f} to {LEDGE[1]:.2f} carry the board; the lands and feet sit on them</text>')
el.append(f'<text x="{tx(-13.0)}" y="{ty(-1.5)}" font-size="12" font-family="Helvetica">model (0, 0) = board centre = pocket centre = base centre</text>')
el.append(f'<text x="{tx(-BX/2)+4}" y="{ty(BY/2)+18}" font-size="12" font-family="Helvetica">Legend: brown = board lands 0.30 x 0.55 at 0.51 pitch; blue dash-dot = foot outline 2.50 x 1.745;</text><text x="{tx(-BX/2)+4}" y="{ty(BY/2)+54}" font-size="12" font-family="Helvetica">red = hot-bar blade face 2.50 x 1.60.</text>')
el.append(f'<text x="{tx(-BX/2)+4}" y="{ty(BY/2)+36}" font-size="12" font-family="Helvetica">Engrave on the base top: "PARTS FACE UP", "A FLEX1" beside the upper joint, "B FLEX2" beside the lower joint, an arrow "+X fingertip" to the right.</text>')
# section A-A at X -2.25 through both joints: Y horizontal, Z up, scale S
S2 = 38.0
sx0, sz0 = ox, 1020.0


def sxp(y):
    return sx0 + y * S2


def szp(z):
    return sz0 - z * S2


el.append(f'<text x="20" y="{szp(BZ)-40}" font-size="13" font-family="Helvetica">SECTION A-A at X -2.25 (through both feet), seen from the fingertip end; Y to the right, Z up. Base top = Z 0.</text>')
# base with pocket and channel cut: polygon
pts = [(-BY/2, -BZ), (BY/2, -BZ), (BY/2, 0), (PY/2, 0), (PY/2, -PD), (CH_HALF, -PD), (CH_HALF, -PD-CH_D), (-CH_HALF, -PD-CH_D), (-CH_HALF, -PD), (-PY/2, -PD), (-PY/2, 0), (-BY/2, 0)]
el.append('<polygon points="' + " ".join(f"{sxp(y)},{szp(z)}" for y, z in pts) + '" fill="#e8e8e8" stroke="black" stroke-width="1.5"/>')
# board
el.append(f'<rect x="{sxp(-BOARD_Y/2)}" y="{szp(0)-0}" width="{BOARD_Y*S2}" height="{BOARD_T*S2}" fill="#2f7f2f" stroke="black"/>')
# J1 body hanging in the channel
el.append(f'<rect x="{sxp(-3.093)}" y="{szp(-BOARD_T)}" width="{6.186*S2}" height="{0.9*S2}" fill="#404040"/>')
el.append(f'<text x="{sxp(-1.0)}" y="{szp(-BOARD_T-1.2)+14}" font-size="11" fill="white" font-family="Helvetica">J1</text>')
# feet with stiffener and blades
for sg in (-1, 1):
    fy0, fy1 = sorted((sg * FOOT[2], sg * FOOT[3]))
    el.append(f'<rect x="{sxp(fy0)}" y="{szp(0.02+0.03+0.11)}" width="{(fy1-fy0)*S2}" height="{0.11*S2}" fill="#d08000" stroke="black" stroke-width="0.5"/>')
    sy0, sy1 = sorted((sg * 3.45, sg * 5.05))
    el.append(f'<rect x="{sxp(sy0)}" y="{szp(0.16+0.10)}" width="{(sy1-sy0)*S2}" height="{0.10*S2}" fill="#f0c060" stroke="black" stroke-width="0.5"/>')
    by0, by1 = sorted((sg * BLADE[2], sg * BLADE[3]))
    el.append(f'<rect x="{sxp(by0)}" y="{szp(0.26+3.0)}" width="{(by1-by0)*S2}" height="{3.0*S2}" fill="none" stroke="red" stroke-width="1.5"/>')
    ny = sg * FOOT[3]
    el.append(f'<line x1="{sxp(ny)}" y1="{szp(0.105)}" x2="{sxp(sg*(BY/2+1.0))}" y2="{szp(0.105)}" stroke="#d08000" stroke-width="2.2"/>')
el.append(f'<text x="{sxp(-12.5)}" y="{szp(3.6)}" font-size="12" font-family="Helvetica">blade presses DOWN on the stiffener (red); heat goes through stiffener 0.10 + ribbon 0.11 into the tinned board lands</text>')
el.append(f'<text x="{sxp(-12.5)}" y="{szp(-BZ)+18}" font-size="12" font-family="Helvetica">pocket depth {PD:.2f}; channel {2*CH_HALF:.2f} wide x {CH_D:.2f} deeper; base {BZ:.1f} thick; ribbon lands face DOWN, stiffener up</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,4 L8,4" stroke="black"/></marker></defs>'
       + "".join(el) + "</svg>\n")
open(out, "w").write(svg)
with open(vlog, "w") as f:
    for n, v, s in V:
        f.write(f"{n} = {v} | {s}\n")
print("written", out, len(svg), "bytes;", len(V), "values")
