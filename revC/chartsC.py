import sys; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from aerobooster_revC_model import *
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
INK2="#52514e"; SURF="#fcfcfb"
names=[("Trough 6 m² (rev. B)",Config("B",trough_m2=6)),("Trough 3 + PV 4 m²",Config("H3",trough_m2=3,pv_m2=4)),
       ("PV 4 m²",Config("P4",pv_m2=4)),("PV 6 m²",Config("P6",pv_m2=6)),("PV 6 m², 45 L store",Config("P6L",pv_m2=6,store_l=45))]
res=[(n,summary(run(c))) for n,c in names]
metrics=[("Breakfast","breakfast"),("Evening meal","evening"),("Weeks with 3 kisra days","kisra_full"),("Weeks with 2 oven bakes","oven_full")]
cols=["#2a78d6","#eb6834","#1baf7a","#eda100"]
fig,ax=plt.subplots(figsize=(10,4.6)); ax.set_facecolor(SURF); fig.patch.set_facecolor("white")
x=np.arange(len(res)); w=0.19
for i,(lab,k) in enumerate(metrics):
    v=[m[k] for _,m in res]
    b=ax.bar(x+(i-1.5)*w,v,w-0.02,color=cols[i],label=lab)
    for xi,vi in zip(x+(i-1.5)*w,v): ax.text(xi,vi+1,f"{vi:.0f}",ha="center",fontsize=7,color=INK2)
ax.set_xticks(x); ax.set_xticklabels([n for n,_ in res]); ax.set_ylim(0,110); ax.set_ylabel("% of the year served",color=INK2)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.grid(axis="y",color="0.9"); ax.set_axisbelow(True)
ax.legend(frameon=False,ncol=4,loc="upper center",bbox_to_anchor=(0.5,1.12),fontsize=8)
fig.text(0.01,0.01,"AeroBooster rev. C annual simulation, synthetic Khartoum-type weather (219 clear, 77 hazy, 37 broken-cloud, 32 heavy-dust days). Calculated, not measured.",fontsize=7,color=INK2)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig("chart_service.png",dpi=160)
# daily store temperature
fig,ax=plt.subplots(figsize=(10,3.8)); ax.set_facecolor(SURF)
for (lab,c),col in zip([("PV 6 m², 45 L store",Config("P6L",pv_m2=6,store_l=45)),("Trough 6 m² (rev. B)",Config("B",trough_m2=6))],["#2a78d6","#eb6834"]):
    r=run(c); T=[d["T"] for d in r["daily"]]
    ax.plot(range(1,366),T,color=col,lw=1.3,label=lab+": store at midnight")
for y,l in ((215,"kisra floor 215 °C"),(150,"meal floor 150 °C")):
    ax.hlines(y,1,365,color="0.6",lw=0.8,ls="--"); ax.text(368,y,l,fontsize=7,va="center",color=INK2)
ax.axvspan(15,17,color="0.85",lw=0); ax.text(16,60,"3-day\nstorm",fontsize=7,ha="center",color=INK2)
ax.set_xlim(1,400); ax.set_ylabel("°C",color=INK2); ax.set_xlabel("Day of year",color=INK2)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.legend(frameon=False,fontsize=8,loc="lower right")
fig.tight_layout(); fig.savefig("chart_store_year.png",dpi=160)
print("ok")
