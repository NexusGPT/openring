"""end_wall.py <body.stl>: read the binary STL of the machined body (design/mfg/parts/body/body-us9.stl, inside model v7 cut)
and print, at each block end, the outer skin X of the body for Z bins between the cavity floor (0.40) and the glass seat (2.75),
over |Y| <= 6.45 (the panel pocket width). Wall = outer skin - panel pocket face (13.725). Vertex based: the skin between two
vertices is not sampled, so a printed outer X is a lower bound of the true outer X at that Z bin when the skin is convex."""
import sys
import struct
import numpy as np

data = open(sys.argv[1], "rb").read()
n = struct.unpack("<I", data[80:84])[0]
rec = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
V = rec["v"].reshape(-1, 3).astype(float)
print(f"triangles {n}, vertices {len(V)}; body box X {V[:,0].min():.3f}..{V[:,0].max():.3f}, Y {V[:,1].min():.3f}..{V[:,1].max():.3f}, Z {V[:,2].min():.3f}..{V[:,2].max():.3f}")
POCKET = 13.725
for sgn, name in ((1, "fingertip (+X)"), (-1, "hand (-X)")):
    sel = V[(sgn * V[:, 0] > 13.0) & (np.abs(V[:, 1]) <= 6.45)]
    print(f"== {name}: {len(sel)} vertices with |X| > 13.0 and |Y| <= 6.45")
    for z0 in np.arange(0.0, 3.21, 0.2):
        s = sel[(sel[:, 2] >= z0) & (sel[:, 2] < z0 + 0.2)]
        if len(s) == 0:
            print(f"  Z {z0:.1f}..{z0+0.2:.1f}: no vertex")
            continue
        xo = (sgn * s[:, 0]).max()
        print(f"  Z {z0:.1f}..{z0+0.2:.1f}: outer |X| {xo:.3f}  wall beyond the pocket face 13.725: {xo - POCKET:.3f}")
