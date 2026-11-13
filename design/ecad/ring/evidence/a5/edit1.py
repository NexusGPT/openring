import re
p=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)

# storage symbol
rep(s[s.index("# Zetta SD NAND LGA-8"):s.index("# SGM38046 balls")],
'''# CS Semiconductor CSNP32GCR01-BOW, LGA-8: pad numbers and names from the maker spec V1.0 p5 table 2.1
# (design/datasheets/slim2_cs-sdnand-20230403.pdf): 1 SDD2, 2 SDD3 (SPI CS), 3 SCLK, 4 VSS, 5 CMD (SPI DI),
# 6 SDD0 (SPI DO), 7 SDD1, 8 VCC. Names kept as the SD names of wiring decision W3.
SYM['CSNP32GCR01_BOW'] = [('1', 'DAT2', 'bidirectional'), ('2', 'DAT3', 'bidirectional'), ('3', 'CLK', 'input'),
                          ('4', 'VSS', 'power_in'), ('5', 'CMD', 'bidirectional'), ('6', 'DAT0', 'bidirectional'),
                          ('7', 'DAT1', 'bidirectional'), ('8', 'VCC', 'power_in')]

''')
# mic symbol
rep(s[s.index("# IM73D122V01"):s.index("# Screen TOH095XVT-01")],
'''# IM68D128B: pin names Clock, VDD, Ground, Data, Select from the Infineon brief of the same 3.5 x 2.65 x 0.98
# package (slim.md section 5.1, IM68D121J brief p1); pin numbers not in any document here: provisional P1..P5
SYM['IM68D128B'] = [('P1', 'CLOCK', 'input'), ('P2', 'VDD', 'power_in'), ('P3', 'GND', 'power_in'),
                    ('P4', 'DATA', 'output'), ('P5', 'SELECT', 'input')]

''')
# screen names as printed in slim.md 1.3
rep("# Screen TOH095XVT-01, 15 contacts: datasheet p5 drawing (parts/ui-pass2.md section 1)",
    "# Screen TOH095XVT-01, 15 contacts, names in the order printed in the table of parts/slim.md section 1.3\n# (maker p6; the table prints pin 4 twice and no pin 3: position k here = k-th entry as printed)")
rep("('VCC', 'power_in'),\n             ('IOVCC'","('VCI', 'power_in'),\n             ('IOVCC'")
rep("('TE', 'output'), ('RESET', 'input')","('TE', 'output'), ('RESX', 'input')")
# switches
rep(s[s.index("# SKRHADE010: Alps"):s.index("# DMN2450UFB4")],
'''# Alps SKTAAAE010: 1 pole 1 throw tact switch (maker spec KTA-601 p1); the spec shows no terminal numbers
# (drawing not in the copy): two terminals P1, P2, provisional
SYM['SKTAAAE010'] = [('P1', '~', 'passive'), ('P2', '~', 'passive')]
''')
rep("SYM['WIRE'] = [('1', '1', 'passive')]\nSYM['SOLDER_PADS_6'] = [(str(i), 'W%d' % i, 'passive') for i in range(1, 7)]\n",
'''# band-side connection groups on the main board (A5 section 17.3: two flex tails); pad numbers are this
# schematic's own definition of the pad order, not a maker pin
BAND_A = ['JOY_UP', 'JOY_DOWN', 'JOY_LEFT', 'JOY_RIGHT', 'BTN_REC', 'GND']
BAND_A_NAMES = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'REC', 'GND']
BAND_B = ['MOTOR_DRV', 'VDD_3V0', 'VBAT', 'GND', 'NTC', 'VBUS', 'USB_DN', 'USB_DP', 'GND']
BAND_B_NAMES = ['MOT-', 'MOT+', 'CELL+', 'CELL-', 'NTC', 'VBUS', 'D-', 'D+', 'GND']
SYM['BAND_PADS_A'] = [(str(i + 1), n, 'passive') for i, n in enumerate(BAND_A_NAMES)]
SYM['BAND_PADS_B'] = [(str(i + 1), n, 'passive') for i, n in enumerate(BAND_B_NAMES)]
''')
rep("M = 'main'; P = 'power'; A = 'mics'; S = 'storage'; D = 'screen'; K = 'controls'; T = 'contacts'",
    "M = 'main'; P = 'power'; A = 'mics'; S = 'storage'; D = 'screen'; K = 'controls'; T = 'contacts'; BD = 'band'")
# cell and RT1 to band sheet
rep("two('RT1', 'NTC', '10k NTC', 'OPEN 12.2', 'ring:R_0402', P, 'NTC', 'GND')",
    "two('RT1', 'NTC', '10k NTC', 'OPEN 12.2', 'ring:R_0402', BD, 'NTC', 'GND')  # in the band at the cell (A5 17.3)")
rep("'ring:CELL_TABS', P,","'ring:CELL_TABS', BD,")
# mics
rep(s[s.index("# ---- microphones (W4)"):s.index("# ---- storage (W3)")],
'''# ---- microphones (W4, A5 16.4 and 16.6: two microphones, one stereo input on the A pins)
mics = [('U5', 'MIC_A_CLK', 'MIC1_DATA', 'MIC_A_DATA', 'GND', 'R31', 'C31', 'C35'),
        ('U6', 'MIC_A_CLK', 'MIC2_DATA', 'MIC_A_DATA', 'VDD_MIC', 'R32', 'C32', 'C36')]
for u, clk, dl, bus, lr, r, c1, c2 in mics:
    part(u, 'IM68D128B', 'IM68D128B', 'IM68D128B', 'ring:Infineon_IM68D128B_3.5x2.65', A,
         {'DATA': dl, 'VDD': 'VDD_MIC', 'CLOCK': clk, 'SELECT': lr, 'GND': 'GND'})
    two(r, 'R', '100R', '', 'ring:R_0201', A, dl, bus)
    two(c1, 'C', '1uF', '', 'ring:C_0201', A, 'VDD_MIC', 'GND')
    two(c2, 'C', '100nF', '', 'ring:C_0201', A, 'VDD_MIC', 'GND')

''')
# storage
rep("""part('U3', 'ZDSD64GLGEAG', 'ZDSD64GLGEAG-R', 'ZDSD64GLGEAG-R', 'ring:LGA-8_6.2x8', S,""",
    """part('U3', 'CSNP32GCR01_BOW', 'CSNP32GCR01-BOW', 'CSNP32GCR01-BOW', 'ring:LGA-8_6.2x8', S,""")
open(p,'w').write(s)
