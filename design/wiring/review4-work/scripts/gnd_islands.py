# For each flex board: are the two GND lands of the foot joined by the ribbon's own copper? (KiCad connectivity). Run with run_kipy.sh.
import pcbnew
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/band")
for f,ref,a,b in ((1,"J_BAND_A","6","8"),(2,"J_BAND_B","2","7")):
    for s in range(7,14):
        bd=pcbnew.LoadBoard("%s/flex%d-us%d.kicad_pcb"%(R,f,s)); bd.BuildConnectivity(); c=bd.GetConnectivity()
        pads={}
        for fp in bd.GetFootprints():
            for p in fp.Pads(): pads[(fp.GetReference(),p.GetNumber())]=p
        pa,pb=pads[(ref,a)],pads[(ref,b)]
        conn=[ (q.GetParentFootprint().GetReference(),q.GetNumber()) for q in c.GetConnectedPads(pa)]
        print("flex%d-us%d %s:%s connected pads %s ; %s:%s joined on ribbon: %s"%(f,s,ref,a,sorted(conn),ref,b,(ref,b) in conn))
