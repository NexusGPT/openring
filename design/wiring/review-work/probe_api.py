# Probe which connectivity calls KiCad 10's Python offers (prints signatures and a trial result)
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
b.BuildConnectivity()
c = b.GetConnectivity()
for n in dir(c):
    if 'Connect' in n or 'Cluster' in n or 'Island' in n:
        print('method', n)
p = list(b.GetPads())[0]
print('pad', p.GetParentFootprint().GetReference(), p.GetNumber(), p.GetNetname())
for args in ([pcbnew.PCB_PAD_T, pcbnew.PCB_TRACE_T, pcbnew.PCB_VIA_T, pcbnew.PCB_ARC_T, pcbnew.PCB_ZONE_T],):
    try:
        r = c.GetConnectedItems(p, args)
        print('GetConnectedItems(list)', len(r), [x.GetClass() for x in r][:10])
    except Exception as e:
        print('GetConnectedItems err', e)
try:
    r = c.GetConnectedItems(p)
    print('GetConnectedItems(p)', len(r))
except Exception as e:
    print('GetConnectedItems(p) err', str(e)[:300])
try:
    r = c.GetConnectedPads(p)
    print('GetConnectedPads', type(r), len(r))
except Exception as e:
    print('GetConnectedPads err', str(e)[:300])
