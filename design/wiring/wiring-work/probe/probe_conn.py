import pcbnew, collections
b = pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pcb/ring.kicad_pcb"))
b.BuildConnectivity()
c = b.GetConnectivity()
pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
bynet = collections.defaultdict(list)
for p in pads:
    if p.GetNetname(): bynet[p.GetNetname()].append(p)
for net in ("GND", "LCD_SCK", "VBAT", "RF_FEED"):
    lst = bynet[net]
    sizes = collections.Counter()
    for p in lst:
        cp = c.GetConnectedPads(p)
        sizes[len(cp)] += 1
    print(net, len(lst), dict(sizes))
for ref, num in (("J1","10"),("ANT1","4"),("J_BAND_A","5")):
    p = [x for x in pads if x.GetParentFootprint().GetReference()==ref and x.GetNumber()==num][0]
    print(ref, num, len(c.GetConnectedPads(p)), len(bynet[p.GetNetname()]))
