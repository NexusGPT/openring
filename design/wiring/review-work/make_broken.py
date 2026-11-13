# Honest-control copy: removes the track segments of one net nearest to one pad (so the path breaks)
# and writes the copy to the review work folder. Usage: run_kipy.sh make_broken.py <board> <net> <out>
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
net = sys.argv[2]
gone = 0
for t in list(b.GetTracks()):
    if t.GetNetname() == net and t.GetClass() in ('PCB_TRACK', 'PCB_ARC'):
        b.Remove(t)
        gone += 1
pcbnew.SaveBoard(sys.argv[3], b)
print('removed tracks of', net, gone)
