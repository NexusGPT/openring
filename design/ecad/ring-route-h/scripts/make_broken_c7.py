# make_broken_c7.py a2.kicad_pcb a1.kicad_pcb out.kicad_pcb : copy of A2 with C7 put back on the screen face (B.Cu) at its A1 place and rotation
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); a = pcbnew.LoadBoard(sys.argv[2])
m = b.FindFootprintByReference("C7"); ma = a.FindFootprintByReference("C7")
if m.GetLayer() != ma.GetLayer(): m.Flip(m.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
m.SetOrientation(ma.GetOrientation()); m.SetPosition(ma.GetPosition())
b.Save(sys.argv[3]); print("C7 now", b.GetLayerName(m.GetLayer()), m.GetPosition().x, m.GetPosition().y, m.GetOrientationDegrees(), "saved", sys.argv[3])
