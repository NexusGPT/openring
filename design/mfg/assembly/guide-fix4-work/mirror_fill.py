"""Mirror the new hot-bar check texts of joints.csv into guide-joints-work/fill_joints.py (HOTBAR dict)."""
import csv, re, json, ast
A=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/assembly")
rows={r['joint_id']:r for r in csv.DictReader(open(A+'/joints.csv',newline='',encoding='utf-8'))}
p=A+'/guide-joints-work/fill_joints.py'
s=open(p,encoding='utf-8').read()
for wl,land in [('W011','A8'),('W021','A6'),('W026','B2'),('W032','B7'),('W027','B3')]:
    chk=rows['J-%s-A'%wl]['check']
    pre='land %s, '%land; suf=' (hotbar-joint.md section 4)'
    assert chk.startswith(pre) and chk.endswith(suf), wl
    body=chk[len(pre):-len(suf)]
    m=re.search(r'^    "%s": \("%s", "(.*)"\),$'%(wl,land), s, re.M)
    assert m, wl
    new='    "%s": ("%s", %s),'%(wl,land,json.dumps(body))
    s=s[:m.start()]+new+s[m.end():]
    print('mirrored', wl)
ast.parse(s)
d=ast.literal_eval(re.search(r'HOTBAR = (\{.*?\n\})', s, re.S).group(1))
for wl,land in [('W011','A8'),('W021','A6'),('W026','B2'),('W032','B7'),('W027','B3')]:
    assert 'land %s, %s (hotbar-joint.md section 4)'%(land,d[wl][1])==rows['J-%s-A'%wl]['check'], wl
print('parses; the 5 HOTBAR texts give the joints.csv checks exactly')
open(p,'w',encoding='utf-8').write(s)
