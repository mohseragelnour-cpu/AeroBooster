#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroBooster v2, revision C - annual smart-use model (365 days, 6-minute steps).

What it simulates
  * A latent-heat salt store (solar salt 60/40, enthalpy model: solid -> melting range -> liquid).
  * Up to three heat sources for the store: tracked parabolic troughs (temperature-dependent
    efficiency), PV modules on a resistance heater, and nothing else. A flat water collector
    feeds the 120 L water store.
  * The filed dual-window cascade rule between the salt store and the water store.
  * A smart-use household schedule: three meals, tea, kisra on a target number of days a week
    in a flexible afternoon window, oven bakes in a midday window, hot water, winter heating.
  * Surplus uses when the store is full: charging portable cartridges, an extra "bonus" bake
    to share, and a dryer/pasteurizer fed by the water-side diverting valve.
  * A small electrical system (controller PV + battery) with load shedding.

Rules that keep it honest
  * A load is served only while the store is at or above that load's temperature floor;
    otherwise it is counted as unmet. Nothing is clamped and no energy is created.
  * An energy balance is closed for every run and printed (residual should be ~0).

Ideas taken from the AeroBooster "v3" model by another AI (with corrections):
  * year-long hourly structure, enthalpy (three-phase) store model, weekly dust cycle with
    cleaning, a forced 3-day winter dust storm, battery load shedding, a 75 C water diverter.
Corrections relative to that model: temperature-dependent collector loss, published salt
properties, load floors enforced, no temperature clamps, no thermoelectric drain on the store.

All inputs are design assumptions; nothing here is measured.
"""
import math, random
from dataclasses import dataclass, field

DT = 0.1                     # h
LAT = 15.6                   # deg N (Khartoum)
CPW = 4.186                  # kJ/kg.K

# ----------------------------------------------------------------------------- weather
MONTH_T = [23, 25, 28, 32, 34, 34, 32, 31, 32, 32, 28, 24]          # monthly mean air, C
MONTH_P = {  # probabilities of day types: clear, hazy (dust), partly cloudy, heavy dust/overcast
    0: (.75, .20, .00, .05), 1: (.75, .20, .00, .05), 2: (.70, .25, .00, .05),
    3: (.55, .35, .00, .10), 4: (.50, .38, .02, .10), 5: (.45, .35, .10, .10),
    6: (.35, .15, .40, .10), 7: (.30, .15, .45, .10), 8: (.40, .15, .35, .10),
    9: (.70, .22, .03, .05), 10: (.75, .20, .00, .05), 11: (.75, .20, .00, .05)}
DAYTYPE = {"clear": (1.00, 1.00), "hazy": (0.55, 0.85), "partly": (None, 0.75), "heavy": (0.15, 0.45)}


def month_of(day):
    return min(11, int(day / 30.42))


def make_year(seed=7, storm=(14, 15, 16)):
    rnd = random.Random(seed)
    days = []
    for d in range(365):
        if d in storm:
            days.append("heavy"); continue
        p = MONTH_P[month_of(d)]; r = rnd.random(); c = 0.0
        for name, pr in zip(("clear", "hazy", "partly", "heavy"), p):
            c += pr
            if r <= c:
                days.append(name); break
        else:
            days.append("clear")
    return days


def sun(day, t):
    """solar altitude sin, declination (rad), hour angle (rad) at local solar time t (h)."""
    dec = math.radians(23.45) * math.sin(2 * math.pi * (284 + day + 1) / 365.0)
    w = math.radians(15.0 * (t - 12.0)); la = math.radians(LAT)
    s = math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(w)
    return s, dec, w


def irradiance(day, t, dtype, rnd):
    """DNI on a tracked aperture (W/m2, with cos(incidence) of a polar axis), global on a
    latitude-tilted plane (W/m2), and solar altitude sine."""
    s, dec, w = sun(day, t)
    if s <= 0.02:
        return 0.0, 0.0, s
    am = 1.0 / (s + 0.50572 * (6.07995 + math.degrees(math.asin(s))) ** -1.6364)
    dni = 1353.0 * 0.7 ** (am ** 0.678) * 0.88               # Meinel, with a Sahel aerosol factor
    ghi = 1098.0 * s * math.exp(-0.057 / s) * 0.97          # Haurwitz
    kd, kg = DAYTYPE[dtype]
    if dtype == "partly":                                   # broken cloud: beam on or off
        on = rnd.random() < 0.5
        dni = dni if on else 0.0
        ghi = ghi * (1.0 if on else 0.5)
    else:
        dni *= kd; ghi *= kg
    dhi = max(0.0, ghi - dni * s)
    # plane tilted at latitude facing south: cos(incidence) = cos(dec)*cos(w)
    cos_t = max(0.0, math.cos(dec) * math.cos(w))
    gt = dni * cos_t + dhi * (1 + math.cos(math.radians(LAT))) / 2
    trough = dni * math.cos(dec) if s > math.sin(math.radians(15)) else 0.0
    return trough, gt, s


def t_air(day, t):
    m = MONTH_T[month_of(day)]
    return m + 7.0 * math.sin(2 * math.pi * (t - 9.0) / 24.0)


# ----------------------------------------------------------------------------- store
class SaltStore:
    """Enthalpy model. H in kJ relative to 25 C. Solar salt 60/40 melting over 220-230 C."""
    def __init__(self, litres=30.0, latent=97.0, eg_frac=0.0, T0=230.0):
        self.m = litres * 1.90 * 0.90          # kg salt (90 % fill)
        self.m_salt = self.m * (1 - eg_frac)    # graphite stores no latent heat
        self.m_steel = 0.20 * self.m / 0.9 * 1.0
        self.cps, self.cpl, self.L = 1.40, 1.50, latent
        self.T1, self.T2 = 220.0, 230.0
        self.H = self.H_of(T0)

    def H_of(self, T):
        ms, st = self.m, self.m_steel * 0.50
        if T <= self.T1:
            return (ms * self.cps + st) * (T - 25)
        H1 = (ms * self.cps + st) * (self.T1 - 25)
        if T <= self.T2:
            f = (T - self.T1) / (self.T2 - self.T1)
            return H1 + f * self.m_salt * self.L + (ms * (self.cps + self.cpl) / 2 + st) * (T - self.T1)
        H2 = H1 + self.m_salt * self.L + (ms * (self.cps + self.cpl) / 2 + st) * (self.T2 - self.T1)
        return H2 + (ms * self.cpl + st) * (T - self.T2)

    def T(self):
        lo, hi = -50.0, 400.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if self.H_of(mid) < self.H: lo = mid
            else: hi = mid
        return (lo + hi) / 2

    def usable_kwh(self, Tlo=200.0, Thi=255.0):
        return (self.H_of(Thi) - self.H_of(Tlo)) / 3600.0


# ----------------------------------------------------------------------------- configuration
@dataclass
class Config:
    name: str
    trough_m2: float = 0.0
    receiver: tuple = (0.58, 5.61, 0.0136, 12.0)   # eta0, a1, a2 (per m2 absorber), C   (black chrome, cap + secondary)
    pv_m2: float = 0.0                             # PV modules on the store heater
    pv_eff: float = 0.172
    store_l: float = 30.0
    eg_frac: float = 0.0
    G_store: float = 0.289                         # W/K standby (50 mm aerogel + 200 mm wool)
    jacket: float = 0.6
    T_max: float = 255.0
    thr_hi: float = 245.0                          # dual-window first threshold (C.1: 240 -> 245, keeps the store above the 248 C oven start)
    tea_from_tank: bool = True                     # C.1: tea water is drawn from the hot-water tank
    thr_lo: float = 140.0                          # second threshold
    gate: tuple = (8.0, 20.0)
    flat_m2: float = 2.0
    tank_l: float = 120.0
    tank_max: float = 75.0                         # diverting valve
    kisra_per_week: int = 3
    oven_per_week: int = 2
    bonus: bool = True                             # surplus uses switched on
    seed: int = 7
    winter_heat: bool = True
    ctrl_pv_w: float = 100.0


@dataclass
class Event:
    name: str
    kwh: float
    kw: float
    floor: float
    left: float = 0.0
    active: bool = False


def run(cfg: Config, verbose=False):
    rnd = random.Random(cfg.seed + 101)
    days = make_year(cfg.seed)
    S = SaltStore(cfg.store_l, eg_frac=cfg.eg_frac)
    Tw = 45.0
    soc = 0.8; BATT = 1200.0
    acc = dict(coll=0.0, pv_heat=0.0, turned_away=0.0, loss=0.0, jacket=0.0, cascade=0.0, cook=0.0,
               flat=0.0, divert=0.0, wash=0.0, heat=0.0, cart=0.0, bonus=0.0, tankloss=0.0,
               dni=0.0, gt=0.0)
    H0 = S.H; W0 = Tw
    stats = {k: [0, 0] for k in ("breakfast", "main", "evening", "tea", "kisra", "oven", "wash", "heating")}
    week_kisra = []; week_oven = []; kisra_week = 0; oven_week = 0
    storm_service = []
    bonus_n = 0; cart_n = 0
    minT = 999; min_soc = 1.0
    soil_tr = soil_pv = 1.0
    daily = []
    for d in range(365):
        dtype = days[d]
        if d % 7 == 0:
            if d > 0:
                week_kisra.append(kisra_week); week_oven.append(oven_week)
            kisra_week = oven_week = 0
            soil_tr = soil_pv = 1.0                      # weekly cleaning
        if dtype == "heavy":
            soil_tr -= 0.05; soil_pv -= 0.03
        winter = cfg.winter_heat and (d < 59 or d >= 334)
        ev = {}
        kisra_today = oven_today = False
        cart_today = 0; bonus_today = False
        day_rec = dict(served=0, wanted=0)
        days_left_in_week = 7 - d % 7
        for step in range(int(round(24 / DT))):
            t = step * DT
            T = S.T(); Ta = t_air(d, t)
            minT = min(minT, T)
            trough_dni, gt, s = irradiance(d, t, dtype, rnd)
            acc["dni"] += trough_dni * DT / 1000; acc["gt"] += gt * DT / 1000
            # ---------------- heat in
            q_tr = 0.0
            if cfg.trough_m2 > 0 and trough_dni > 0:
                e0, a1, a2, C = cfg.receiver
                dT = T + 35 - Ta
                q = cfg.trough_m2 * (trough_dni * e0 * soil_tr - (a1 * dT + a2 * dT * dT) / C) * 0.95 / 1000
                pump_ok = soc > 0.12
                if q > 0 and pump_ok:
                    if T < cfg.T_max: q_tr = q
                    else: acc["turned_away"] += q * DT
            q_pv = cfg.pv_m2 * gt * cfg.pv_eff * soil_pv / 1000 if cfg.pv_m2 > 0 else 0.0
            pv_to_store = q_pv if T < cfg.T_max else 0.0
            pv_spill = q_pv - pv_to_store
            # ---------------- schedule (start events)
            def start(name, kwh, kw, floor):
                if name not in ev or not ev[name].active:
                    ev[name] = Event(name, kwh, kw, floor, kwh, True)
                    stats_key = name if name in stats else None
                    if stats_key: stats[stats_key][1] += 1
            hh = round(t, 1)
            if hh == 7.0: start("breakfast", 0.35, 0.7, 150)
            if hh == 13.0: start("main", 0.90, 1.0, 150)
            if hh == 19.0: start("evening", 0.60, 0.8, 150)
            for th in (7.5, 11.0, 16.5, 21.0):
                if hh == th:
                    start("tea", 1.5 * CPW * (100 - min(Tw, 95)) / 3600, 0.8, 150)
            # kisra: smart window 10:00-17:00
            need_k = cfg.kisra_per_week - kisra_week
            if (not kisra_today and need_k > 0 and 10.0 <= t <= 17.0 and "kisra" not in ev):
                urgent = need_k >= days_left_in_week
                if T >= 245 or (urgent and T >= 222) or (t >= 16.0 and T >= 222 and need_k >= days_left_in_week - 1):
                    start("kisra", 0.73, 0.6, 215); kisra_today = True
            need_o = cfg.oven_per_week - oven_week
            if (not oven_today and need_o > 0 and 11.0 <= t <= 15.0 and "oven" not in ev and not ev.get("kisra", Event("", 0, 0, 0)).active):
                urgent = need_o >= days_left_in_week
                if T >= 248 or (urgent and T >= 238):
                    start("oven", 0.54, 0.55, 235); oven_today = True
            # surplus uses (store full and the sun is up)
            surplus = (T >= cfg.T_max - 3) and (q_tr + q_pv) > 0.2
            if cfg.bonus and surplus and cart_today < 2 and "cart" not in [e for e in ev if ev[e].active]:
                start("cart", 0.25, 0.5, 225); cart_today += 1
            if cfg.bonus and surplus and kisra_today and not bonus_today and 12.0 <= t <= 16.0 and not ev.get("kisra").active:
                start("bonus", 0.73, 0.6, 215); bonus_today = True
            # ---------------- serve events
            q_out = 0.0; lid_off = False; tea_draw = 0.0
            for e in ev.values():
                if not e.active: continue
                if T >= e.floor:
                    take = min(e.kw * DT, e.left)
                    e.left -= take; q_out += take / DT; lid_off = True
                    if e.left <= 1e-9:
                        e.active = False
                        if e.name in stats: stats[e.name][0] += 1
                        if e.name == "kisra": kisra_week += 1
                        if e.name == "oven": oven_week += 1
                        if e.name == "cart": cart_n += 1; acc["cart"] += e.kwh
                        if e.name == "bonus": bonus_n += 1; acc["bonus"] += e.kwh
                        if e.name in ("breakfast", "main", "evening", "kisra", "oven", "tea"): acc["cook"] += e.kwh
                        if e.name == "tea" and cfg.tea_from_tank: tea_draw += 1.5 * CPW * (Tw - 25) / 3600 / DT
                else:
                    e.active = False                       # failed: not hot enough (unmet)
                    served = e.kwh - e.left
                    if e.name in ("breakfast", "main", "evening", "kisra", "oven", "tea"): acc["cook"] += served
                    if e.name == "cart": acc["cart"] += served
                    if e.name == "bonus": acc["bonus"] += served
            # ---------------- losses, jacket, cascade
            G = cfg.G_store + (0.6 if lid_off else 0.0)   # plate uncovered while cooking
            loss = G * (T - Ta) / 1000
            jk = cfg.jacket * cfg.G_store * (T - Ta) / 1000 if Tw < cfg.tank_max else 0.0
            near_full = T > cfg.thr_hi
            tail = T < cfg.thr_lo and cfg.gate[0] <= t < cfg.gate[1]
            casc = 0.0
            if (near_full or tail) and T > Tw + 15 and Tw < cfg.tank_max:
                casc = min(1.0, (cfg.tank_max - Tw) * cfg.tank_l * CPW / 3600 / DT)
            # ---------------- water store
            dTw = Tw + 6 - Ta
            q_flat = 0.0
            if gt > 50:
                eta = 0.70 - (1.25 * dTw + 0.0048 * dTw * dTw) / gt
                q_flat = max(0.0, cfg.flat_m2 * gt * eta / 1000)
            to_tank = q_flat if Tw < cfg.tank_max else 0.0
            divert = q_flat - to_tank
            draw = tea_draw
            if hh in (8.0, 18.0):                          # washing: 55 L at 45 C each
                stats["wash"][1] += 1
                need = 55 * CPW * (45 - 25) / 3600
                if Tw >= 45: draw += need / DT; stats["wash"][0] += 1
            if hh == 9.0 and Tw >= 60: draw += 12 * CPW * (Tw - 25) / 3600 / DT   # hygiene tap
            heat_on = winter and (t >= 20 or t < 5)
            if heat_on:
                stats["heating"][1] += 1
                if Tw >= 40: draw += 0.30; stats["heating"][0] += 1
            tank_loss = 0.8 * (Tw - Ta) / 1000
            # ---------------- update energies
            dH = (q_tr + pv_to_store - q_out - loss - casc) * DT * 3600
            S.H += dH
            dE = (to_tank + jk + casc * 0.9 - draw - tank_loss) * DT * 3600
            Tw += dE / (cfg.tank_l * CPW)
            acc["coll"] += q_tr * DT; acc["pv_heat"] += pv_to_store * DT; acc["loss"] += loss * DT
            acc["jacket"] += jk * DT; acc["cascade"] += casc * DT; acc["flat"] += to_tank * DT
            acc["divert"] += divert * DT; acc["tankloss"] += tank_loss * DT
            acc["turned_away"] += pv_spill * DT * 0          # PV spill goes to the battery side, see below
            acc["wash"] += draw * DT
            # ---------------- electrical
            p_gen = cfg.ctrl_pv_w * gt / 1000 * 0.85 * soil_pv + pv_spill * 1000 * 0.3   # controller panel + share of spilled PV
            p_load = 3.0 + (10.0 if q_tr > 0 else 0.0) + (1.0 if (cfg.trough_m2 > 0 and trough_dni > 0) else 0.0) + (12.0 if 18 <= t < 22 else 0.0) + \
                     (10.0 if (19 <= t < 21 and soc > 0.3) else 0.0) + (8.0 if heat_on and soc > 0.3 else 0.0)
            soc = min(1.0, max(0.05, soc + (p_gen - p_load) * DT / BATT))
            min_soc = min(min_soc, soc)
        if d in (14, 15, 16, 17):
            storm_service.append((d + 1, round(S.T()), kisra_today))
        daily.append(dict(day=d + 1, T=S.T(), Tw=Tw, dtype=dtype))
    week_kisra.append(kisra_week); week_oven.append(oven_week)
    # energy balance on the salt store (kWh)
    bal = (S.H - H0) / 3600 - (acc["coll"] + acc["pv_heat"] - acc["loss"] - acc["cascade"]
                               - acc["cook"] - acc["cart"] - acc["bonus"])
    res = dict(cfg=cfg, stats=stats, weeks_kisra=week_kisra, weeks_oven=week_oven, acc=acc,
               bonus=bonus_n, cart=cart_n, minT=minT, min_soc=min_soc, storm=storm_service,
               balance=bal, days=days, daily=daily, usable=S.usable_kwh())
    return res


def pct(a):
    return 100.0 * a[0] / a[1] if a[1] else float("nan")


def summary(r):
    s = r["stats"]; a = r["acc"]
    wk = r["weeks_kisra"]; wo = r["weeks_oven"]
    full_k = sum(1 for x in wk if x >= r["cfg"].kisra_per_week) / len(wk) * 100
    full_o = sum(1 for x in wo if x >= r["cfg"].oven_per_week) / len(wo) * 100
    return dict(name=r["cfg"].name,
                breakfast=pct(s["breakfast"]), main=pct(s["main"]), evening=pct(s["evening"]), tea=pct(s["tea"]),
                kisra_wk=sum(wk) / len(wk), kisra_full=full_k, oven_wk=sum(wo) / len(wo), oven_full=full_o,
                wash=pct(s["wash"]), heating=pct(s["heating"]) if s["heating"][1] else float("nan"),
                coll=(a["coll"] + a["pv_heat"]) / 365, turned=a["turned_away"] / 365, cook=a["cook"] / 365,
                cart=r["cart"], bonus=r["bonus"], divert=a["divert"], cascade=a["cascade"] / 365,
                loss=a["loss"] / 365, minT=r["minT"], soc=r["min_soc"] * 100, bal=r["balance"],
                dni=a["dni"] / 365, gt=a["gt"] / 365)


if __name__ == "__main__":
    r = run(Config("check: trough 6 m2", trough_m2=6.0))
    print(summary(r))
