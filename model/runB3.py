import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *
V2 = dict(ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)
capsec = dict(eta0=0.58, a1=6.6*0.85, a2=0.016*0.85)
sec("12. ALL ON THE v2 STORE BUILD (table for the design document)")
block("A. filed fixed CPC 5.59 m2", CPC, **V2)
block("B. trough 4 m2, steel receiver + cap + secondary", trough(4.0, **capsec), **V2)
block("B. trough 6 m2, steel receiver + cap + secondary  (ADOPTED)", trough(6.0, **capsec), **V2)
block("B. trough 6 m2, steel receiver, plain (no cap, no secondary)", trough(6.0), **V2)
block("B. trough 6 m2, plain black paint instead of selective", trough(6.0, eta0=0.58, a1=6.6*0.85, a2=0.067*0.85), **V2)
block("B. trough 4 m2, evacuated all-glass tube receiver", trough(4.0, eta0=0.60, a1=0.28, a2=0.009, C=10.8), **V2)
block("B. trough 3 m2 (one trough only), steel + cap + secondary", trough(3.0, **capsec), **V2)

print("\n--- lens strip above the receiver (per metre of trough; effective width of trough = 1.6 m x mirror path) ---")
for rho, gam, lab in ((0.84, 0.85, "aluminium mirror, hand-built"), (0.93, 0.90, "glass mirror, good shape")):
    mir = rho*0.90*0.92*gam; lens = 0.88*0.90*0.92*0.95; base = 1.6*mir
    for w in (0.058, 0.15, 0.30):
        net = w*lens - 0.058*0.90*0.92 - (w-0.058)*mir
        print(f"  {lab:<30} strip {w*1000:3.0f} mm: mirror path {mir:.3f}, lens path {lens:.3f}, net {net:+.4f} m = {100*net/base:+.1f} % of the trough")
