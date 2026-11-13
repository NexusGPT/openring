import re
BASE = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
DS = BASE + "/design/datasheets/npm1304_datasheet_v1_0.txt"
RING = BASE + "/design/ecad/ring"
W = RING + "/pmic-caps-work"
NET = RING + "/netlist.csv"
REF = RING + "/npm1304-reference.md"
SCH = RING + "/sch-notes.md"
MKN = RING + "/make_netlist.py"
LEAD = BASE + "/design/wiring/lead-decisions.md"
def lines(p):
    return open(p, encoding="utf-8").read().split("\n")
def norm(s):
    return re.sub(r"\s+", " ", s).strip()
fails = 0; count = 0
def chk(path, n, sub):
    global fails, count
    count += 1
    L = lines(path)
    got = norm(L[n-1]) if 1 <= n <= len(L) else ""
    ok = norm(sub) in got
    fails += (not ok)
    print("%s %s:%d quote=%r line=%r" % ("PASS" if ok else "FAIL", path.split("/")[-1], n, sub, got[:110]))
ds = [(4648,"They have dedicated input"),(4649,"pins where voltage cannot exceed VSYS."),(4679,"Current limiting is only"),
 (4694,"The LDO can be supplied from VOUT1, VOUT2 or VSYS, but must comply with VINLDO."),
 (4726,"tSS"),(4727,"Soft start time"),(4729,"to 5 V"),(4730,"1.8"),(4731,"ms"),(4737,"VINLS"),(4739,"1.0"),(4740,"VSYS"),
 (3149,"μH"),(3152,"%"),(3155,"mΩ"),(3158,"mA"),(3160,"> 200"),(3174,"μF"),(3177,"mΩ"),(3241,"VOUT = 3.3 V"),
 (3150,"Inductor tolerance"),(3159,"Rated current (Imax)"),(3162,"Table 17: Recommended inductor specifications"),
 (13656,"Full configuration"),(13657,"Simple configuration"),(13658,"Minimal configuration"),(13662,"Not used"),(13668,"Not used"),
 (13536,"Supply for TWI and GPIOs"),(13752,"GPIO4"),(13824,"GPIO4"),(14276,"Net tie"),
 (14047,"0603"),(14051,"0603"),(14056,"0603"),(14060,"0603"),(14064,"0201"),(14383,"0201"),(14640,"0201"),
 (14655,"A PCB with a minimum of two layers, including a ground plane, is recommended for optimal performance."),
 (14368,"C5, C14"),(14381,"100 nF"),(14653,"performance or functionality."),
]
for n, s in ds: chk(DS, n, s)
for n, s in [(23,"C71 4.7 uF, part GRM155R60J475ME47D"),(24,"C6 2.2 uF, 10 V, at the VBAT balls"),(25,"three of 10 uF, 16 V, at balls C1, C2 and C7"),
             (25,"Add a third 10 uF"),(26,"VDD_MIC and VDD_SD are used as switches with small capacitors"),(26,"C9 to C12: two of 10 uF on each output"),
             (29,"Nordic lists 0603 for every capacitor")]:
    chk(REF, n, s)
for n, s in [(30,"with C4, C5, C1, C2"),(214,"C21 stays for U4"),(215,"C88, third 10 uF X5R 16 V on VSYS/PVDD"),
             (216,"Applied to both outputs: C86 on VDD_MIC at ball A4, C87 on VDD_SD at ball A5")]:
    chk(SCH, n, s)
chk(MKN, 286, "X5R 16 V"); chk(MKN, 288, "load switch mode outputs")
chk(LEAD, 24, "156 mohm max")
for n, s in [(68,"GND,C71,2,~,passive"),(71,"GND,C74,2,~,passive"),(72,"GND,C75,2,~,passive"),(73,"GND,C76,2,~,passive"),(74,"GND,C77,2,~,passive"),(85,"GND,C88,2,~,passive"),(316,"VDD_1V8,L71,2,~,passive"),(332,"VDD_3V0,L72,2,~,passive"),(328,"VDD_1V8,U2,E4,VDDIO,power_in"),(198,"NTC,J_BAND_B,3,NTC,passive"),(199,"NTC,RT1,1,~,passive"),(361,"VSET1,R71,1,~,passive"),(126,"GND,U2,A6,AVSS,power_in")]:
    chk(NET, n, s)
print("RESULT checks=%d fails=%d" % (count, fails))
