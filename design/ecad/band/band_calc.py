"""Current, voltage drop, motor lead cut lengths and lengths table, from evidence/build_rows.json (written by build_band.py) and band_geom.py.
Copper: 12 um, resistivity 1.72e-5 ohm mm at 20 C (annealed copper, standard value); IPC-2221 external limit I = 0.048 dT^0.44 A^0.725 (A in mil2)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import band_geom as G, band_layout as L
rows = {(r["kind"], r["us"]): r for r in json.load(open(os.path.join(HERE, "evidence", "build_rows.json")))}
RHO, T = 1.72e-5, 0.012
def rpm(w): return RHO / (w * T)
def ipc(w, dT=10.0):
    a = w * T / 0.0254 ** 2
    return 0.048 * dT ** 0.44 * a ** 0.725
print("line  width  ohm/mm  IPC-2221 limit at 10 K rise (A)")
for w in (0.08, 0.10, 0.20):
    print(f"      {w:.2f}   {rpm(w):.5f}   {ipc(w):.3f}")
print()
print("US  FLEX1 flat  FLEX2 flat  model path1  model path2")
for us in G.SIZES:
    print(f"{us:>2}  {rows[('FLEX1',us)]['flat_length']:>9.3f}  {rows[('FLEX2',us)]['flat_length']:>9.3f}  {rows[('FLEX1',us)]['model_path']:>10.3f}  {rows[('FLEX2',us)]['model_path']:>10.3f}")
print()
I_START, I_CELL = 0.175, 0.2275
print(f"Motor: start current {I_START*1000:.0f} mA (motor-drive.md: Jinlong W0525 p5-6, rotor held, 3.0 V); cell total at a start 227.5 mA at 3.30 V (motor-drive.md section 2.5).")
print("US  VMOT line mm  drop mV (0.20 wide)  GND line mm  drop mV   motor lead cut length (mm, from the motor edge to the land end): P1 / P2")
for us in G.SIZES:
    S = G.Size(us); r = rows[("FLEX1", us)]
    m1 = r["mot_m1_u"]
    lv = (m1 - L.U_NEAR)                            # VMOT from land 7 to motor land
    lg = (m1 + 1.0 - L.U_FAR) + 1.5                 # GND from land 6 via the B.Cu lane to the motor land, with the strap
    dv, dg = lv * rpm(0.20) * I_START * 1000, lg * rpm(0.20) * I_START * 1000
    # lead: motor centre arc position on the tail axis
    uc = S.u_j + S.s_motor_c if hasattr(S, "s_motor_c") else S.u_j + S.motor_s_model[0] - 0.7
    cut = []
    for k, ul in enumerate((m1, m1 + 1.0)):
        exit_u = uc + (-0.5 if k == 0 else 0.5)
        along = abs(ul - exit_u)
        motor_x = 0.8 if us in (7, 12) else 0.7        # model v8 SIZE_TABLE last column
        across = motor_x                              # motor rim at v = motor_x (X = motor_x - 2.5 + 2.5 ... rim v = motor_x) to the stripped end at v 0.0
        cut.append(math.hypot(along, across))
    print(f"{us:>2}  {lv:>10.2f}  {dv:>16.1f}  {lg:>10.2f}  {dg:>8.1f}   {cut[0]:.2f} / {cut[1]:.2f}  (motor land slide vs model {r['mot_slide_mm']:+.2f})")
print()
print("Cell line (FLEX2): VBAT and GND, 0.20 wide, current 227.5 mA")
print("US  VBAT line mm (land 1 to PRT1 land)  drop mV   GND line mm  drop mV")
for us in G.SIZES:
    r = rows[("FLEX2", us)]; S = G.Size(us)
    uL1 = S.u_j + r["prt1_l1_s"]
    l = uL1 - L.U_FAR
    print(f"{us:>2}  {l:>12.2f}  {l*rpm(0.20)*I_CELL*1000:>20.1f}  {l+0.9:>8.2f}  {(l+0.9)*rpm(0.20)*I_CELL*1000:>6.1f}")
