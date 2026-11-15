#!/usr/bin/env python3
"""Option B (tracked trough) on the archived AeroBooster model.

The archived model file is loaded unchanged and patched in memory in four places only:
  1. the concentrating branch K may have its own irradiance (tracked direct beam),
  2. its own efficiency coefficients (so the flat water branch keeps the archived ones),
  3. a duty factor for broken cloud (beam is on or off, not uniformly dimmed),
  4. an optional recovery jacket returning a fraction of the store's standby loss to the tank.
With none of the new keys set, the patched model is identical to the archived one (checked).

Revision C.3 notes (November 2026):
  - Realistic insulation: 200 mm rock wool (k≈0.055) gives G≈0.49 W/K for a 30 L store.
    The earlier G=0.289 W/K requires ~100 mm microporous insulation at $12,000/m³.
    For 45 L store (C-PV): G≈0.49 W/K with 200 mm rock wool.
  - Dual-window thresholds revised: thrHi=245 °C, thrLo=140 °C (from 215/200).
  - Water collector critical: without 2 m² flat collector, bake service collapses.
  - PV route (C-PV): 6.5 m² PV (≈1.4 kWp) for home with realistic insulation.
  - Tea from tank option: tea_from_tank=True serves tea from water store, not salt store.
"""
import importlib.util, math, sys, types

import os
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aerobooster_oven_heating.py")
src = open(SRC, encoding="utf-8").read()
spec = importlib.util.spec_from_file_location("orig", SRC)
orig = importlib.util.module_from_spec(spec); spec.loader.exec_module(orig)

a1 = """        if G > 0.0 and b['A_K'] > 0.0:
            T_mean = 0.5 * (T_b + min(T_b + 20.0, p['T_oil_max']))
            if T_mean > p['T_amb'] + p['dT_on'] or T_b < b['T_max']:
                e = eta(p, T_mean, G, p['C_K'], p['eta_opt_K'])
                Q_K = b['A_K'] * G * e"""
b1 = """        G_K, duty = irr_K(p, t_h, day, G)
        if G_K > 0.0 and b['A_K'] > 0.0:
            if 'abs_offset' in p: T_mean = T_b + p['abs_offset']
            else: T_mean = 0.5 * (T_b + min(T_b + 20.0, p['T_oil_max']))
            if T_mean > p['T_amb'] + p['dT_on'] or T_b < b['T_max']:
                e = eta_K(p, T_mean, G_K)
                Q_K = b['A_K'] * G_K * e * duty"""
a2 = """        if counting:
            acc['loss_b'] += L_b * dth; acc['loss_t'] += L_t * dth"""
b2 = """        jk = p.get('jacket', 0.0)
        if jk > 0.0 and T_t < p['T_tank_max']:
            T_t += jk * L_b * dth / (p['V_tank'] * CPW)
            if counting: acc['jacket'] = acc.get('jacket', 0.0) + jk * L_b * dth
        if counting:
            acc['loss_b'] += L_b * dth; acc['loss_t'] += L_t * dth"""
assert src.count(a1) == 1 and src.count(a2) == 1
mod = types.ModuleType("patched")

def erbs(kt):
    if kt <= 0.22: return 1.0 - 0.09 * kt
    if kt <= 0.80: return 0.9511 - 0.1604*kt + 4.388*kt**2 - 16.638*kt**3 + 12.336*kt**4
    return 0.165
KT = 0.72
BEAM_CLEAR = 1.0 - erbs(KT)                       # 0.785 of global is beam on a clear day

def sunny_share(c):
    """Share of a day's clear-sky beam that survives cloud factor c (Erbs)."""
    return c * (1.0 - erbs(KT * c)) / BEAM_CLEAR

def irr_K(p, t_h, day, G):
    """Irradiance seen by the concentrating branch, and the duty factor."""
    mode = p.get('K_mode')
    if mode is None:
        return G, 1.0                               # archived behaviour
    cl = p['cloud'][day % len(p['cloud'])]
    duty = sunny_share(cl) if p.get('broken_cloud', True) else 1.0
    if t_h <= p['sunrise'] or t_h >= p['sunset']:
        return 0.0, duty
    x = (t_h - p['sunrise']) / (p['sunset'] - p['sunrise'])
    if mode == 'cpc':                               # fixed CPC: all beam + 1/C of diffuse, clear-sky level
        Gc = p['G_peak'] * math.sin(math.pi * x)
        f = BEAM_CLEAR + (1.0 - BEAM_CLEAR) / p['K']['C']
        if not p.get('broken_cloud', True):         # uniform haze instead
            fd = erbs(KT * cl); f = (1.0 - fd) + fd / p['K']['C']; Gc *= cl
        return Gc * f, duty
    if mode == 'trk':                               # tracked trough: direct beam only
        alt_n = math.radians(p['alt_noon'])
        s = math.sin(math.pi * x) * math.sin(alt_n)
        if s < math.sin(math.radians(p.get('min_alt', 15.0))):
            return 0.0, duty
        taper = 0.7 ** ((1.0 / s) ** 0.678) / 0.7 ** ((1.0 / math.sin(alt_n)) ** 0.678)
        dni = p['G_peak'] * BEAM_CLEAR * taper * p.get('inc', 1.0)   # inc = cos(incidence) of a polar-axis trough = cos(declination)
        if not p.get('broken_cloud', True):
            dni *= sunny_share(cl)
        return dni, duty
    raise ValueError(mode)

def eta_K(p, T_mean, G):
    if 'K' not in p:
        return mod.eta(p, T_mean, G, p['C_K'], p['eta_opt_K'])
    k = p['K']; dT = T_mean - p['T_amb']
    e = k['eta0'] - (k['a1'] / k['C']) * dT / (G * 1000.0) - (k['a2'] / k['C']) * dT * dT / (G * 1000.0)
    return max(e, 0.0) * k.get('pipe', 0.95)

mod.__dict__.update(irr_K=irr_K, eta_K=eta_K)
a3 = "        Q_K_gross = Q_K\n"
b3 = "        Q_K += p.get('A_pv', 0.0) * G * p.get('eta_pv', 0.172)   # optional PV panel feeding a resistance heater in the store\n        Q_K_gross = Q_K\n"
assert src.count(a3) == 1
exec(compile(src.replace(a1, b1).replace(a2, b2).replace(a3, b3), "patched", "exec"), mod.__dict__)

A = orig.A_PANEL
POOR=[0.8,0.6,0.5,0.7,0.6,0.8,0.7]; TWO=[1.0,0.55,1.0,0.45,1.0,1.0,1.0]; ONE=[1.0,1.0,0.55,1.0,1.0,1.0,1.0]; CLEAR=[1.0]*7
LOADS=[("kisra",0.73,17.0,1.2,215.0,2.0,[1]*7), ("oven",0.54,12.0,1.6,235.0,4.0,[1,0,1,0,1,0,0])]

def base(**kw):
    p = dict(orig.BASE)
    p.update(n_W=0.25, pump_W=False, pump_K=True, retention_saving=0.30, ins_mm=150.0, k_ins=0.050,
             tail_full_margin=40, tail_window=(8.0, 20.0), V_tank=120.0, meal_kWh=0.80, hot_loads=LOADS,
             C_K=1.94, eta_opt_K=0.84**0.9)
    p.update(kw); return p

# ---- collectors
CPC = dict(mode='cpc', area=3*3*0.3529*1.76, K=dict(eta0=0.70*0.84**0.9, a1=1.25, a2=0.0048, C=1.94, pipe=0.95))
def trough(area=4.0, eta0=0.55, a1=6.6, a2=0.016, C=12.0, pipe=0.95):
    return dict(mode='trk', area=area, K=dict(eta0=eta0, a1=a1, a2=a2, C=C, pipe=pipe))

def cfg(coll, cloud, season='summer', heat=2.5, **kw):
    p = base(cloud=cloud, K_mode=coll['mode'], K=dict(coll['K']), n_K=coll['area']/A)
    if coll['mode'] == 'trk':
        p.update(abs_offset=35.0, alt_noon=80.0 if season == 'summer' else 51.0)
    if season == 'summer':
        p.update(night_kWh=0.30)
    else:
        p.update(G_peak=0.80, sunrise=7.0, sunset=17.0, T_amb=20.0, T_cold=18.0,
                 night_kWh=0.0 if heat else 0.30, heat_kWh=heat, heat_start=20.0, heat_hours=9.0, P_heat=0.5)
    p.update(kw); return p

# ---- C.3 insulation presets (for convenience in runB7.py)
# Home 30L store:
#   Original RevB: 50mm aerogel + 200mm wool -> G≈0.289 W/K  (needs microporous, unrealistic for this cost)
#   C.3 realistic: 200mm rock wool only (k≈0.055) -> G≈0.49 W/K
#   C.3 with aerogel: 20mm aerogel + 200mm wool -> G≈0.37 W/K (still expensive)
INS_REVB     = dict(ins_mm=250.0, k_ins=0.0399)        # original RevB: 50 aerogel + 200 wool
INS_C3_REAL  = dict(ins_mm=200.0, k_ins=0.055)         # C.3 realistic: 200mm rock wool only
INS_C3_AER20 = dict(ins_mm=220.0, k_ins=0.045)         # C.3 compromise: 20mm aerogel + 200mm wool

# Home 45L store (C-PV path):
#   200mm rock wool -> G≈0.49 W/K (same conductance, larger surface but thicker relative)
INS_CPV_REAL = dict(ins_mm=200.0, k_ins=0.055)         # for 45L store

# Dual-window thresholds (C.3 revision):
#   thrHi=245 (was 215 in RevB), thrLo=140 (was 200), gate 08-20, ΔT 15K, tank max 75°C
DW_C3 = dict(tail_full_margin=10, T_thr_hi=245.0)      # keys depend on archived model's parameter names

def run(p, L=97.0):
    mod.MEDIA['salt']['L_fus'] = L
    a = mod.simulate(p); d = a['days_counted']
    return dict(stew=f"{a['meal_ok']}/7", kisra=f"{a['hl_ok']['kisra']}/7", oven=f"{a['hl_ok']['oven']}/3",
                light=f"{a['light_ok']}/7", tea=f"{a['tea_ok']}/70",
                heat=(f"{a['heat_ok']}/7" if a['heat_try'] else "-"),
                coll=a['coll_K']/d, dump=a['dump_K']/d, loss=a['loss_b']/d, peak=a['T_bank_max'],
                casc=a['tail']/d, jacket=a.get('jacket', 0.0)/d, G=a['G_bank'], usable=a['usable'], raw=a)

HDR = f"  {'case':<50}{'stew':>6}{'kisra':>7}{'oven':>6}{'light':>7}{'tea':>8}{'heat':>6}{'coll':>7}{'dump':>6}{'loss':>6}{'peak':>6}"
def line(lab, r):
    print(f"  {lab:<50}{r['stew']:>6}{r['kisra']:>7}{r['oven']:>6}{r['light']:>7}{r['tea']:>8}{r['heat']:>6}"
          f"{r['coll']:>7.2f}{r['dump']:>6.2f}{r['loss']:>6.2f}{r['peak']:>6.0f}")
def sec(t): print("\n" + "=" * 118); print(t); print("=" * 118); print(HDR)
WEEKS = [("summer clear", CLEAR, 'summer'), ("summer one dull day", ONE, 'summer'), ("summer two dull days", TWO, 'summer'),
         ("summer poor week", POOR, 'summer'), ("winter clear + heating", CLEAR, 'winter'), ("winter poor + heating", POOR, 'winter')]
def block(title, coll, **kw):
    print(f"-- {title}")
    out = []
    for lab, cl, s in WEEKS:
        r = run(cfg(coll, cl, s, **kw)); line(lab, r); out.append(r)
    return out
