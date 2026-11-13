from build123d import import_step
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/parts/")
j = import_step(D + "J1_usb4105.step"); sh = import_step(D + "shell.step"); pl = import_step(D + "base_plate.step")
print("J1 to shell %.3f, to plate %.3f" % (j.distance_to(sh), j.distance_to(pl)))
for n in ("cell_dnk852338", "main_board", "LED1"):
    p = import_step(D + n + ".step"); print(n, "%.3f" % min(p.distance_to(sh), p.distance_to(pl)))
best = []
for f in sh.faces():
    d = j.distance_to(f)
    if d < 0.4:
        c = f.center(); n = f.normal_at(c)
        best.append((round(d, 3), f.geom_type.name, round(c.X, 2), round(c.Y, 2), round(c.Z, 2), round(n.X, 2), round(n.Y, 2), round(n.Z, 2), round(f.area, 2)))
for b in sorted(best)[:8]: print(b)
bb = j.bounding_box(); print("J1 bbox", [round(v, 2) for v in (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z)])
