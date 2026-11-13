import pcbnew
b = pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pcb/ring.kicad_pcb"))
b.BuildConnectivity()
c = b.GetConnectivity()
print([m for m in dir(c) if not m.startswith('_')])
pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
for ref, num in (("J1","10"),("ANT1","4"),("J_BAND_A","5"),("U1","A1")):
    ps = [x for x in pads if x.GetParentFootprint().GetReference()==ref and x.GetNumber()==num]
    if not ps: continue
    p=ps[0]
    try:
        items = c.GetConnectedItems(p)
        print(ref,num,'items',len(items), sorted(set(type(i).__name__ for i in items)))
    except Exception as e:
        print('err', e)
    try:
        print(ref,num,'netitems', len(c.GetNetItems(p.GetNetCode(), [pcbnew.PCB_PAD_T])))
    except Exception as e:
        print('err2', e)
