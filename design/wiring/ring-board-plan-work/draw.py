
import json,sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from rules import KEEPOUTS,RESERVED,BSIDE
d=json.load(open(sys.argv[1]))
fig,ax=plt.subplots(figsize=(16,7.6))
ax.add_patch(Rectangle((-13.6,-6.3),27.2,12.6,fill=False,lw=1.5))
for k in KEEPOUTS:
    r=k["r"]; ax.add_patch(Rectangle((r[0],r[1]),r[2]-r[0],r[3]-r[1],color="orange",alpha=0.3))
for r in RESERVED: ax.add_patch(Rectangle((r[0],r[1]),r[2]-r[0],r[3]-r[1],color="cyan",alpha=0.3))
for ref,(x,y,rot,c,z) in d.items():
    if ref in BSIDE: continue
    ax.add_patch(Rectangle((c[0],c[1]),c[2]-c[0],c[3]-c[1],fill=False,lw=0.6))
    ax.text(x,y,ref,fontsize=5,ha="center",va="center")
ax.set_xlim(-14,14); ax.set_ylim(6.6,-6.6); ax.set_aspect("equal"); ax.grid(True,lw=0.2)
plt.savefig(sys.argv[2],dpi=110,bbox_inches="tight")
