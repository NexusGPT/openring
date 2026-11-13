import pcbnew
for f in ('flex1-us7', 'flex1-us13'):
    b = pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/band/%s.kicad_pcb") % f)
    for fp in b.GetFootprints():
        if fp.GetReference().startswith('SW'):
            print('SWCHECK %s %s footprint %s pads %s' % (f, fp.GetReference(), fp.GetFPID().GetLibItemName(), sorted(p.GetNumber() for p in fp.Pads())))
