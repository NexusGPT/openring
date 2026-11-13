import pcbnew, sys
RING=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/OpenRing.pretty")
BAND=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/band/OpenRingBand.pretty")
import csv
fp={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/parts.csv"))):
    fp[r["reference"]]=r["footprint"]
# positions: band-interface.md section 2 (group middle X -2.250, Y +-4.325); fixed parts from ring-board-plan.md f.1 (placement.csv)
pos={"J_BAND_A":(-2.250,-4.325),"J_BAND_B":(-2.250,4.325),"U3":(-5.0,0.0),"U11":(0.0,4.2),"C83":(0.0,5.45)}
board=pcbnew.BOARD()
boxes={}
for ref,(x,y) in pos.items():
    lib,name=fp[ref].split(":")
    m=pcbnew.FootprintLoad(BAND if lib=="OpenRingBand" else RING,name)
    m.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
    board.Add(m)
    m.BuildCourtyardCaches()
    c=m.GetCourtyard(pcbnew.F_CrtYd)
    b=c.BBox()
    boxes[ref]=(pcbnew.ToMM(b.GetLeft()),pcbnew.ToMM(b.GetTop()),pcbnew.ToMM(b.GetRight()),pcbnew.ToMM(b.GetBottom()))
    print(ref,name,"courtyard x %.3f..%.3f y %.3f..%.3f"%(boxes[ref][0],boxes[ref][2],boxes[ref][1],boxes[ref][3]))
bad=0
refs=list(boxes)
for i in range(len(refs)):
    for j in range(i+1,len(refs)):
        a,b=boxes[refs[i]],boxes[refs[j]]
        ox=min(a[2],b[2])-max(a[0],b[0]); oy=min(a[3],b[3])-max(a[1],b[1])
        if ox>1e-6 and oy>1e-6:
            bad+=1; print("OVERLAP",refs[i],refs[j],"%.3f x %.3f"%(ox,oy))
        else:
            print("clear  ",refs[i],refs[j],"gap %.3f"%max(-ox,-oy))
print("RESULT","PASS" if bad==0 else "FAIL","overlaps",bad)
sys.exit(1 if bad else 0)
