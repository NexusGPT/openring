import sys
P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s=open(P,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:60])
    s=s.replace(old,new)
rep("| Screen `screen`, `screen_tail` | DISP1 | 0.95 inch AMOLED with a folded tail into J1 | `design/mech/thin/placement.csv:24`, `design/mech/thin/placement.csv:25` | 15 |",
"| Screen `screen`, `screen_tail` | DISP1 | 0.95 inch AMOLED with its own stock cable (15 contacts). The screen is turned 180 degrees; the cable is bent back under the panel at the fingertip end and plugged into J1 on the board's screen face, J1's opening toward the fingertip, contacts up, contact 1 on the +Y side | `design/mech/thin/placement.csv:24`, `design/mech/thin/placement.csv:25`, `design/wiring/screen-cable-study.md:166` | 15 |")
rep("| Foam frame `foam` | FOAM1 | 0.10 mm foam frame, 1.2 mm wide, closed all round (v7); Nitto SCF AN010, no adhesive, held by the screen's pressure (can change with the screen cable study) | `design/mech/thin/placement.csv:23`, `design/bom.csv:57` | 15 |",
"| Foam `foam` | FOAM1 | Nitto SCF AN010, 0.10 mm, no adhesive. It is NOT fitted as a closed frame any more: the screen cable passes the whole width at the fingertip end, so the panel hangs from the glass through ADH1. Any spacer must leave X -4.8 to +14.2 open across Y +-6.4. Whether a spacer stays, and in what shape, is not decided | `design/wiring/screen-cable-study.md:207`, `design/mech/thin/placement.csv:23`, `design/bom.csv:57` | 15 |")
rep("27.2 x 12.6 x 0.3 mm, 4 copper layers with laser microvias, parts on the under face only | `design/mech/thin/placement.csv:22`, `design/mfg/specs/main-board.md:6` | 1 |",
"27.2 x 12.6 x 0.3 mm, 4 copper layers with laser microvias, parts on both faces: 72 parts and the ribbon lands on the parts face, J1, 8 small parts and the 12 test pads on the screen face | `design/mech/thin/placement.csv:22`, `design/ecad/ring/pcb/board-notes-r3.md:35`, `design/ecad/ring/pcb/board-notes-r3.md:47` | 1 |")
rep("| Board parts | all refs of step 2 | chips, passives, microphones, connector, antenna, test pads | `design/bom.csv` | 2 |",
"| Board parts | all refs of step 2 | chips, passives, microphones, connector J1, antenna, test pads; on both faces, soldered in two passes | `design/bom.csv`, `design/ecad/ring/pcb/fab/ring-pos-front.csv:1`, `design/ecad/ring/pcb/fab/ring-pos-back.csv:1` | 2 |")
rep("under the board beside the +Y floor slot |","on the parts face beside the +Y floor slot |")
open(P,'w',encoding='utf-8').write(s)
