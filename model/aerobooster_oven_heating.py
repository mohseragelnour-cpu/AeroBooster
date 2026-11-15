#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Three AeroBooster model variants, computed on one two-branch architecture.

  A  baseline   - what we converged on: 3 flat ETC, one pumped oil loop, salt bank
  B  expired-IP - split loops: thermosyphon water branch + CPC/oil cooking branch
                  (Winston CPC US4387961, expired 2000), heat-retention cooking
  C  maximal    - B plus bought-in in-force-patent products: aerogel/VIP insulation,
                  better selective absorber, encapsulated PCM in the water tank

Two-branch physics. Branch W serves <95 C loads, branch K serves the 200-260 C bank.
Collector efficiency referred to APERTURE area:
    eta = eta0*eta_opt - (a1/C)*dT/G - (a2/C)*dT^2/G
For C=1 (flat) this reduces to the first-order model used in v2-v4.
A concentrator divides the loss terms by C because losses scale with absorber area
while gain scales with aperture area. That is why a CPC helps a hot branch and
hurts a cold one.

ALL PARAMETERS ARE ESTIMATES. Calibrate against the experiment workbooks.
"""
import math

A_PANEL = 1.76 * 1.13          # 1.9888 m2, standard PV-module footprint

MEDIA = dict(
    salt=dict(rho=1.90, cp_s=1.40, cp_l=1.50, L_fus=110.0, T_melt=225.0,
              dT_melt=10.0, fill=0.90, steel_frac=0.20, T_max=255.0),
    packed=dict(rho=2.45, cp_s=0.90, cp_l=0.95, L_fus=24.0, T_melt=225.0,
                dT_melt=10.0, fill=0.95, steel_frac=0.10, T_max=258.0),
)

BASE = dict(
    # site: Sudan, high DNI
    G_peak=0.95, T_amb=35.0, sunrise=6.0, sunset=18.0, cloud=[1.0]*7,
    # collector, flat evacuated tube referred to aperture
    eta0=0.70, a1=1.25, a2=0.0048, pipe_eff=0.95,
    # branch split
    n_W=0, n_K=3, C_W=1.0, C_K=1.0, eta_opt_W=1.0, eta_opt_K=1.0,
    pump_W=True, pump_K=True,
    # oil loop limits
    T_oil_max=260.0, dT_on=8.0, dT_off=3.0,
    # salt bank
    medium="salt", V_store=30.0, T_bank_min=200.0,
    ins_mm=100.0, k_ins=0.030, bridge=1.15, h_out=10.0, cp_steel=0.50,
    # water tank
    V_tank=30.0, cp_w=4.184, UA_tank60=0.70, T_tank_max=95.0, T_cold=28.0,
    pcm_tank_kWh=0.0,                      # encapsulated PCM buffer in the tank
    # cascade: bank tail heat into the water tank
    P_tail=1.0, eta_tail=0.90, dT_tail_min=15.0, T_tail_max=90.0,
    T_tail_floor=0.0,   # tail cascade stops here, reserving the bank for morning
    tail_window=(0.0, 24.0),   # hours in which the TAIL window may open
    # demand
    meal_kWh=1.50, meal_start=18.0, P_meal=1.5,
    # household oven: needs the bank ABOVE a floor to reach baking temperature
    oven_kWh=0.0, oven_start=9.0, P_oven=1.6, T_oven_min=235.0, oven_days=[1]*7,
    # generalised hot loads drawn from the bank, each with its own floor:
    # (name, kWh, start hour, kW, bank floor C, window h, days mask)
    hot_loads=[],
    # winter space heating: drawn from the water tank over several hours
    heat_kWh=0.0, heat_start=20.0, heat_hours=8.0, P_heat=1.0, T_heat_min=45.0,
    light_kWh=0.40, light_start=7.0, P_light=1.0,
    night_kWh=0.30, night_start=21.0, P_night=0.8,
    tea_hours=[6, 8, 10, 12, 14, 15, 17, 19, 20, 22], tea_litres=0.5, T_tea=95.0,
    tea_ok_tank=80.0,
    retention_saving=0.0,                  # heat-retention cooking, fraction of meal energy
    # run
    days=21, warmup=14, dt=10.0,
)


def irradiance(p, t_h, day=0):
    if t_h <= p['sunrise'] or t_h >= p['sunset']:
        return 0.0
    x = (t_h - p['sunrise']) / (p['sunset'] - p['sunrise'])
    cl = p['cloud'][day % len(p['cloud'])]
    return p['G_peak'] * math.sin(math.pi * x) * cl


def eta(p, T_mean, G, C, eta_opt):
    """Aperture-referred efficiency. Loss terms divided by the concentration ratio."""
    if G <= 0.0:
        return 0.0
    dT = T_mean - p['T_amb']
    e = p['eta0'] * eta_opt - (p['a1'] / C) * dT / (G * 1000.0) \
        - (p['a2'] / C) * dT * dT / (G * 1000.0)
    return max(e, 0.0) * p['pipe_eff']


def build(p):
    med = MEDIA[p['medium']]
    m = p['V_store'] * med['rho'] * med['fill']
    m_st = med['steel_frac'] * m
    C_s = m * med['cp_s'] + m_st * p['cp_steel']
    C_l = m * med['cp_l'] + m_st * p['cp_steel']
    E_lat = m * med['L_fus']
    T1 = med['T_melt'] - med['dT_melt'] / 2.0
    T2 = med['T_melt'] + med['dT_melt'] / 2.0
    E1 = C_s * (T1 - 25.0)
    E2 = E1 + E_lat + 0.5 * (C_s + C_l) * med['dT_melt']

    def T_of_E(E):
        if E <= E1: return 25.0 + E / C_s
        if E >= E2: return T2 + (E - E2) / C_l
        return T1 + (E - E1) / (E2 - E1) * med['dT_melt']

    def E_of_T(T):
        if T <= T1: return C_s * (T - 25.0)
        if T >= T2: return E2 + C_l * (T - T2)
        return E1 + (T - T1) / med['dT_melt'] * (E2 - E1)

    t = p['ins_mm'] / 1000.0
    s = (p['V_store'] / med['fill'] / 1000.0) ** (1.0 / 3.0)
    a_in, a_out = 6 * s * s, 6 * (s + 2 * t) ** 2
    G_bank = 1.0 / (1.0 / (p['bridge'] * p['k_ins'] * math.sqrt(a_in * a_out) / t)
                    + 1.0 / (p['h_out'] * a_out))
    UA_tank = p['UA_tank60'] * (p['V_tank'] / 60.0) ** (2.0 / 3.0)
    usable = (E_of_T(med['T_max']) - E_of_T(p['T_bank_min'])) / 3600.0
    return dict(med=med, T_of_E=T_of_E, E_of_T=E_of_T, G_bank=G_bank,
                UA_tank=UA_tank, usable=usable, T_max=med['T_max'],
                A_W=A_PANEL * p['n_W'], A_K=A_PANEL * p['n_K'])


def simulate(p):
    b = build(p)
    dt, dth = p['dt'], p['dt'] / 3600.0
    CPW = p['cp_w'] / 3600.0                      # kWh per litre per K
    E_b = b['E_of_T'](p['T_amb'] + 5.0)
    T_t = 45.0
    E_pcm = 0.0
    E_b_start = None; T_t_start = None
    meal_left = light_left = night_left = oven_left = heat_left = 0.0
    oven_active = False; heat_active = False
    HL = list(p.get('hot_loads', []))
    hl_left = [0.0]*len(HL); hl_on = [False]*len(HL)
    acc = dict(coll_W=0.0, coll_K=0.0, dump_K=0.0, dump_W=0.0, loss_b=0.0,
               loss_t=0.0, meal_ok=0, meal_try=0, light_ok=0, light_try=0,
               night_ok=0, night_try=0, tea_ok=0, tea_try=0, cook_del=0.0,
               tail=0.0, tea_del=0.0, pump_Wh=0.0, T_bank_max=0.0, T_bank_end=0.0,
               clamp=0.0, tea_over=0.0, night_del=0.0, E_b0=0.0, T_t0=0.0,
               oven_ok=0, oven_try=0, oven_del=0.0, oven_blocked=0,
               heat_ok=0, heat_try=0, heat_del=0.0,
               hl_ok={h[0]: 0 for h in HL}, hl_try={h[0]: 0 for h in HL},
               hl_del={h[0]: 0.0 for h in HL})
    meal_short = light_short = night_short = 0.0

    n_steps = int(p['days'] * 24 * 3600 / dt)
    for i in range(n_steps):
        t_abs = i * dth
        day = int(t_abs // 24)
        t_h = t_abs - 24 * day
        counting = day >= p['warmup']
        if counting and E_b_start is None:
            E_b_start = E_b; T_t_start = T_t
        G = irradiance(p, t_h, day)
        T_b = b['T_of_E'](E_b)
        if counting:
            acc['T_bank_max'] = max(acc['T_bank_max'], T_b)

        # ---------------- collection, cooking branch K -> salt bank
        Q_K = 0.0
        if G > 0.0 and b['A_K'] > 0.0:
            T_mean = 0.5 * (T_b + min(T_b + 20.0, p['T_oil_max']))
            if T_mean > p['T_amb'] + p['dT_on'] or T_b < b['T_max']:
                e = eta(p, T_mean, G, p['C_K'], p['eta_opt_K'])
                Q_K = b['A_K'] * G * e
        Q_K_gross = Q_K
        if T_b >= b['T_max'] and Q_K > 0.0:
            if counting: acc['dump_K'] += Q_K * dth
            Q_K = 0.0
        E_b += Q_K * 3600.0 * dth
        if counting and Q_K_gross > 0.0:
            acc['coll_K'] += Q_K_gross * dth
            if p['pump_K'] and Q_K > 0.0: acc['pump_Wh'] += 45.0 * dth

        # ---------------- collection, water branch W -> water tank
        Q_W = 0.0
        if G > 0.0 and b['A_W'] > 0.0:
            T_mean = 0.5 * (T_t + min(T_t + 12.0, p['T_tank_max']))
            e = eta(p, T_mean, G, p['C_W'], p['eta_opt_W'])
            Q_W = b['A_W'] * G * e
        if Q_W > 0.0:
            head = (p['T_tank_max'] - T_t) * p['V_tank'] * CPW
            add = min(Q_W * dth, max(head, 0.0))
            T_t += add / (p['V_tank'] * CPW)
            spill = Q_W * dth - add
            if p['pcm_tank_kWh'] > 0.0 and spill > 0.0:
                room = p['pcm_tank_kWh'] - E_pcm
                take = min(spill, max(room, 0.0))
                E_pcm += take; spill -= take
            if counting:
                acc['coll_W'] += Q_W * dth
                acc['dump_W'] += spill
                if p['pump_W']: acc['pump_Wh'] += 25.0 * dth

        # ---------------- cascade: bank tail heat into the tank
        near_full = T_b > b['T_max'] - p.get('tail_full_margin', 10.0)
        tw = p.get('tail_window', (0.0, 24.0))
        tail_heat = ((T_b < p['T_bank_min']) and (T_b > p.get('T_tail_floor', 0.0))
                     and (tw[0] <= t_h < tw[1]))
        if (T_b > T_t + p['dT_tail_min'] and T_t < p['T_tail_max']
                and (near_full or tail_heat)):
            Q = min(p['P_tail'], (p['T_tail_max'] - T_t) * p['V_tank'] * CPW / dth)
            if Q > 0.0:
                E_b -= Q * 3600.0 * dth
                T_t += Q * p['eta_tail'] * dth / (p['V_tank'] * CPW)
                if counting: acc['tail'] += Q * p['eta_tail'] * dth

        # ---------------- PCM buffer gives back when the tank falls
        if E_pcm > 0.0 and T_t < p['T_tank_max'] - 5.0:
            room = (p['T_tank_max'] - 5.0 - T_t) * p['V_tank'] * CPW
            give = min(E_pcm, room, 0.5 * dth)
            T_t += give / (p['V_tank'] * CPW); E_pcm -= give

        # ---------------- demand: start events
        def starts(hr):
            return t_h >= hr and t_h - dth < hr
        if starts(p['meal_start']):
            meal_left = p['meal_kWh'] * (1.0 - p['retention_saving'])
            if counting: acc['meal_try'] += 1
        if starts(p['light_start']) and p['light_kWh'] > 0.0:
            light_left = p['light_kWh']
            if counting: acc['light_try'] += 1
        if starts(p['night_start']) and p['night_kWh'] > 0.0:
            night_left = p['night_kWh']
            if counting: acc['night_try'] += 1
        if starts(p['oven_start']) and p['oven_kWh'] > 0.0 \
                and p['oven_days'][day % len(p['oven_days'])]:
            oven_left = p['oven_kWh']; oven_active = True
            if counting: acc['oven_try'] += 1
        if starts(p['heat_start']) and p['heat_kWh'] > 0.0:
            heat_left = p['heat_kWh']; heat_active = True
            if counting: acc['heat_try'] += 1

        # meal and light heating draw from the bank
        for key, left_name, P_key in (('meal', 'meal_left', 'P_meal'),
                                      ('light', 'light_left', 'P_light')):
            left = {'meal_left': meal_left, 'light_left': light_left}[left_name]
            if left > 0.0:
                T_b = b['T_of_E'](E_b)
                avail = max(E_b - b['E_of_T'](150.0), 0.0) / 3600.0
                Q = min(p[P_key] * dth, left, avail)
                if Q > 0.0:
                    E_b -= Q * 3600.0
                    left -= Q
                    if counting: acc['cook_del'] += Q
                if left_name == 'meal_left': meal_left = left
                else: light_left = left

        # generalised hot loads
        for j, (nm, kwh, hr0, pw, floor, win, days) in enumerate(HL):
            if starts(hr0) and days[day % len(days)]:
                hl_left[j] = kwh; hl_on[j] = True
                if counting: acc['hl_try'][nm] += 1
            if hl_left[j] > 0.0:
                T_b = b['T_of_E'](E_b)
                if T_b >= floor:
                    avail = max(E_b - b['E_of_T'](floor), 0.0) / 3600.0
                    Q = min(pw * dth, hl_left[j], avail)
                    if Q > 0.0:
                        E_b -= Q * 3600.0; hl_left[j] -= Q
                        if counting: acc['hl_del'][nm] += Q
            if starts((hr0 + win) % 24.0) and hl_on[j]:
                if hl_left[j] <= 1e-6 and counting: acc['hl_ok'][nm] += 1
                hl_left[j] = 0.0; hl_on[j] = False

        # oven draws from the bank, but ONLY above the baking temperature floor
        if oven_left > 0.0:
            T_b = b['T_of_E'](E_b)
            if T_b >= p['T_oven_min']:
                avail = max(E_b - b['E_of_T'](p['T_oven_min']), 0.0) / 3600.0
                Q = min(p['P_oven'] * dth, oven_left, avail)
                if Q > 0.0:
                    E_b -= Q * 3600.0
                    oven_left -= Q
                    if counting: acc['oven_del'] += Q

        # space heating draws from the water tank over a long window
        if heat_left > 0.0:
            avail = max((T_t - p['T_heat_min']) * p['V_tank'] * CPW, 0.0)
            Q = min(p['P_heat'] * dth, heat_left, avail)
            if Q > 0.0:
                T_t -= Q / (p['V_tank'] * CPW); heat_left -= Q
                if counting: acc['heat_del'] += Q

        # night warming draws from the water tank
        if night_left > 0.0:
            avail = max((T_t - 50.0) * p['V_tank'] * CPW, 0.0)
            Q = min(p['P_night'] * dth, night_left, avail)
            if Q > 0.0:
                T_t -= Q / (p['V_tank'] * CPW); night_left -= Q
                if counting: acc['night_del'] += Q

        # settle events at the end of their window
        if starts(p['meal_start'] + 2.0):
            if meal_left > 1e-6: meal_short += meal_left
            elif counting: acc['meal_ok'] += 1
            meal_left = 0.0
        if starts(p['light_start'] + 1.5):
            if light_left > 1e-6: light_short += light_left
            elif counting: acc['light_ok'] += 1
            light_left = 0.0
        if starts(p['oven_start'] + 4.0) and oven_active:
            if oven_left > 1e-6:
                if counting: acc['oven_blocked'] += 1
            elif counting: acc['oven_ok'] += 1
            oven_left = 0.0; oven_active = False
        if starts((p['heat_start'] + p['heat_hours']) % 24.0) and heat_active:
            if heat_left <= 1e-6 and counting: acc['heat_ok'] += 1
            heat_left = 0.0; heat_active = False
        if starts(p['night_start'] + 2.0):
            if night_left > 1e-6: night_short += night_left
            elif counting: acc['night_ok'] += 1
            night_left = 0.0

        # tea from the tank
        for hr in p['tea_hours']:
            if starts(hr):
                if counting: acc['tea_try'] += 1
                need = p['tea_litres'] * (p['T_tea'] - p['T_cold']) * CPW
                if T_t >= p['tea_ok_tank']:
                    draw = p['tea_litres'] * (T_t - p['T_cold']) * CPW
                    T_t -= draw / (p['V_tank'] * CPW)
                    if counting:
                        acc['tea_ok'] += 1; acc['tea_del'] += min(draw, need)
                        acc['tea_over'] += max(draw - need, 0.0)

        # ---------------- losses
        T_b = b['T_of_E'](E_b)
        L_b = b['G_bank'] * (T_b - p['T_amb']) / 1000.0
        E_b -= L_b * 3600.0 * dth
        L_t = b['UA_tank'] * (T_t - p['T_amb']) / 1000.0
        T_t -= L_t * dth / (p['V_tank'] * CPW)
        if counting:
            acc['loss_b'] += L_b * dth; acc['loss_t'] += L_t * dth
        if T_t < p['T_cold']:
            if counting: acc['clamp'] += (p['T_cold'] - T_t) * p['V_tank'] * CPW
            T_t = p['T_cold']

    acc['T_bank_end'] = b['T_of_E'](E_b)
    acc['dE_bank'] = (E_b - (E_b_start if E_b_start is not None else E_b)) / 3600.0
    acc['dE_tank'] = ((T_t - (T_t_start if T_t_start is not None else T_t))
                      * p['V_tank'] * CPW)
    acc['E_pcm_end'] = E_pcm
    acc['meal_short'] = meal_short; acc['light_short'] = light_short
    acc['night_short'] = night_short
    acc['usable'] = b['usable']; acc['A_W'] = b['A_W']; acc['A_K'] = b['A_K']
    acc['G_bank'] = b['G_bank']
    acc['days_counted'] = p['days'] - p['warmup']
    return acc


def report(name, p, a):
    d = a['days_counted']
    tot_in = a['coll_W'] + a['coll_K']
    print(f"\n{'='*74}\n{name}")
    print(f"{'='*74}")
    print(f"  aperture   water branch {a['A_W']:5.2f} m2 (C={p['C_W']:.1f})   "
          f"cooking branch {a['A_K']:5.2f} m2 (C={p['C_K']:.1f})")
    print(f"  bank       {p['V_store']:.0f} L {p['medium']}, usable {a['usable']:.2f} kWh, "
          f"insulation {p['ins_mm']:.0f} mm k={p['k_ins']:.3f}")
    print(f"  standby    G_bank {a['G_bank']:.3f} W/K  ->  "
          f"{a['G_bank']*(230-p['T_amb']):.1f} W at 230 C")
    print(f"  collected  {tot_in/d:6.2f} kWh/day  (water {a['coll_W']/d:5.2f}, "
          f"cooking {a['coll_K']/d:5.2f})")
    print(f"  dumped     {(a['dump_K']+a['dump_W'])/d:6.2f} kWh/day  "
          f"({100*(a['dump_K']+a['dump_W'])/max(tot_in,1e-9):4.1f}% of collection)")
    print(f"  losses     bank {a['loss_b']/d:5.2f}  tank {a['loss_t']/d:5.2f} kWh/day")
    print(f"  delivered  cooking {a['cook_del']/d:5.2f}  cascade {a['tail']/d:5.2f}  "
          f"tea {a['tea_del']/d:5.2f} kWh/day")
    print(f"  MEALS      {a['meal_ok']}/{a['meal_try']}   "
          f"light {a['light_ok']}/{a['light_try']}   night {a['night_ok']}/{a['night_try']}"
          f"   tea {a['tea_ok']}/{a['tea_try']}")
    if a['meal_short'] > 1e-6:
        print(f"  shortfall  meals {a['meal_short']:.2f} kWh, light {a['light_short']:.2f}, "
              f"night {a['night_short']:.2f}")
    print(f"  bank T     peak {a['T_bank_max']:.1f} C   end {a['T_bank_end']:.1f} C")
    print(f"  pump       {a['pump_Wh']/d:.0f} Wh/day electrical")
    return a


def main():
    runs = []

    # ---------------- A: baseline, 3 flat panels, one pumped oil loop, tank from cascade
    A = dict(BASE)
    A.update(n_W=0.0, n_K=3, C_K=1.0, pump_W=False, pump_K=True)
    runs.append(("A  المرجعي", "MODEL A  baseline: 3 flat ETC, one pumped oil loop, tank fed by cascade", A))

    # ---------------- B: CPC on the cooking branch (Winston US4387961, expired 2000)
    #   the CPC is 1.54x more efficient at dT=200, so test dropping one panel
    B2 = dict(BASE)
    B2.update(n_W=0.25, n_K=2, C_W=1.0, C_K=2.0, eta_opt_K=0.85,
              pump_W=False, pump_K=True, retention_saving=0.30)
    runs.append(("B  المطور", "MODEL B  expired IP: 2 CPC panels (one panel REMOVED) + 0.5 panel thermosyphon "
                 "water branch + heat-retention cooking", B2))

    # B3: same but keeping three panels, to show the headroom CPC buys
    B3 = dict(B2); B3.update(n_K=3)
    runs.append(("B+ ثلاثة ألواح", "MODEL B+ same as B but keeping 3 CPC panels (headroom check)", B3))

    # ---------------- C: B plus bought-in products covered by in-force patents
    C = dict(B2)
    # aerogel blanket at 230 C mean is ~0.020-0.025 W/mK, not the 0.013 quoted at
    # ambient. Vacuum insulation panels are NOT usable here: most are rated <100 C.
    C.update(k_ins=0.022, ins_mm=60.0, eta0=0.75, a1=1.05, a2=0.0040,
             pcm_tank_kWh=1.20)
    runs.append(("C  الأقصى", "MODEL C  maximal: B + aerogel/VIP insulation + modern selective absorber "
                 "+ encapsulated PCM in the tank (all BOUGHT: no licence needed)", C))

    # C-: can C drop to a single CPC panel?
    C1 = dict(C); C1.update(n_K=1)
    runs.append(("C- لوح واحد", "MODEL C-  C with only ONE CPC panel on the cooking branch", C1))

    out = []
    for tag, title, p in runs:
        a = simulate(p)
        report(title, p, a)
        out.append((tag, p, a))

    # ---------------- energy balance
    print(f"\n{'='*78}\nENERGY BALANCE (all terms now tracked; residual should be near zero)\n{'='*78}")
    print(f"  {'model':<16}{'in':>8}{'used':>8}{'loss':>8}{'dump':>8}{'stored':>8}{'resid':>8}")
    for tag, p, a in out:
        d = a['days_counted']
        inp = a['coll_W'] + a['coll_K'] + a['clamp']
        used = a['cook_del'] + a['tea_del'] + a['tea_over'] + a['night_del']
        loss = a['loss_b'] + a['loss_t']
        dump = a['dump_K'] + a['dump_W']
        store = a['dE_bank'] + a['dE_tank'] + a['E_pcm_end']
        res = inp - (used + loss + dump + store)
        print(f"  {tag:<16}{inp/d:8.2f}{used/d:8.2f}{loss/d:8.2f}{dump/d:8.2f}"
              f"{store/d:8.2f}{100*res/max(inp,1e-9):7.1f}%")

    # ---------------- headline comparison
    print(f"\n{'='*78}\nCOMPARISON\n{'='*78}")
    print(f"  {'model':<16}{'panels':>8}{'aperture':>10}{'meals':>8}{'tea':>8}"
          f"{'standby':>10}{'dump%':>8}{'pump':>8}")
    print(f"  {'':<16}{'':>8}{'m2':>10}{'':>8}{'':>8}{'W@230C':>10}{'':>8}{'Wh/d':>8}")
    for tag, p, a in out:
        d = a['days_counted']
        tot = a['coll_W'] + a['coll_K']
        dmp = 100.0 * (a['dump_K'] + a['dump_W']) / max(tot, 1e-9)
        print(f"  {tag:<16}{p['n_K']+p['n_W']:8.1f}{a['A_W']+a['A_K']:10.2f}"
              f"{a['meal_ok']:4d}/{a['meal_try']:<3d}{a['tea_ok']:4d}/{a['tea_try']:<3d}"
              f"{a['G_bank']*(230-p['T_amb']):10.1f}{dmp:8.1f}{a['pump_Wh']/d:8.0f}")

    # ---------------- cloud robustness: the decisive test
    print(f"\n{'='*78}\nCLOUD ROBUSTNESS  (meals delivered out of 7)\n{'='*78}")
    skies = [("clear          ", [1.0]*7),
             ("one dull day   ", [1.0,1.0,0.55,1.0,1.0,1.0,1.0]),
             ("two dull days  ", [1.0,0.55,1.0,0.45,1.0,1.0,1.0]),
             ("poor week      ", [0.8,0.6,0.5,0.7,0.6,0.8,0.7])]
    print(f"  {'model':<16}" + "".join(f"{n.strip():>17}" for n, _ in skies))
    for tag, p, _ in out:
        row = f"  {tag:<16}"
        for _, cl in skies:
            q = dict(p); q['cloud'] = cl
            r = simulate(q)
            row += f"{r['meal_ok']:>8d}/{r['meal_try']:<8d}"
        print(row)

    # ---------------- CPC crossover
    print(f"\n{'='*78}\nWHERE THE CPC HELPS AND WHERE IT HURTS\n{'='*78}")
    print(f"  {'dT (K)':>8}{'flat C=1':>11}{'CPC C=2':>11}{'CPC C=3':>11}   best")
    p = dict(BASE); G = 0.95
    for dT in (20, 40, 60, 80, 100, 120, 150, 180, 200, 225):
        e1 = eta(p, 35.0 + dT, G, 1.0, 1.00)
        e2 = eta(p, 35.0 + dT, G, 2.0, 0.85)
        e3 = eta(p, 35.0 + dT, G, 3.0, 0.82)
        best = max((e1, "flat"), (e2, "CPC C=2"), (e3, "CPC C=3"))[1]
        print(f"  {dT:8d}{e1:11.3f}{e2:11.3f}{e3:11.3f}   {best}")

    # ---------------- packed bed honesty check
    print(f"\n{'='*78}\nPACKED BED (quartzite+sand, Sandia SAND2004-3207) vs SALT ONLY\n{'='*78}")
    for med in ("salt", "packed"):
        p = dict(BASE); p['medium'] = med
        bb = build(p); m = MEDIA[med]
        salt_kg = p['V_store'] * m['rho'] * m['fill'] * (1.0 if med == 'salt' else 0.22)
        print(f"  {med:8s} usable {bb['usable']:5.2f} kWh in 30 L = "
              f"{bb['usable']/p['V_store']:.4f} kWh/L   KNO3-bearing salt {salt_kg:5.1f} kg")
    p = dict(BASE); p['medium'] = 'packed'
    need = build(dict(BASE))['usable']
    bb = build(p)
    print(f"  -> to match the salt-only {need:.2f} kWh the packed bed needs "
          f"{30*need/bb['usable']:.0f} L, i.e. {30*need/bb['usable']/30:.2f}x the volume")


if __name__ == "__main__":
    main()
