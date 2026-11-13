P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s=open(P,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70])
    s=s.replace(old,new)
rep(" parts face up (the screen, plugged into J1 on the screen face, hangs below the board),"," parts face up,")
rep("The test pads are on the populated under face (`design/ecad/ring/pcb/board-notes.md:53`; footprint `design/ecad/ring/pcb/build_board.py:253`), which faces the block floor 0.05 mm away (`design/architecture.md:426`). After bonded glass",
    "The 12 test pads are on the screen face (`design/ecad/ring/pcb/placement-final.csv:87` to `design/ecad/ring/pcb/placement-final.csv:98`), which faces the screen. From step 15 the screen's cable lies over them (`design/wiring/screen-cable-study.md:205`). After bonded glass")
rep("reserve a free area beside each slot on the under face for one fold","reserve a free area beside each slot on the parts face for one fold")
rep("| Foam FOAM1: fixed, Nitto SCF AN010, 0.10 mm, no adhesive (outline closed all round) | 15 | fixed (item 96, rest; `design/bom.csv:57`) | new |",
    "| Foam FOAM1: material fixed, Nitto SCF AN010, 0.10 mm, no adhesive; NOT a closed frame any more (the screen cable passes at the fingertip end); whether a spacer stays and its shape are open | 15 | material fixed (item 96, rest; `design/bom.csv:57`); the shape: the lead (`design/wiring/screen-cable-study.md:207`) | new |")
open(P,'w',encoding='utf-8').write(s)
