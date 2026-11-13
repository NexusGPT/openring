from build123d import import_step, GeomType
sh = import_step((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/parts/shell.step"))
for f in sh.faces():
    if f.geom_type == GeomType.PLANE:
        c = f.center(); n = f.normal_at(c)
        if c.X < -9.0 and c.Y > 5 and 10 < c.Z < 20:
            bb = f.bounding_box()
            print("plane face centre (%.2f %.2f %.2f) n (%.2f %.2f %.2f) area %.2f bbox x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (c.X, c.Y, c.Z, n.X, n.Y, n.Z, f.area, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))
