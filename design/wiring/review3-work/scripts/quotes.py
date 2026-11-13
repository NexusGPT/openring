# review 3: print the pinned file lines this review cites (path:line: text), from the delivered files
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
SPEC = {
    "design/mfg/assembly/assembly.md": [73, 96, 99, 112, 131, 136, 138, 139, 144, 145, 148, 153, 156, 210, 212, 213, 374],
    "design/ecad/band/band-interface.md": [55, 65, 91, 94, 106, 115, 123, 137, 141],
    "design/ecad/case/pcb/board-notes.md": [296, 297, 299, 300, 301],
    "design/case/case-architecture.md": [64, 151, 152],
    "design/wiring/product-wiring.csv": [59, 64],
    "design/bom.csv": [62, 75],
    "design/ecad/ring/pcb/fab/stackup.txt": [20],
}
n = 0
for f, lines in SPEC.items():
    t = open(R + f, newline="").read().split("\n")
    for k in lines:
        print("%s:%d: %s" % (f, k, t[k - 1][:900])); n += 1
print("RESULT quoted lines=%d" % n)
