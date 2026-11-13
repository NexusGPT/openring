P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s = open(P).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)

i0 = s.index("        'nPM1300_CAAA': (")
i1 = s.index("        'IM68D128B': (")
s = s[:i0] + """        'nPM1304_CSP35': ('A6, architecture 17.13: the nPM1304 ball map against the nPM1300 is not confirmed (Nordic states no pin or footprint compatibility, parts/research-npm1304.md section 2); the pin names are the nPM1300 names of the DK schematic PCA10184 v0.5.4 p6 (QFN nPM1300-QEAA) and are assumed for the nPM1304; P1..P33 are placeholders, not balls (the CSP has 35 balls, 33 names are drawn, so 2 or more assignments are unknown)', 'Nordic nPM1304 product specification, ball assignment table (open item S18)'),
""" + s[i1:]
rep("""        'MOTOR': ('Vybronics""", """        'BAND_PADS_A': ('pad numbers are this schematic\\'s own order (BAND_SPLIT at the top of make_netlist.py), not a maker pin; the split of signals between the two tails is confirmed by the lead after the inside model (A6, sch-notes)', 'flex tail drawing from the flex maker and the inside model (open items S16 and the lead\\'s confirmation)'),
        'BAND_PADS_B': ('as BAND_PADS_A', 'as BAND_PADS_A'),
        'MOTOR': ('Vybronics""")
rep("""            if 'OPEN' in p['value'] or 'OPEN' in p['mpn']:""",
"""            if p['reference'] in OPEN_ORDER_CODE:
                w.writerow([p['reference'], '', 'order code', OPEN_ORDER_CODE[p['reference']], 'Nordic (open item S18)'])
            if 'OPEN' in p['value'] or 'OPEN' in p['mpn']:""")
rep("TESTPAD_REFS = ", """# parts whose order code is empty on purpose (never invented): reference -> why
OPEN_ORDER_CODE = {'U2': 'S18: Nordic. The nPM1304 orderable part number is not read from a Nordic page by this task: the order code is left empty (architecture 17.9 S18, 17.13)'}
TESTPAD_REFS = """)
open(P, 'w').write(s)
print('ok')
