import sys, re
BASE = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
DS = BASE + "/design/datasheets/npm1304_datasheet_v1_0.txt"
M1D60 = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pmic-caps-work/w1d_murata_grm155r60j106me15.txt")
M1D61 = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pmic-caps-work/w1d_murata_grm155r61a475meaa.txt")
M1B = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pmic-caps-work/w1b_murata_grm155r61e105ka12.txt")
M1C = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pmic-caps-work/w1c_murata_grt188r61a106ke13.txt")
RING = BASE + "/design/ecad/ring"
NET = RING + "/netlist.csv"
PARTS = RING + "/parts.csv"
REF = RING + "/npm1304-reference.md"
SCH = RING + "/sch-notes.md"
MKN = RING + "/make_netlist.py"
LEAD = BASE + "/design/wiring/lead-decisions.md"

def lines(p):
    with open(p, encoding="utf-8") as f:
        return f.read().split("\n")

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

fails = 0
count = 0
def check_line(path, n, sub):
    global fails, count
    count += 1
    L = lines(path)
    ok = (1 <= n <= len(L)) and (norm(sub) in norm(L[n-1]))
    if not ok:
        fails += 1
    got = norm(L[n-1]) if 1 <= n <= len(L) else "<out of range>"
    print("%s  %s:%d  quote=%r  line=%r" % ("PASS" if ok else "FAIL", path.split("/")[-1], n, sub, got[:140]))

def check_any(path, sub, expect_line=None):
    global fails, count
    count += 1
    L = lines(path)
    hits = [i+1 for i, l in enumerate(L) if norm(sub) in norm(l)]
    ok = bool(hits) and (expect_line is None or expect_line in hits)
    if not ok:
        fails += 1
    print("%s  %s  quote=%r  hits=%s expected=%s" % ("PASS" if ok else "FAIL", path.split("/")[-1], sub, hits[:8], expect_line))

ds = [
 (810,"VBUSOUT must have a decoupling capacitor."),
 (1466,"If a capacitor is placed in parallel with the thermistor, the max capacitance is 100 pF."),
 (1636,"VBUS supplies VSYS. When VBUS is disconnected, VSYS is supplied by its decoupling capacitors until it is"),
 (1646,"VSYS must not be supplied from an external source."),
 (3143,"Recommended values for the inductor are shown in the following table."),
 (3147,"Nominal inductance"),(3148,"2.2"),(3151,"≤ 20"),(3153,"DC resistance (DCR)"),(3154,"≤ 400"),
 (3156,"Saturation current (Isat)"),(3157,"> 350"),
 (3172,"Effective capacitance"),(3173,"≥ 4"),(3175,"ESR"),(3176,"≤ 50"),(3178,"Table 18: Recommended capacitor specifications"),
 (3242,"C = 10 µF"),
 (4648,"They have dedicated input"),(4649,"pins where voltage cannot exceed VSYS."),
 (4678,"Soft start is enabled by default."),
 (4680,"available from the power source connected to LSIN[n]."),
 (4688,"The LDO can be supplied from VOUT1, VOUT2 or VSYS, but must comply with VINLDO."),
 (4691,"This information is valid for Build code B00 and later:"),
 (4695,"The LDO should always be used with soft start enabled."),
 (4728,"Soft start current limit = 25 mA, 10 µF, 0 V"),
 (4738,"Input voltage range"),
 (13660,"Both configured"),(13661,"One configured"),(13664,"Both configured, LDO"),(13666,"One configured, load"),(13667,"switch mode"),
 (13713,"VDDIO"),(13714,"Configured"),
 (13788,"Via to GND-layer on PVSS1"),(13961,"Via to GND-layer on PVSS1"),(14275,"Via to GND-layer on PVSS1"),
 (13482,"GPIO3"),(13486,"GPIO2"),(13514,"GPIO0"),(13542,"GPIO1"),
 (14039,"Figure 57: CSP schematic"),(14353,"Figure 59: CSP schematic"),
 (14044,"C1"),(14045,"1.0 μF"),(14046,"Capacitor, X5R, 25 V, ±10%"),
 (14048,"C5"),(14049,"1.0 μF"),(14050,"Capacitor, X5R, 10 V, ±10%"),
 (14052,"C2, C3, C4, C7, C8,"),(14053,"C9, C10, C11, C12"),(14054,"10 μF"),(14055,"Capacitor, X5R, 16 V, ±20%"),
 (14057,"C6"),(14058,"2.2 μF"),(14059,"Capacitor, X5R, 10 V, ±10%"),
 (14061,"C13"),(14062,"100 nF"),(14063,"Capacitor, X5R"),(14064,"0201"),(14083,"Table 37: Bill of material"),
 (14365,"1.0 μF"),(14366,"Capacitor, X5R, 25 V, ±10%"),(14368,"C5, C14"),(14369,"1.0 μF"),(14370,"Capacitor, X5R, 10 V, ±10%"),
 (14372,"C2, C4, C7"),(14373,"10 μF"),(14374,"Capacitor, X5R, 16 V, ±20%"),(14376,"C6"),(14377,"2.2 μF"),
 (14380,"C13"),(14381,"100 nF"),(14402,"Table 38: Bill of material"),
 (14622,"1.0 μF"),(14623,"Capacitor, X5R, 25 V, ±10%"),(14625,"C5"),(14626,"1.0 μF"),(14627,"Capacitor, X5R, 10 V, ±10%"),
 (14629,"C4"),(14630,"10 μF"),(14631,"Capacitor, X5R, 10 V, ±20%"),(14633,"C6"),(14634,"2.2 μF"),
 (14637,"C13"),(14638,"100 nF"),(14650,"Table 39: Bill of material"),
 (14656,"The BUCK supply voltage should be decoupled with high performance capacitors as close as possible to"),
 (14657,"the supply pins."),
 (14659,"bypass capacitors must be connected as close as possible to the device."),
]
print("== datasheet (npm1304_datasheet_v1_0.txt)")
for n, s in ds:
    check_line(DS, n, s)

mu = [
 (M1D60,49,"静電容量 10µF ±20%"),(M1D60,52,"定格電圧 6.3Vdc"),
 (M1D61,52,"静電容量 4.7µF ±20%"),(M1D61,55,"定格電圧 10Vdc"),
 (M1B,82,"静電容量 1.0μF ±10%"),(M1B,90,"定格電圧 25Vdc"),
 (M1C,79,"Capacitance 10μF ±10%"),(M1C,91,"Rated Voltage 10Vdc"),
]
print("== Murata text")
for p, n, s in mu:
    check_line(p, n, s)

print("== netlist.csv (ring)")
for s, n in [("VBUS,C71,1,~,passive",296),("VBUS,C72,1,~,passive",297),("VBUSOUT,C73,1,~,passive",305),
             ("VSYS,C74,1,~,passive",365),("VSYS,C75,1,~,passive",366),("VSYS,C76,1,~,passive",367),
             ("VSYS,C77,1,~,passive",368),("VSYS,C88,1,~,passive",369),("VSYS,U2,C1,VSYS,power_out",370),
             ("VSYS,U2,C2,VSYS,passive",371),("VSYS,U2,C7,PVDD,power_in",372),
             ("VBAT,C21,1,~,passive",288),("VBAT,C83,1,~,passive",289),("VBAT,C85,1,~,passive",290),
             ("VBAT,U2,D1,VBAT,power_in",293),("VBAT,U2,D2,VBAT,power_in",294),
             ("VDD_1V8,C1,1,~,passive",307),("VDD_1V8,C2,1,~,passive",308),("VDD_1V8,C4,1,~,passive",309),
             ("VDD_1V8,C5,1,~,passive",310),("VDD_1V8,C78,1,~,passive",311),("VDD_1V8,C80,1,~,passive",312),
             ("VDD_1V8,C81,1,~,passive",313),("VDD_1V8,L71,2,~,passive",316),
             ("VDD_3V0,C79,1,~,passive",329),("VDD_3V0,L72,2,~,passive",332),
             ("VDD_MIC,C31,1,~,passive",335),("VDD_MIC,C32,1,~,passive",336),("VDD_MIC,C35,1,~,passive",337),
             ("VDD_MIC,C36,1,~,passive",338),("VDD_MIC,C86,1,~,passive",339),
             ("VDD_SD,C60,1,~,passive",344),("VDD_SD,C61,1,~,passive",345),("VDD_SD,C82,1,~,passive",346),
             ("VDD_SD,C87,1,~,passive",347),
             ("SW1,L71,1,~,passive",263),("SW1,U2,B7,SW1,passive",264),("SW2,L72,1,~,passive",265),("SW2,U2,D7,SW2,passive",266),
             ("GND,U2,A6,AVSS,power_in",126),("GND,U2,A7,PVSS1,power_in",127),("GND,U2,E7,PVSS2,power_in",128),
             ("NTC,RT1,1,~,passive",199),("NTC,U2,D3,NTC,passive",200),("VDD_MIC,U2,A4,LSOUT1/VOUTLDO1,power_out",340),
             ("VDD_SD,U2,A5,LSOUT2/VOUTLDO2,power_out",353)]:
    check_any(NET, s, n)

print("== parts.csv (ring)")
for s in ["C71,C,1.0uF 25V,GRM155R61E105KA12D,OpenRing:Chip_0402,power,no",
          "C72,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,power,no",
          "C73,C,1.0uF,GRM033R60J105MEA2D,OpenRing:Chip_0201,power,no",
          "C74,C,10uF,GRM155R60J106ME15D,OpenRing:Chip_0402,power,no",
          "C75,C,10uF,GRM155R60J106ME15D,OpenRing:Chip_0402,power,no",
          "C76,C,1.0nF,,OpenRing:Chip_0201,power,no",
          "C77,C,1.0nF,,OpenRing:Chip_0201,power,no",
          "C88,C,10uF,GRT188R61A106KE13D,OpenRing:Chip_0603,power,no",
          "C21,C,4.7uF,GRM155R61A475MEAAD,OpenRing:Chip_0402,screen,no",
          "C83,C,10uF,GRM155R60J106ME15,OpenRing:Chip_0402,controls,no",
          "C85,C,2.2uF,0402ZC225KAT2A,OpenRing:Chip_0402,power,no",
          "C1,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,main,no",
          "C2,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,main,no",
          "C4,C,10uF,GRM155R60J106ME15D,OpenRing:Chip_0402,main,no",
          "C5,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,main,no",
          "C78,C,10uF,GRM155R60J106ME15D,OpenRing:Chip_0402,power,no",
          "C80,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,power,no",
          "C81,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,storage,no",
          "C79,C,10uF,GRM155R60J106ME15D,OpenRing:Chip_0402,power,no",
          "C31,C,1uF,GRM033R60J105MEA2D,OpenRing:Chip_0201,mics,no",
          "C32,C,1uF,GRM033R60J105MEA2D,OpenRing:Chip_0201,mics,no",
          "C35,C,1nF C0G,04025A102JAT2A,OpenRing:Chip_0402,mics,no",
          "C36,C,1nF C0G,04025A102JAT2A,OpenRing:Chip_0402,mics,no",
          "C86,C,1.0uF,GRM155R61E105KA12D,OpenRing:Chip_0402,power,no",
          "C87,C,1.0uF,GRM155R61E105KA12D,OpenRing:Chip_0402,power,no",
          "C60,C,2.2uF,0402ZC225KAT2A,OpenRing:Chip_0402,storage,no",
          "C61,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,storage,no",
          "C82,C,100nF,CL03A104KP3NNNC,OpenRing:Chip_0201,storage,no",
          "L71,L,2.2uH,1269AS-H-2R2M=P2,OpenRing:L_Murata_1269AS-H_2.5x2.0,power,no",
          "L72,L,2.2uH,1269AS-H-2R2M=P2,OpenRing:L_Murata_1269AS-H_2.5x2.0,power,no"]:
    count += 1
    hit = [i+1 for i, l in enumerate(lines(PARTS)) if l == s]
    ok = len(hit) == 1
    if not ok: fails += 1
    print("%s  parts.csv quote=%r  line=%s" % ("PASS" if ok else "FAIL", s, hit))

print("== reference, sch-notes, make_netlist, lead-decisions")
for p, n, s in [

 (REF,15,"C5 1.0 uF, 10 V"),
 (REF,23,"C71 4.7 uF, part GRM155R60J475ME47D"),
 (REF,25,"three of 10 uF, 16 V, at balls C1, C2 and C7"),
 (REF,25,"Add a third 10 uF"),
 (REF,26,"VDD_MIC and VDD_SD are used as switches with small capacitors"),
 (REF,26,"C9 to C12: two of 10 uF on each output"),
 (REF,27,"GPIO4"),
 (REF,29,"Nordic lists 0603 for every capacitor"),
 (REF,29,"the ring uses 0402 and 0201"),
 (SCH,214,"C85 2.2 uF X5R 10 V on VBAT at balls D1, D2"),
 (SCH,216,"puts C14 1.0 uF X5R 10 V on LSOUT1"),
 (SCH,253,"C88 with C74, C75 at C1, C2, C7"),
 (MKN,288,"load switch mode outputs"),
 (MKN,432,"C86"),
 (LEAD,24,"C71, C86 and C87 are one part (Murata GRM155R61E105KA12D, 1.0 uF 25 V, 0402)"),
]:
    check_line(p, n, s)

print("RESULT checks=%d fails=%d" % (count, fails))
