import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *
INC = math.cos(math.radians(23.45))            # 0.917: polar-axis trough at either solstice
V2 = dict(ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)
capsec = dict(eta0=0.58, a1=6.6*0.85, a2=0.016*0.85)
print(f"incidence factor at the solstices (polar axis): {INC:.3f}")
sec("13. FINAL TABLE: v2 store build, broken cloud, polar-axis trough at the SOLSTICES (beam x 0.917)")
block("A. filed fixed CPC 5.59 m2", CPC, **V2)
R = {}
R['B6'] = block("B. 6 m2, selective steel receiver + cap + secondary (ADOPTED)", trough(6.0, **capsec), inc=INC, **V2)
block("B. 6 m2, same, at the EQUINOX (beam x 1.0)", trough(6.0, **capsec), **V2)
block("B. 6 m2, selective steel receiver, no cap, no secondary", trough(6.0), inc=INC, **V2)
block("B. 6 m2, cap + secondary, brush-on selective paint (emittance doubled)", trough(6.0, eta0=0.58, a1=6.6*0.85, a2=0.032*0.85), inc=INC, **V2)
block("B. 6 m2, cap + secondary, ordinary black paint", trough(6.0, eta0=0.58, a1=6.6*0.85, a2=0.067*0.85), inc=INC, **V2)
block("B. 6 m2, cap + secondary, poor optics 0.48", trough(6.0, eta0=0.48, a1=6.6*0.85, a2=0.016*0.85), inc=INC, **V2)
block("B. 6 m2, cap + secondary, glass mirrors (optical 0.65)", trough(6.0, eta0=0.65, a1=6.6*0.85, a2=0.016*0.85), inc=INC, **V2)
block("B. 5 m2, cap + secondary", trough(5.0, **capsec), inc=INC, **V2)
block("B. 4 m2, cap + secondary", trough(4.0, **capsec), inc=INC, **V2)
block("B. 3 m2 (one trough), cap + secondary", trough(3.0, **capsec), inc=INC, **V2)
block("B. 8 m2, cap + secondary", trough(8.0, **capsec), inc=INC, **V2)
ev = dict(eta0=0.60, a1=0.28, a2=0.009, C=10.8)
block("B. 4 m2, evacuated all-glass tube receiver (as certified)", trough(4.0, **ev), inc=INC, **V2)
block("B. 4 m2, evacuated tube, 3x certified loss and 70 K offset", trough(4.0, eta0=0.60, a1=0.84, a2=0.027, C=10.8), inc=INC, abs_offset=70.0, **V2)
block("B. 6 m2, evacuated all-glass tube receiver (as certified)", trough(6.0, **ev), inc=INC, **V2)

sec("14. UNIFORM HAZE (dust) instead of broken cloud, v2 store build")
block("A. fixed CPC", CPC, broken_cloud=False, **V2)
block("B. 6 m2 adopted", trough(6.0, **capsec), inc=INC, broken_cloud=False, **V2)

sec("15. Tracker lost for 1 or 2 days of a clear summer week (adopted B)")
for n in (1, 2):
    cl = [1.0]*7
    # a day without tracking: beam for the trough only is lost -> emulate with a per-day mask
    p = cfg(trough(6.0, **capsec), cl, 'summer', inc=INC, **V2)
    mask = [1,1,0,1,1,1,1] if n == 1 else [1,0,1,1,0,1,1]
    base_irr = mod.irr_K
    def irr2(pp, t_h, day, G, _m=mask, _b=base_irr):
        g, d = _b(pp, t_h, day, G)
        return (g if _m[day % 7] else 0.0), d
    mod.irr_K = irr2
    r = run(p); line(f"clear summer week, {n} day(s) without tracking", r)
    mod.irr_K = base_irr

d = 7
for lab, season in (("summer", 'summer'), ("winter", 'winter')):
    r = run(cfg(trough(6.0, **capsec), CLEAR, season, inc=INC, **V2)); a = r['raw']
    print(f"\nAdopted B, clear {lab} day at solstice (kWh/day): collected {r['coll']:.2f} | rejected off-sun {r['dump']:.2f} | store loss {r['loss']:.2f} | jacket recovers {r['jacket']:.2f} | "
          f"stew+morning {a['cook_del']/d:.2f} | kisra {a['hl_del']['kisra']/d:.2f} | oven {a['hl_del']['oven']/d:.2f} | cascade {r['casc']:.2f} | "
          f"heating {a.get('heat_del',0)/d:.2f} | flat {a['coll_W']/d:.2f} | tea {a['tea_del']/d:.2f} | usable store {r['usable']:.2f} | G {r['G']:.3f} W/K")
# beam energy
def beam_day(season, inc):
    p = cfg(trough(6.0, **capsec), CLEAR, season, inc=inc, **V2); e = 0.0; dt = 1/60
    t = 0.0
    while t < 24: 
        g, _ = irr_K(p, t, 0, 0.0); e += g*dt; t += dt
    return e
print(f"\ntracked beam on the aperture, clear day: summer {beam_day('summer', INC):.2f} (equinox-type {beam_day('summer',1.0):.2f}), winter {beam_day('winter', INC):.2f} kWh/m2")
k = capsec
for T in (200, 235, 270, 290):
    dT = T - 35; loss = (k['a1']*dT + k['a2']*dT*dT)/12.0
    G = 0.95*BEAM_CLEAR*INC*1000
    print(f"  adopted receiver at {T} C: loss {loss:5.0f} W per m2 aperture; efficiency at {G:.0f} W/m2 beam = {100*(k['eta0']-loss/G)*0.95:.1f} %")
