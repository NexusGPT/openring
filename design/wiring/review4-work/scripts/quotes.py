# Prints the pinned lines this review cites (first 600 characters each).
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
cites=[("design/mfg/assembly/assembly.md",[3,70,73,96,97,100,103,116,124,136,141,150,154,159,163,170,201,202,203,205,210,218,221,222,262,334,384]),
("design/mfg/assembly/hotbar-joint.md",[184]),
("design/ecad/case/pcb/board-notes.md",[315,318,323,324]),
("design/mfg/assembly/process.md",[67,90,152,153,154,155,175,177]),
("design/ecad/band/band-interface.md",[97,117,122,137]),
("design/ecad/ring/netlist.csv",[381,386,387]),
("design/bom.csv",[48,64,74,77]),
("design/wiring/lead-decisions.md",[65,71,81,83]),
("design/mfg/parts/body/body-us9.dims.csv",[8])]
for f,ls in cites:
    L=open(R+f,encoding="utf-8").read().split("\n")
    for n in ls: print("%s:%d: %s"%(f,n,L[n-1][:600]))
