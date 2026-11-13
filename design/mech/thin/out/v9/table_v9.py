#!/usr/bin/env python3
"""Per-size table from out/v9/final_usN.log (lines copied by pattern, not typed)."""
import re
pats = {"result": r"^RESULT .*", "findings": r"^check_thin: .*", "plan": r"^board plan: .*", "bp": r"^BOARD-PLAN: .*",
        "zone": r"^ZONE copper-free .*", "ant": r"^ANTENNA free space .*", "room": r"under the antenna [\d.]+ mm of room",
        "mbody": r"^motor free space to outer_body__metal: .*", "mzone": r"^MOTOR body to the copper-free zone prism: .*",
        "rc": r"^radio corner RC1: .*", "cell": r"^cell: .*", "glb": r"^GLB: .*"}
for n in range(7, 14):
    t = open(f"final_us{n}.log").read()
    print(f"== US {n}")
    for k, p in pats.items():
        m = re.search(p, t, re.M)
        print(f"  {k}: {m.group(0) if m else 'MISSING'}")
