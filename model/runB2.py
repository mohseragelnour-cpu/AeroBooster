import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *
V2 = dict(ins_mm=250.0, k_ins=0.0399, jacket=0.6, n_W=1.0)     # v2 store build + 2 m2 flat collector
capsec = dict(eta0=0.58, a1=6.6*0.85, a2=0.016*0.85)

sec("7. RECOMMENDED OPTION B: two 3 m2 troughs = 6 m2, steel absorber, selective, glass envelope")
block("6 m2, plain receiver, filed store build", trough(6.0))
block("6 m2, insulated cap + secondary reflector, filed store build", trough(6.0, **capsec))
block("6 m2, cap + secondary, v2 store build (aerogel+wool, jacket, 2 m2 flat)", trough(6.0, **capsec), **V2)
block("5 m2, cap + secondary, v2 store build", trough(5.0, **capsec), **V2)
block("4 m2, cap + secondary, v2 store build", trough(4.0, **capsec), **V2)

sec("8. OPTION A on the same v2 store build, for a like-for-like comparison")
block("A. fixed CPC 5.59 m2, v2 store build", CPC, **V2)

sec("9. EVACUATED all-glass tube as trough receiver, 4 m2: how fragile is the good result?")
ev = dict(eta0=0.60, a1=0.28, a2=0.009, C=10.8)
block("as certified tubes, absorber 35 K above store", trough(4.0, **ev))
block("absorber 70 K above store (poor heat extraction at 10x flux)", trough(4.0, **ev), abs_offset=70.0)
block("tube losses 3x certified", trough(4.0, eta0=0.60, a1=0.84, a2=0.027, C=10.8))
block("both: 70 K and 3x losses", trough(4.0, eta0=0.60, a1=0.84, a2=0.027, C=10.8), abs_offset=70.0)

sec("10. UNIFORM HAZE (dust), recommended B versus A, v2 store build")
block("A. fixed CPC", CPC, broken_cloud=False, **V2)
block("B. 6 m2 cap + secondary", trough(6.0, **capsec), broken_cloud=False, **V2)

sec("11. B 6 m2 cap+secondary, v2 build: what if the selective coating fails or optics are poor")
block("coating emittance doubled (a2 x2)", trough(6.0, eta0=0.58, a1=6.6*0.85, a2=0.032*0.85), **V2)
block("optical 0.48", trough(6.0, eta0=0.48, a1=6.6*0.85, a2=0.016*0.85), **V2)

r = run(cfg(trough(6.0, **capsec), CLEAR, 'summer', **V2)); a = r['raw']; d = 7
print(f"\nRecommended B, clear summer day (kWh): collected {r['coll']:.2f} | rejected by turning off-sun {r['dump']:.2f} | "
      f"store loss {r['loss']:.2f} of which jacket recovers {r['jacket']:.2f} | stew+morning meal {a['cook_del']/d:.2f} | "
      f"kisra {a['hl_del']['kisra']/d:.2f} | oven {a['hl_del']['oven']/d:.2f} | cascade to water {r['casc']:.2f} | flat collector {a['coll_W']/d:.2f} | tea {a['tea_del']/d:.2f}")
r = run(cfg(trough(6.0, **capsec), CLEAR, 'winter', **V2)); a = r['raw']
print(f"Recommended B, clear winter day (kWh): collected {r['coll']:.2f} | rejected {r['dump']:.2f} | store loss {r['loss']:.2f} | "
      f"stew+morning {a['cook_del']/d:.2f} | kisra {a['hl_del']['kisra']/d:.2f} | cascade {r['casc']:.2f} | heating {a['heat_del']/d:.2f} | flat {a['coll_W']/d:.2f}")

print("\n--- hand calculations ---")
# solid rod
k=390.0; L=1.9; q=1.6*0.746*1000*0.55      # W per m of trough absorbed
for dmm in (20,30,40,60):
    Acs=math.pi*(dmm/1000)**2/4
    for dT in (150,):
        Q=2*k*Acs*dT/L
        print(f"solid copper rod {dmm} mm, {L} m, heated along its length, {dT} K end-to-end: carries {Q:6.1f} W of {q*L:6.0f} W absorbed ({100*Q/(q*L):.1f} %)")
Acs=q*L*L/(2*k*150); dn=math.sqrt(4*Acs/math.pi)
print(f"copper rod needed to carry it all with 150 K: diameter {dn*1000:.0f} mm, mass {Acs*L*8960:.0f} kg")
# thermosyphon flooding limit, Dowtherm A, Tien-Chung
def flood(T, P_bar, hfg, sigma, rhol, d=0.036):
    rhov=P_bar*1e5*0.166/(8.314*(T+273.15)); A=math.pi*d*d/4
    Bo=d*math.sqrt(9.81*(rhol-rhov)/sigma); Ku=3.2*math.tanh(0.5*Bo**0.25)**2
    Q=Ku*hfg*A*(sigma*9.81*(rhol-rhov))**0.25*(rhov**-0.25+rhol**-0.25)**-2
    return rhov,Ku,Q
for T,P,h,s,rl in ((200,0.24,320e3,0.021,900),(250,0.85,300e3,0.017,860),(282,1.70,285e3,0.014,820),(316,3.12,265e3,0.011,780)):
    rv,Ku,Q=flood(T,P,h,s,rl)
    print(f"thermosyphon 36 mm bore, Dowtherm A at {T} C ({P} bar): vapour {rv:.2f} kg/m3, flooding limit {Q/1000:.2f} kW vertical")
print(f"per 3 m2 trough: absorbed at noon {3*0.746*0.58:.2f} kW")
# receiver stagnation, steel selective non-evacuated, C=12
for C,e0 in ((12,0.58),):
    S=e0*900*C; a1=6.6*0.85; a2=0.016*0.85
    dT=(-a1+math.sqrt(a1*a1+4*a2*S))/(2*a2); print(f"stagnation of steel receiver in focus at 0.9 kW/m2: {dT+35:.0f} C")
# lens strip
for w in (0.058,0.15,0.30):
    print(f"lens strip {w*1000:.0f} mm wide above the tube: adds {w*0.88*0.92:.3f}, removes {max(w-0.058,0)*0.84*0.90*0.92*0.85+0.0:.3f} m of effective width per m (mirror it shades); net {w*0.88*0.92-0.058*0.92-max(w-0.058,0)*0.84*0.90*0.92*0.85:+.3f} m of 1.6 m")
# time to drift out of focus
acc=math.degrees(math.atan(0.021/0.8))
print(f"half acceptance of 42 mm absorber seen from rim at 0.8 m: +/-{acc:.1f} deg -> sun leaves focus {acc/15*60:.0f} min after tracking stops")
