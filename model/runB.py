import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *

# 0. identity check: no new keys -> archived model
p0 = dict(orig.BASE); p0.update(n_W=0.25, n_K=3*3*0.3529*1.76/A, C_K=1.94, eta_opt_K=0.84**0.9, pump_W=False,
          retention_saving=0.30, ins_mm=150.0, tail_full_margin=40, tail_window=(8.0,20.0), V_tank=120.0,
          meal_kWh=0.80, hot_loads=LOADS, cloud=POOR, night_kWh=0.30)
ro, rp = orig.simulate(p0), mod.simulate(p0)
print("patched == archived when new keys unused:",
      all(abs(ro[k]-rp[k]) < 1e-9 for k in ('coll_K','loss_b','cook_del','tail','tea_del')))
print("sunny share of clear-day beam for cloud factors:",
      {c: round(sunny_share(c), 2) for c in (1.0, 0.8, 0.7, 0.6, 0.55, 0.5, 0.45)})

# clear-day beam energy on a tracked aperture
def daily(p):
    E = 0.0
    for i in range(24*60):
        g, d = irr_K(p, i/60.0, 0, 0.0); E += g/60.0
    return E
ps = cfg(trough(), CLEAR, 'summer'); pw = cfg(trough(), CLEAR, 'winter')
print(f"tracked-aperture beam energy, clear day: summer {daily(ps):.2f}  winter {daily(pw):.2f} kWh/m2")
T = trough()['K']
for Tm in (200, 235, 270, 290):
    dT = Tm - 35; loss = (T['a1']*dT + T['a2']*dT*dT)/T['C']
    print(f"  receiver {Tm} C: loss {loss:5.0f} W per m2 aperture; efficiency at 0.746 kW/m2 = {max(T['eta0']-loss/746,0)*100:4.1f} %")

sec("1. SAME BASIS FOR BOTH: wool 0.050, latent 97, winter 20 C, broken cloud (sun on/off), filed loads, 0.5 m2 flat")
A_ = block("A. filed fixed CPC, 5.59 m2 (collector as modelled)", CPC)
B4 = block("B. tracked trough 4.0 m2, steel absorber, selective, glass envelope, C=12, optical 0.55", trough(4.0))

sec("2. OPTION B: aperture")
for ar in (3.0, 4.0, 5.0, 6.0):
    block(f"trough {ar:.0f} m2", trough(ar))

sec("3. OPTION B, 4 m2: receiver and optics")
block("selective + insulated top cap (loss -15%)", trough(4.0, a1=6.6*0.85, a2=0.016*0.85))
block("selective + cap + secondary reflector (optical 0.58)", trough(4.0, eta0=0.58, a1=6.6*0.85, a2=0.016*0.85))
block("plain black paint, not selective (a2 0.067)", trough(4.0, a2=0.067))
block("standard all-glass evacuated tube as receiver, C=10.8 (beyond its 250 C rating)", trough(4.0, eta0=0.60, a1=0.28, a2=0.009, C=10.8))
block("poor optics 0.45", trough(4.0, eta0=0.45))
block("good glass mirrors 0.65", trough(4.0, eta0=0.65))
block("smaller absorber 28 mm, C=18, intercept lower (optical 0.50)", trough(4.0, eta0=0.50, C=18.0))

sec("4. OPTION B, 4 m2: v2 store insulation and recovery jacket, 2 m2 flat collector")
block("as section 1 (150 mm wool, 0.5 m2 flat)", trough(4.0))
block("50 mm aerogel + 200 mm wool (k_eff 0.040, 250 mm)", trough(4.0), ins_mm=250.0, k_ins=0.0399)
block("  + recovery jacket returning 60% of store loss", trough(4.0), ins_mm=250.0, k_ins=0.0399, jacket=0.6)
block("  + jacket + 2 m2 flat collector", trough(4.0), ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)
block("150 mm wool + jacket 60% + 2 m2 flat", trough(4.0), jacket=0.6, n_W=1.0)

sec("5. UNIFORM HAZE instead of broken cloud (dust): beam dimmed all day")
block("A. fixed CPC", CPC, broken_cloud=False)
block("B. trough 4 m2", trough(4.0), broken_cloud=False)

sec("6. OPTION B: tracker availability (days lost per week to a stuck drive)")
for lost, cl in ((1, [1,1,1,0.0,1,1,1]), (2, [1,0.0,1,1,0.0,1,1])):
    r = run(cfg(trough(4.0), cl, 'summer')); line(f"clear summer week, {lost} day(s) without tracking", r)

# daily energy picture, B 4 m2, clear summer day, v2 build
r = run(cfg(trough(4.0), CLEAR, 'summer', ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)); a = r['raw']; d = 7
print(f"\nB 4 m2, v2 build, clear summer day (kWh): collected {r['coll']:.2f} | rejected by defocus {r['dump']:.2f} | "
      f"store loss {r['loss']:.2f} (jacket recovers {r['jacket']:.2f}) | stew+morning {a['cook_del']/d:.2f} | kisra {a['hl_del']['kisra']/d:.2f} | "
      f"oven {a['hl_del']['oven']/d:.2f} | cascade {r['casc']:.2f} | flat collector {a['coll_W']/d:.2f}")
print(f"store: usable {r['usable']:.2f} kWh, G {r['G']:.3f} W/K = {r['G']*195:.0f} W at 230/35 C")
