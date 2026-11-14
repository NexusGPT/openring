#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# kp.sh in.kicad_pcb out.kicad_pcb script.py [args] : copy in to pcb/work.kicad_pcb (project and rules beside it), run the KiCad Python
# script with in = out = pcb/work.kicad_pcb, copy the result to out, then put back the project file (KiCad's save rewrites it) and check its sha256
H=$REPO_ROOT/design/ecad/ring-route-h
IN=$1; OUT=$2; S=$3; shift 3
cp "$H/pcb/ring-thin-a2.kicad_pro" "$H/pcb/work.kicad_pro" && cp "$IN" "$H/pcb/work.kicad_pcb" || exit 9
cd "$H/pcb" && nice -n 19 "$H/scripts/run_kipy.sh" "$S" "$H/pcb/work.kicad_pcb" "$H/pcb/work.kicad_pcb" "$@"
RC=$?
cp "$H/pcb/work.kicad_pcb" "$OUT"
cp "$H/pcb/ring-thin-a2.kicad_pro" "$H/pcb/work.kicad_pro"
cd "$H/pcb" && shasum -a 256 work.kicad_pro | grep -q b79a620d57d5251670c6f0b2980fff439fee7c5587db09e0141bbd6c7f912009 && echo "project restored" || echo "PROJECT NOT RESTORED"
echo "script exit $RC"
