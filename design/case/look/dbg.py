import sys, json, os
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look"))
import numpy as np
from PIL import Image
import render as R
prm = json.load(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/case_params.json")))
sc = R.Scene(prm)
tgt = np.array([12.0, 0, 17.0])
eye = tgt + 300 * R.unit(np.array([-0.70, -0.72, 0.62]))
cam = R.Cam(eye, tgt + np.array([0, 0, 2]), fov=14, w=800, h=600)
d, tid, _ = R.rasterize(cam, sc.V, sc.T, need_attr=False)
m = np.where(tid >= 0, sc.M[np.where(tid >= 0, tid, 0)], -1)
pal = np.array([[200,200,200],[255,255,255],[255,200,0],[40,40,40],[0,0,0],[0,255,0],[255,0,0],[0,0,255],[0,255,255],[240,240,250]]+[[128,128,128]]*5)
img = np.where((m >= 0)[..., None], pal[np.clip(m, 0, 14)], 230).astype(np.uint8)
Image.fromarray(img).save((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look/dbg_mat.png"))
print(R.MATNAMES)
