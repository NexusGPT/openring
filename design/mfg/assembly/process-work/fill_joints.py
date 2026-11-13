"""Fill design/mfg/assembly/joints.csv from process.md. Reads WORK/joints-before.csv (the table as found), writes the
delivered joints.csv and WORK/logs/fill.log (one line per changed field)."""
import csv, os, re
W = os.path.dirname(os.path.abspath(__file__))
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
OUT = ROOT + '/design/mfg/assembly/joints.csv'
rows = list(csv.DictReader(open(W + '/joints-before.csv', newline='')))
fields = list(rows[0].keys())

PROFILE = ("P3 profile: to 150 C at less than 2.5 C/s, 150 to 200 C in 90 to 110 s, 60 to 75 s above 217 C, at most 35 s "
           "above 230 C, peak 240 C (accepted 235 to 245 C on a thermocouple at the board surface), cool at 6 C/s or slower")
PASTE = "Kester NP505-HR SAC305 Type 4 (20 to 38 um), 88.5 % metal, no-clean, part 7040211410"
PFLUX = "the ROL0 no-clean flux of the NP505-HR paste; no added liquid flux; residue left, never washed or brushed (process.md P1.2, P1.5)"
WFLUX = "the ROL0 no-clean core of the Kester 275 wire; residue left (process.md P1.3, P1.5)"
W025 = "Kester 275 SAC305 no-clean cored wire 0.25 mm, 2.2 % flux, part 2470687623 (process.md P1.3, P4)"
W04 = "Kester 275 SAC305 no-clean cored wire 0.4 mm, 2.2 % flux, part 2470687608, also for tinning the stripped ends at case step 1 (process.md P1.3, P4)"
W05 = "Kester 275 SAC305 no-clean cored wire 0.5 mm, 2.2 % flux, part 2470687603 (process.md P1.3, P4)"
C13 = "check probe point: the land numbers of the ribbon's board end are on no flex drawing (process.md P8 change C13)"
C4 = "alignment: the boards have no fiducial (process.md P7, P8 change C4)"

log = []
def setf(r, f, v):
    if r[f] != v:
        log.append("%s | %s | %r -> %r" % (r['joint_id'], f, r[f][:80], v[:120]))
        r[f] = v
def addsrc(r, secs):
    setf(r, 'source', r['source'] + "; process: design/mfg/assembly/process.md " + secs)

for r in rows:
    j, st = r['joint_id'], r['step']
    if st == '16':  # hot bar, group 1: alloy and flux only
        setf(r, 'solder_source', "alloy SAC305 (process.md P1.1); form (paste, preform or tinned land): MISSING, see hotbar-joint.md")
        setf(r, 'flux', "Kester 959T no-clean liquid flux, ORL0, flash point 18 C: dry before heat (process.md P1.4)")
        parts = [p.strip() for p in r['gap'].split(' ; ') if p.strip() and not p.strip().startswith('flux:')]
        setf(r, 'gap', "waits for hotbar-joint.md (process.md P8 change C17): " + " ; ".join(parts))
        addsrc(r, "P1.1, P1.4")
    elif st == '6':  # switches
        setf(r, 'solder_source', PASTE + ", printed through a 0.08 mm stainless stencil cut from the FLEX1 paste layer: paste layer MISSING (process.md P8 change C1)")
        setf(r, 'flux', PFLUX + "; Alps forbids flux on the switch face")
        setf(r, 'tool', "0.08 mm stainless laser-cut stencil, reflow oven with a thermocouple logger, the head on a flat carrier (process.md P2, P6)")
        setf(r, 'heat', PROFILE + "; 1 reflow (Alps: 260 C 3 s, 40 s above 230 C, at most 2 reflows) (process.md P3)")
        g = ["solder: the FLEX1 boards have no paste layer (process.md P8 change C1)"]
        if j.startswith('J-'):
            g.append(C13)
        setf(r, 'gap', " ; ".join(g))
        addsrc(r, "P1.2, P1.5, P2, P3, P6")
    elif st == '7':  # motor leads
        setf(r, 'solder_source', W025 + "; the same wire tins the stripped lead end")
        setf(r, 'flux', WFLUX)
        setf(r, 'tool', "50 W temperature-controlled soldering iron, chisel tip 0.8 mm wide or narrower (process.md P4, P6)")
        setf(r, 'gap', C13)
        addsrc(r, "P1.3, P1.5, P4, P6")
    elif st == '9':  # ring cell tabs
        setf(r, 'solder_source', W025 + "; the land is not pre-tinned, the wire brings the solder")
        setf(r, 'flux', WFLUX)
        setf(r, 'tool', "50 W temperature-controlled soldering iron, chisel or conical tip 0.45 mm wide or narrower (process.md P4, P6)")
        setf(r, 'gap', C13)
        addsrc(r, "P1.3, P1.5, P4, P6")
    elif st == '8':  # discs
        setf(r, 'solder_source', PASTE + ", printed through a 0.08 mm stainless stencil, four 0.58 mm round openings per land: paste layer MISSING (process.md P8 change C2)")
        setf(r, 'flux', PFLUX)
        setf(r, 'tool', "0.08 mm stainless stencil, hot plate with a thermocouple taped on the ribbon beside a disc, tweezers, 10 times magnifier (process.md P5, P6)")
        setf(r, 'heat', "hot plate on the " + PROFILE + "; ribbon slid off onto a metal block to cool (process.md P5)")
        if j.startswith('J-'):
            c = r['check'].replace("; disc flush with the liner's inner face [needs step 21]",
                "; disc top 0.070 to 0.112 mm above the land copper (process.md P5); flush with the liner is checked at step 21, not here (process.md P8 change C11)")
            setf(r, 'check', c)
            setf(r, 'gap', "solder: the FLEX2 boards have no paste layer (process.md P8 change C2) ; " + C13)
        else:
            setf(r, 'gap', "solder: the FLEX2 boards have no paste layer (process.md P8 change C2)")
        addsrc(r, "P1.2, P1.5, P2, P5, P6")
    elif st == '15':  # J1 contacts
        setf(r, 'tool', "no tool: fingertip on the middle of J1's lever (Hirose: no sharp tool such as tweezers); the cable held by its stiffened end and pushed in flat to the very end; 10 times magnifier (process.md P6)")
        setf(r, 'check', r['check'] + "; continuity of every contact proven by T-SCREEN and T-SIGN at the end of step 16, ring on its cell and USB from the jig through CP1 to CP4, screen folded down, before step 17 closes J1 [needs step 16] (process.md P8 change C12)")
        setf(r, 'check_possible_at_this_step', "no, 16")
        setf(r, 'gap', "")
        addsrc(r, "P6, P8 C12")
    elif j in ('J-W054-B', 'J-W055-B', 'J-W056-B', 'J-W057-B', 'P-case_pins'):
        setf(r, 'solder_source', PASTE + ", printed on the four pin pads of PCB2 through a 0.10 mm stencil (pin in paste): paste openings MISSING (process.md P8 change C6)")
        setf(r, 'flux', PFLUX)
        setf(r, 'tool', "0.10 mm stainless stencil, reflow oven with a thermocouple logger, PCB2 on a carrier with holes for the pin tails (process.md P4, P6)")
        setf(r, 'heat', PROFILE + "; pin limit 260 C for 10 s (Harwin product page) (process.md P3, P4)")
        setf(r, 'gap', "solder: PCB2 has no paste opening at the pin pads (process.md P8 change C6)")
        addsrc(r, "P1.2, P1.5, P3, P4, P6")
    elif st in ('case 6', 'case 7'):  # 30 AWG wires
        setf(r, 'solder_source', W04)
        setf(r, 'flux', WFLUX)
        setf(r, 'tool', "50 W temperature-controlled soldering iron, chisel tip 0.9 mm wide or narrower (process.md P4, P6)")
        setf(r, 'heat', "tip 340 C, at most 7 s per joint (process.md P4; a choice for the lead to confirm)")
        if j == 'J-W063-B':
            setf(r, 'check', r['check'].replace(" [needs case 8]", "; on W1 wait for a steady reading, C15 on VRING charges first (process.md P8 change C15) [needs case 8]"))
        setf(r, 'gap', "")
        addsrc(r, "P1.3, P1.5, P4, P6")
    elif j in ('J-W059-B', 'J-W060-B'):
        setf(r, 'solder_source', W05)
        setf(r, 'flux', WFLUX)
        setf(r, 'tool', "50 W temperature-controlled soldering iron, chisel tip 1.3 mm wide or narrower (process.md P4, P6)")
        setf(r, 'heat', "tip 340 C, at most 7 s per joint (process.md P4; the cell maker gives no limit; a choice for the lead to confirm)")
        setf(r, 'check', "red probe on pad W5, black probe on pad W6: +3.0 to 4.35 V, the same reading as before cutting (process.md P8 change C16)")
        setf(r, 'gap', "")
        addsrc(r, "P1.3, P1.5, P4, P6, P8 C16")
    elif j in ('J-W061-B', 'J-W062-B'):
        setf(r, 'solder_source', W05)
        setf(r, 'flux', WFLUX)
        setf(r, 'tool', "50 W soldering iron, chisel tip 1.3 mm wide or narrower (process.md P4, P6)")
        setf(r, 'gap', "")
        addsrc(r, "P1.3, P1.5, P4, P6")
    elif j in ('J-W036-A', 'J-W037-A', 'J-W038-A', 'J-W039-A'):
        setf(r, 'flux', PFLUX)
        setf(r, 'tool', "0.075 mm stainless laser-cut stencil, reflow oven with a thermocouple logger (pass 2) (process.md P2, P6)")
        setf(r, 'heat', PROFILE + "; pass 2, 1 reflow for this part (process.md P3)")
        setf(r, 'gap', C4 + " ; check: no saved document gives the accept rule of a reflowed joint (process.md P8 change C14)")
        addsrc(r, "P1.2, P1.5, P2, P3, P6")
    elif j == 'P-ring-F':
        setf(r, 'flux', PFLUX)
        setf(r, 'tool', "0.075 mm stainless laser-cut, electro-polished stencil, reflow oven with a thermocouple logger (pass 2) (process.md P2, P6)")
        setf(r, 'heat', PROFILE + "; pass 2 (process.md P3)")
        setf(r, 'gap', C4)
        addsrc(r, "P1.2, P1.5, P2, P3, P6")
    elif j == 'P-ring-B':
        setf(r, 'flux', PFLUX)
        setf(r, 'tool', "0.10 mm stainless laser-cut, electro-polished stencil, reflow oven with a thermocouple logger (pass 1) (process.md P2, P6)")
        setf(r, 'heat', PROFILE + "; this face sees pass 1 and pass 2: J1 at its limit of 2 reflows, so never a third reflow (process.md P3)")
        setf(r, 'gap', C4 + " ; solder: the J1 openings are 1:1 and the 12 test pads have openings; P2 asks Hirose's reduced J1 openings and none on the test pads (process.md P8 change C3)")
        addsrc(r, "P1.2, P1.5, P2, P3, P6")
    elif j == 'P-case_main':
        u2 = " ".join("U2:%d" % i for i in range(1, 25))
        setf(r, 'solder_source', r['solder_source'] + ",U2 ; paste layer design/ecad/case/pcb/fab/case_main/gerber/case_main-F_Paste.gbr for " + u2 +
             " ; U2 pad 25 (thermal pad): four 1.1 x 1.1 mm windows off the land centre, TI's example stencil (process.md P2; process-work/logs/case_noland.log) ; " + PASTE)
        setf(r, 'flux', PFLUX)
        setf(r, 'tool', "0.10 mm stainless laser-cut stencil, reflow oven with a thermocouple logger; after the reflow a 50 W iron for the USB socket J1's shell slots (process.md P2, P6, P8 change C5)")
        setf(r, 'heat', PROFILE + "; one reflow only (radio module U1: single reflow); J1 shell slots by iron, Kester 275 0.5 mm, tip 340 C, at most 7 s (process.md P3, P4)")
        setf(r, 'check', "every joint at 10 times under the magnifier; no bridge on U2, U6 and J1; the four J1 shell slots filled (process.md P8 change C5)")
        setf(r, 'check_possible_at_this_step', "yes")
        setf(r, 'gap', "step: no case step builds this board yet; process.md proposes a new case step 0 (process.md P8 change C5) ; " + C4)
        addsrc(r, "P1.2, P1.5, P2, P3, P4, P6, P8 C5")
with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
open(W + '/logs/fill.log', 'w').write("\n".join(log) + "\nFILL changed fields %d rows %d\n" % (len(log), len(rows)))
print("FILL changed fields %d rows %d" % (len(log), len(rows)))
