import sys; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from aerobooster_revC_model import *
def row(c):
    r = run(c); m = summary(r); a = r["acc"]
    print(f"{m['name']:<46} brkf {m['breakfast']:3.0f} main {m['main']:3.0f} eve {m['evening']:3.0f} tea {m['tea']:3.0f} kisra/wk {m['kisra_wk']:.2f} ({m['kisra_full']:.0f}%) oven/wk {m['oven_wk']:.2f} ({m['oven_full']:.0f}%) cart {r['cart']} bonus {r['bonus']}")
    return r
row(Config("P6 lower threshold 200 (as filed)", pv_m2=6, thr_lo=200))
row(Config("P6 kisra 4/week", pv_m2=6, kisra_per_week=4))
row(Config("P6 kisra 7/week (every day)", pv_m2=6, kisra_per_week=7))
row(Config("P6 surplus uses off", pv_m2=6, bonus=False))
row(Config("P6L kisra 7/week", pv_m2=6, store_l=45, kisra_per_week=7))
row(Config("H3 kisra 7/week", trough_m2=3, pv_m2=4, kisra_per_week=7))
for seed in (11, 23, 42):
    row(Config(f"P6L weather seed {seed}", pv_m2=6, store_l=45, seed=seed))
    row(Config(f"H3 weather seed {seed}", trough_m2=3, pv_m2=4, seed=seed))
print("\nannual energy (kWh/yr):")
for c in (Config("P6L", pv_m2=6, store_l=45), Config("H3", trough_m2=3, pv_m2=4)):
    r = run(c); a = r["acc"]
    print(c.name, {k: round(v) for k, v in a.items() if k not in ('dni','gt')}, "cartridges", r["cart"], "bonus bakes", r["bonus"], "usable store kWh %.2f" % r["usable"])
