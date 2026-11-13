P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s=open(P,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70])
    s=s.replace(old,new)
rep("(1) The screen is turned 180 degrees from the way the old text of this file laid it: the ledge","(1) The screen is turned 180 degrees: the ledge")
rep(" (`design/mech/thin/placement.csv:25`, `design/mech/thin/placement.csv:18`).\n- **Locate:** J1 by"," \n- **Locate:** J1 by".replace(" \n","\n"))
rep("- **Join:** DISP1 (`screen`) with its own cable (`screen_tail`) to the board's SCREEN FACE, in this order","- **Join:** DISP1 (`screen`) with its own cable (`screen_tail`, `design/mech/thin/placement.csv:25`, `design/mech/thin/placement.csv:18`) to the board's SCREEN FACE, in this order")
rep("(c) No short between neighbouring contacts: the only neighbouring contacts with a pad each are none (contact 5 is next to 4 and 6, which have no pad), so this too is proven by T-SCREEN at step 18 and by the ohmmeter reading of (b).","(c) A short between neighbouring contacts cannot be measured at a test pad, because no two neighbouring contacts both have one. T-SCREEN at step 18 shows it.")
open(P,'w',encoding='utf-8').write(s)
