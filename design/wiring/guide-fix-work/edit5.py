P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s=open(P,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70])
    s=s.replace(old,new)
# step 16
rep("on the board's under face, by hot-bar soldering [PROPOSED: reason, a thin ribbon on a row of lands is joined in one press, and the lands got no paste in step 2]. The board with its screen is held above the open block, under face up,",
    "on the board's parts face, by hot-bar soldering [PROPOSED: reason, a thin ribbon on a row of lands is joined in one press, and the lands got no paste in step 2]. The board with its screen is held above the open block, parts face up (the screen, plugged into J1 on the screen face, hangs below the board),")
rep("one fold of the ribbon (`design/mech/thin/thin-notes.md:134`).\n- **Locate:** the land rows","one fold of the ribbon (`design/mech/thin/thin-notes.md:134`).\n- **Locate:** the land rows")
# step 17
rep("- **After:** the board's under face, its test pads and the ribbon joints are closed for good.","- **After:** the parts face with its ribbon joints, and the screen face with its test pads and J1, are closed for good.")
rep("board 0.30, foam 0.10, screen 0.80 (`design/architecture.md:426`).","board 0.30, foam 0.10, screen 0.80 (`design/architecture.md:426`); that stack is the 3.20 mm block. With the cable between board and panel the space between them is 1.07 mm and not 0.10 mm (`design/wiring/screen-cable-study.md:243`; confirmed by the inside model of the taller block).")
# step 27
rep("SHPHLD is on TP19 (`design/ecad/ring/sch-notes.md:44`), under the board.","SHPHLD is on TP19 (`design/ecad/ring/netlist.csv:253`), on the screen face under the panel.")
open(P,'w',encoding='utf-8').write(s)
