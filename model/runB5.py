import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *
INC = math.cos(math.radians(23.45))
V2 = dict(ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)
capsec = dict(eta0=0.58, a1=6.6*0.85, a2=0.016*0.85)
# regression: patched == archived when new keys unused
p0 = base(cloud=POOR, night_kWh=0.30, n_K=3*3*0.3529*1.76/A)
mod.MEDIA['salt']['L_fus'] = 110.0; orig.MEDIA['salt']['L_fus'] = 110.0
a = mod.simulate(dict(p0)); b = orig.simulate(dict(p0))
same = all(abs(a[k]-b[k]) < 1e-9 for k in ('coll_K','dump_K','loss_b','tail','coll_W')) and a['meal_ok']==b['meal_ok'] and a['hl_ok']==b['hl_ok']
print("patched == archived when new keys unused:", same)
NONE = dict(mode='trk', area=0.0, K=dict(eta0=0.0, a1=0.0, a2=0.0, C=1.0, pipe=1.0))
print("PV: module 21 %, hot-climate derating 0.88, controller and wiring 0.93 -> 0.172 of plane-of-array global")
sec("16. BENCHMARK: PV modules + resistance heater in the same store (no concentrator), v2 store build")
block("PV only, 6 m2 (about 1.26 kWp)", NONE, A_pv=6.0, **V2)
block("PV only, 4 m2 (about 0.84 kWp)", NONE, A_pv=4.0, **V2)
block("PV only, 8 m2 (about 1.68 kWp)", NONE, A_pv=8.0, **V2)
sec("17. HYBRID: adopted trough 6 m2 + one PV module of 2 m2 (about 420 W) on a heater in the store")
block("broken cloud", trough(6.0, **capsec), inc=INC, A_pv=2.0, **V2)
block("uniform haze (dust)", trough(6.0, **capsec), inc=INC, A_pv=2.0, broken_cloud=False, **V2)
block("trough 4 m2 + PV 2 m2, broken cloud", trough(4.0, **capsec), inc=INC, A_pv=2.0, **V2)
sec("18. for reference again: adopted trough alone / A alone, uniform haze")
block("B 6 m2 alone, haze", trough(6.0, **capsec), inc=INC, broken_cloud=False, **V2)
block("PV only 6 m2, (haze = same as cloud for PV)", NONE, A_pv=6.0, broken_cloud=False, **V2)
for lab, kw in (("PV 6 m2", dict(A_pv=6.0)),):
    for season in ('summer','winter'):
        r = run(cfg(NONE, CLEAR, season, **kw, **V2))
        print(f"{lab} clear {season} day: delivered to store {r['coll']:.2f} kWh/day = {r['coll']/6:.2f} kWh per m2")
