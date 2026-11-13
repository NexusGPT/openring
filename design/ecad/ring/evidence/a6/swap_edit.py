import sys
P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s = open(P).read()
frm, to = sys.argv[1], sys.argv[2]
for old, new in (("('MOTOR_DRV', 'MOT-', '%s')" % frm, "('MOTOR_DRV', 'MOT-', '%s')" % to), ("('VDD_3V0', 'MOT+', '%s')" % frm, "('VDD_3V0', 'MOT+', '%s')" % to)):
    assert s.count(old) == 1, old
    s = s.replace(old, new)
open(P, 'w').write(s)
print('motor rows', frm, '->', to)
