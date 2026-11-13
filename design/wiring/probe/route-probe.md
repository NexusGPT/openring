# Route probe: can Freerouting complete the ring board?

Pre-registration, written 2026-11-12 23:30:33 CET before any router run. No git is run (brief rule), so the time stamp comes from the date command.

## Hypothesis
An automatic router (Freerouting) can complete all connections of the placed ring circuit board under the board's own design rules.

## Pass line (copied from the brief)
On a routed COPY of the board, KiCad's rules check (kicad-cli pcb drc --severity-all --all-track-errors) reports 0 unconnected items and 0 violations. Anything else is "hypothesis not confirmed", reported with the counts.

## Falsifier
Any routed result with 1 or more unconnected items or 1 or more violations in every run that is made (max 4 runs). Pass needs at least one run that meets the pass line.

## Spend cap
75 minutes, at most 4 router runs, 20 minutes per run. No money is spent. Stop as blocked if a tool cannot be made to work in 30 minutes.

## Scope notes
- Board version: ring.kicad_pcb as on disk (10 Nov), 100 footprints, 6 copper layers, 0 tracks, DRC 0 violations and 225 unconnected. Footprints are partly provisional and the netlist is one day older than the current one. The result measures the class of the problem, not the final board.
- Runs: A = rules as exported (through vias only). B = via_at_smd on, and blind via padstacks if Freerouting accepts them.
- Crash, timeout or refusal is recorded as itself, never as pass or fail.
- Writes only in the probe folder and /root/ring-wiring-probe on <build-server>.

## Completed 2026-11-12 23:59:51 CET (Mac clock, CET; server clock is UTC, one hour behind)

Caveat: the board copy is the 10 Nov file (sha256 in copy-sha.txt, same as the original). Footprints are partly provisional and the netlist is one day old. This measures the class of the problem, not the final board.

## Setup and commands
- Tools: Freerouting 2.5.0 jar (official GitHub release, saved on the server only; options from fr-cli-docs.md, the project docs for v2.5.0), run in Docker image eclipse-temurin:25-jre (480 MB, left on the server; eclipse-temurin:21-jre 462 MB also pulled, it failed: class file version 69 needs Java 25). Both images are left. Containers were started with --rm; `docker ps -a` on the server lists none of mine after the runs (server-final-state.txt).
- DSN export (KiCad 10.0.8 Python): `run_kipy.sh export_dsn.py ring.kicad_pcb ring-A.dsn` -> ring-A.dsn. DSN holds 91 nets, rule width 100 um, clearance 100 um, one via Via[0-5]_250:150_um.
- Router (runA2.sh form, see run2.sh): `nice -n 19 docker run --rm --cpus 8 eclipse-temurin:25-jre timeout 1200 java -jar freerouting-2.5.0.jar --gui.enabled=false -de X.dsn -do X.ses -mp 1 -mt 0`.
- Import: `run_kipy.sh import_ses.py ring.kicad_pcb X.ses ringX.kicad_pcb` then `kicad-cli pcb drc --severity-all --all-track-errors` (drc-X.txt, analysis by analyze.py into analysis-X.txt, layers.py into layers-X.txt).
- Baseline (copy before routing): drc-baseline.txt, 0 DRC violations, 225 unconnected items. Matches the brief.
- Scripts: srv.sh (ssh and rsync with remote.sh's options and key path, masks the address), make_c.py (builds ring-C.dsn).

## Runs (4 of 4 used)
| Run | Input | Router setting | Result |
|---|---|---|---|
| A1 | ring-A.dsn (as KiCad exports) | -mp 100, 20 min limit | timeout, exit 124, no SES written (runA1-100passes.log, last lines "exit 124"). Passes oscillated: unrouted 88, 158, 148, 150, 152, 139, 148, 88 (restore), 156, 151. Best was pass 1. Recorded as a timeout, not a pass or a fail. |
| A2 | ring-A.dsn | -mp 1 -mt 0 | SES saved, imported, DRC run |
| B1 | ring-B.dsn (= A plus `(control (via_at_smd on))` in structure) | -mp 1 -mt 0 | SES saved, imported, DRC run |
| C1 | ring-C.dsn (= B plus five blind padstacks Via[i-(i+1)]_200:100_um, F.Cu to B.Cu pairs of neighbours) | -mp 1 -mt 0 | SES saved, imported, DRC run |

Run times (summary-runs.txt, Freerouting "elapsed"): A2 2 min 44 s, B1 2 min 42 s, C1 2 min 32 s (A1 20 min, killed). The optimizer stage was skipped in every run by Freerouting itself ("optimizer only runs on completely routed boards"), so -mt 0 changed nothing.

## Numbers per run
Freerouting's own count (summary-runs.txt): all three runs "started with 225 unrouted nets", final "88 unrouted and 0 violations", score 478.52. So 137 of 225 connections completed and 88 not completed, in each run.
KiCad counts (drc-A2.txt, drc-B1.txt, drc-C1.txt, counts by analyze.py):

| | A2 | B1 | C1 |
|---|---|---|---|
| unconnected items (KiCad) | 89 | 89 | 88 |
| total violations reported | 218 | 218 | 213 |
| annular_width | 116 | 116 | 110 |
| track_width (0.075 mm vs min 0.1) | 40 | 40 | 42 |
| copper_edge_clearance | 30 | 30 | 19 |
| via_dangling (warning) | 29 | 29 | 28 |
| track_dangling (warning) | 3 | 3 | 0 |
| drill_out_of_range | 0 | 0 | 7 |
| via_diameter | 0 | 0 | 7 |
| track segments (layers.py) | 708 | 708 | 665 |
| vias | 116 (all F.Cu-B.Cu) | 116 (all F.Cu-B.Cu) | 110 (103 F.Cu-B.Cu, 7 F.Cu-In1.Cu) |
| layers with copper | F.Cu 525, In1 67, In2 48, In3 45, In4 23, B.Cu 0 | same | F.Cu 494, In1 57, In2 24, In3 50, In4 40, B.Cu 0 |
| nets with an unconnected end | 56 | 56 | 59 |

Nets not completed: the full lists are in analysis-A2.txt, analysis-B1.txt and analysis-C1.txt (the "nets with an unconnected item" line). B.Cu got no track in any run.

Where the unrouted nets cluster (analysis files, pad ends of unconnected items per part): U1 51 (A2), 51 (B1), 55 (C1); U2 11, 13, 22; U4 6, 6, 4; J1 3, 3, 6; J_BAND_B 3, 3, 3; C10 4, 4, 4. U1 (0.325 mm pitch) holds more than half of all unconnected ends in every run; U2 (0.4 mm pitch) is second. Freerouting's fanout stage escaped only 201 of 316 SMD pins (63.6 percent) in every run (runA2.run.log).

## Findings that block the pass line whatever the router does
1. The board's own via rule is inconsistent with its own minimum annular width: a 0.25 mm via with a 0.15 mm drill has a 0.05 mm ring, and KiCad's check says "min annular width 0.1000 mm; actual 0.0500 mm" on every via (drc-A2.txt, 116 hits). The project file (ring.kicad_pro) sets no via annulus, so KiCad's default 0.1 applies. Not caused by the router. The baseline cannot show it because it has no vias. The microvia pair 0.2/0.1 has the same 0.05 ring.
2. Freerouting drew 0.075 mm track pieces (40 hits) although the rule is 0.1; cause not isolated, no run examined it.
3. 30 copper-to-edge hits at the board outline: the router does not keep the 0.1 edge clearance that the project sets. Cause not isolated.
4. In C1, KiCad flagged the imported blind vias (drill_out_of_range 7, via_diameter 7); the 0.2/0.1 padstacks do not meet the rules the way KiCad reads them. Not isolated.
5. ANT1's four pads lie outside the board outline (Freerouting warns at load, runA2.run.log), a known open item in board-notes.md.

## Not shown / limits
- Run B1 differs from A2 only by the via_at_smd control. The result counts are identical (88 unrouted, same score, same fanout count), so the control had no visible effect. Whether Freerouting read it was not checked in the log.
- Only pass 1 was kept for A2, B1, C1 (-mp 1). The 100-pass run A1 never improved on pass 1 (best 88) and got no SES. A longer or different strategy was not tried (4 run limit).
- Blind vias were used (7 F.Cu-In1) but did not reduce the unrouted count (88).

## Deviations and housekeeping
- No git run (brief rule), so the pre-registration is time stamped with the date command only and not committed.
- The first ssh attempt failed on a quoting error and its terminal output showed the server address. That output went into server-session.log, which I then deleted and rewrote (masked). The address is not in any file here.
- First router attempt used Java 21 and failed on class version (ring-A.attempt1-java21.log); it is not counted as a run. A1 was started with -mp 100 and no change was made to the pass line.
- Disk on the Mac: probe folder holds a few small files; no image pulled on the Mac. Server had 43 GB free before the pulls.
- Files left on the server: /root/ring-wiring-probe (jar 65 MB, DSN, SES, logs), mine only.

## Verdict against the pass line
Pass line: 0 unconnected items and 0 violations. Result: best run C1 has 88 unconnected and 213 violations; A2 and B1 have 89 unconnected and 218 violations. Hypothesis not confirmed. Freerouting completed 137 of 225 connections and left 88 in all three runs; unrouted ends cluster at U1 and U2.

RESULT: done, hypothesis not confirmed: Freerouting 2.5.0 completed 137 and left 88 of 225 connections in each of runs A2, B1 and C1 (KiCad unconnected 89, 89, 88; violations 218, 218, 213) and run A1 timed out at 20 minutes with no output.
