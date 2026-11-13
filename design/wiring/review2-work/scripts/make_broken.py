# copy of flex1-us9 with every track of net JOY_UP removed (control for the rules check)
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); n=0
for t in list(b.GetTracks()):
    if t.GetNetname()=='JOY_UP': b.Remove(t); n+=1
b.Save(sys.argv[2]); print('removed',n)
