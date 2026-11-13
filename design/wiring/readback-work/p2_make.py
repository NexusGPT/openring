"""p2_make.py <mode> <out.kicad_pcb>: writes a broken copy of the copy of ring.kicad_pcb (run with run_kipy.sh).
modes: resave (no edit), cut (one LCD_SCK segment removed), join (LCD_SCK joined to LCD_MOSI by one added segment)."""
import sys, math, pcbnew
mode, out = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/readback-work/p2/ring_orig_copy.kicad_pcb"))
mm = pcbnew.ToMM
def unconn():
    b.BuildConnectivity()
    return b.GetConnectivity().GetUnconnectedCount(False)
base = unconn()
print('MAKE mode=%s baseline unconnected count=%d' % (mode, base))
if mode == 'cut':
    segs = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'LCD_SCK']
    segs.sort(key=lambda t: -t.GetLength())
    for t in segs:
        info = (mm(t.GetLength()), b.GetLayerName(t.GetLayer()), mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), t.m_Uuid.AsString())
        b.Remove(t)
        n = unconn()
        print('MAKE try remove segment len=%.3f layer=%s start=(%.3f,%.3f) end=(%.3f,%.3f) uuid=%s -> unconnected %d' % (info + (n,)))
        if n == base + 1:
            print('MAKE chosen segment (rule: unconnected count +1): %s' % (info,))
            break
        b.Add(t)           # put it back and try the next one
    else:
        raise SystemExit('MAKE no segment raised the count by one')
elif mode == 'join':
    A = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'LCD_SCK']
    B = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'LCD_MOSI']
    best = None
    for a in A:
        for c in B:
            if a.GetLayer() != c.GetLayer():
                continue
            for pa in (a.GetStart(), a.GetEnd()):
                for pc in (c.GetStart(), c.GetEnd()):
                    d = math.hypot(pa.x - pc.x, pa.y - pc.y)
                    if best is None or d < best[0]:
                        best = (d, a, pa, pc)
    d, a, pa, pc = best
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pa); t.SetEnd(pc); t.SetWidth(pcbnew.FromMM(0.1)); t.SetLayer(a.GetLayer()); t.SetNet(a.GetNet())
    b.Add(t)
    print('MAKE joined LCD_SCK to LCD_MOSI on %s from (%.3f,%.3f) to (%.3f,%.3f), length %.3f mm, width 0.100' % (b.GetLayerName(a.GetLayer()), mm(pa.x), mm(pa.y), mm(pc.x), mm(pc.y), mm(d)))
    print('MAKE after join unconnected count=%d' % unconn())
pcbnew.SaveBoard(out, b)
print('MAKE saved', out)
