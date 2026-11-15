import sys; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from aerobooster_revC_model import *
CAUT = (0.55, 6.6, 0.016, 12.0)
cfgs = [
 Config("B  trough 6 m2 (revision B)", trough_m2=6),
 Config("B' trough 6 m2, cautious receiver", trough_m2=6, receiver=CAUT),
 Config("H1 trough 6 + PV 2 m2", trough_m2=6, pv_m2=2),
 Config("H2 trough 3 + PV 2 m2", trough_m2=3, pv_m2=2),
 Config("H3 trough 3 + PV 4 m2", trough_m2=3, pv_m2=4),
 Config("P4 PV 4 m2", pv_m2=4),
 Config("P6 PV 6 m2", pv_m2=6),
 Config("P8 PV 8 m2", pv_m2=8),
 Config("P6L PV 6 m2, store 45 L", pv_m2=6, store_l=45),
 Config("P6G PV 6 m2, store 30 L + 10% graphite", pv_m2=6, eg_frac=0.10),
]
hdr = f"{'config':<40}{'brkf':>6}{'main':>6}{'eve':>6}{'tea':>6}{'kis/wk':>7}{'kis3%':>6}{'ov/wk':>6}{'ov2%':>6}{'wash':>6}{'heat':>6}{'in':>6}{'away':>6}{'cook':>6}{'cart':>5}{'bon':>5}{'minSOC':>7}{'bal':>9}"
print(hdr)
out = {}
for c in cfgs:
    r = run(c); m = summary(r); out[c.name] = (r, m)
    print(f"{m['name']:<40}{m['breakfast']:>6.0f}{m['main']:>6.0f}{m['evening']:>6.0f}{m['tea']:>6.0f}{m['kisra_wk']:>7.2f}{m['kisra_full']:>6.0f}{m['oven_wk']:>6.2f}{m['oven_full']:>6.0f}{m['wash']:>6.0f}{m['heating']:>6.0f}{m['coll']:>6.1f}{m['turned']:>6.1f}{m['cook']:>6.2f}{r['cart']:>5}{r['bonus']:>5}{m['soc']:>7.0f}{m['bal']:>9.1e}")
print("\nannual DNI on tracked aperture %.2f, global on tilted plane %.2f kWh/m2/day" % (m['dni'], m['gt']))
from collections import Counter
print("day types:", Counter(make_year(7)))
for k in ("B  trough 6 m2 (revision B)", "P6 PV 6 m2", "H2 trough 3 + PV 2 m2"):
    print(k, "storm days (day, store C at midnight, kisra that day):", out[k][0]["storm"])
