"""AeroBooster P1 bench store: storage-media comparison under direct PV heating.

Vessel: tank ID 294 mm, usable height 194 mm, 3 mm mild steel, insulation 200 mm (side) /
100 mm (bottom) / 100 mm lid, rock-wool k(T). Ceramic band heater on the side wall
(z 20..170 mm) fed directly from 592 W TOPCon panels through a fixed matched resistance.
Axisymmetric (r, z) explicit finite-volume model with enthalpy (phase change) and
anisotropic conductivity. Cooking plate is a lumped node on top.

Daily schedule (clear November days, Khartoum-like): PV 06:00-18:00, evening bake
18:00-19:00, morning bake 07:00-07:30. Bake load: dough on the plate modelled as
h_load = 40 W/m2K to 100 C over the 250 mm cooking area (= 4.8 kW/m2 at 220 C).
A bake minute "counts" when the plate is >= 200 C.

All numbers are model outputs, not measurements.
"""
import math, sys
import numpy as np

# ----------------------------------------------------------------- PV module (592 W, 72-cell TOPCon)
# Interpolated between the 590 W and 595 W bins of a 72-cell TOPCon datasheet.
ISC0, VOC0, VMP0 = 14.36, 52.57, 44.42
IMP0 = 592 / VMP0
TC_VOC, TC_ISC = -0.0025, 0.00045
C2 = (VMP0 / VOC0 - 1) / math.log(1 - IMP0 / ISC0)
C1 = (1 - IMP0 / ISC0) * math.exp(-VMP0 / (C2 * VOC0))


def pv_I(V, G, Tc, ns):
    if G <= 1:
        return 0.0
    isc = ISC0 * G / 1000 * (1 + TC_ISC * (Tc - 25))
    voc = VOC0 * (1 + TC_VOC * (Tc - 25)) * (1 + 0.06 * math.log(G / 1000))
    v = V / ns
    if v >= voc:
        return 0.0
    return max(0.0, isc * (1 - C1 * (math.exp(v / (C2 * voc)) - 1)))


def pv_power_R(R, G, Tc, ns):
    lo, hi = 0.0, VOC0 * ns * 1.2
    for _ in range(50):
        V = (lo + hi) / 2
        if pv_I(V, G, Tc, ns) * R > V:
            lo = V
        else:
            hi = V
    V = (lo + hi) / 2
    return V * pv_I(V, G, Tc, ns)


def pv_mpp(G, Tc, ns):
    best = 0.0
    for k in range(1, 400):
        V = ns * VOC0 * k / 400
        best = max(best, V * pv_I(V, G, Tc, ns))
    return best


def poa(t_h):                 # plane-of-array irradiance, clear day, W/m2
    if t_h < 6 or t_h > 18:
        return 0.0
    return 1000 * math.sin(math.pi * (t_h - 6) / 12) ** 1.15 * 0.95


def ambient(t_h):             # November, hot dry climate
    return 29 + 8 * math.sin(2 * math.pi * (t_h - 9) / 24)


def daily_yield(R, ns):
    Ed = Em = 0.0
    for m in range(0, 24 * 60, 5):
        t = m / 60
        G = poa(t)
        if G <= 0:
            continue
        Tc = ambient(t) + 0.03 * G
        Ed += pv_power_R(R, G, Tc, ns) * 5 / 60
        Em += pv_mpp(G, Tc, ns) * 5 / 60
    return Ed / 1000, Em / 1000


def match_R(ns):
    best = None
    for R10 in range(10, 400, 2):
        R = R10 / 10
        e, em = daily_yield(R, ns)
        if best is None or e > best[1]:
            best = (R, e, em)
    return best


# ----------------------------------------------------------------- insulation
def k_rw(Tm):                 # rock wool / ceramic fibre, W/mK, at mean temperature Tm
    return 0.037 + 1.2e-4 * Tm + 2.2e-7 * Tm * Tm


# ----------------------------------------------------------------- media
RI, H = 0.147, 0.194
NR, NZ = 8, 9


def build(medium):
    dr, dz = RI / NR, H / NZ
    rc = (np.arange(NR) + 0.5) * dr
    zc = (np.arange(NZ) + 0.5) * dz
    Rg, Zg = np.meshgrid(rc, zc, indexing="ij")
    # per-cell properties: rho_c(T) via enthalpy function, kr, kz
    m = {}
    if medium in ("salt", "salt_bigcore"):
        # 180 mm salt (as-loaded bulk 1710 kg/m3), 14 mm headspace modelled as the gap to the plate;
        # P1-B: central cast-iron core d80 from the plate down to z = 100 mm
        fill = Zg < 0.180
        core = (Rg < (0.056 if medium == "salt_bigcore" else 0.040)) & (Zg > 0.100)
        m["kind"] = np.where(core, 2, np.where(fill, 1, 0))   # 0 = air gap, 1 = salt, 2 = iron core
    elif medium == "iron_stack":
        # stacked scrap brake discs d280 (iron fraction 0.65 inside r<140), sand in vents/gaps and outer annulus
        m["kind"] = np.where(Rg < 0.140, 3, 4)
    elif medium == "sand":
        m["kind"] = np.full(Rg.shape, 4)
    elif medium == "ring_sand_piston":
        # scrap-iron ring hugs the wall (spreads the band heater), sand core, iron piston on top
        k = np.where(Rg > 0.110, 3, 4)
        k[:, -1] = np.where(Rg[:, -1] < 0.125, 2, k[:, -1])
        k[0, :] = 2
        m["kind"] = k
    elif medium in ("scrap_piston", "scrap_disc", "sand_piston"):
        # movable cast-iron piston: solid top disc (top row, r<0.125) + central arm (col 0) to the floor.
        bed = 4 if medium == "sand_piston" else 3     # 4 = sand only, 3 = scrap discs + sand
        k = np.where(Rg < 0.140, bed, 4)
        k[:, -1] = np.where(Rg[:, -1] < 0.125, 2, k[:, -1])   # top disc, iron
        if medium != "scrap_disc":
            k[0, :] = 2                                       # central arm, iron, full height
        m["kind"] = k
    elif medium == "iron_random":
        # random cast-iron scrap pieces with sand filling the voids (iron fraction 0.50)
        m["kind"] = np.full(Rg.shape, 5)
    else:
        raise ValueError(medium)
    vol = 2 * math.pi * Rg * dr * dz
    return dict(dr=dr, dz=dz, rc=rc, zc=zc, R=Rg, Z=Zg, vol=vol, **m)


SALT = dict(rho=1710, cps=1.40, cpl=1.50, L=97.0, T1=220.0, T2=230.0)


def h_salt(T):                # kJ/m3 relative to 25 C
    r, a, b, c = SALT["rho"], SALT["cps"], SALT["cpl"], 0.5 * (SALT["cps"] + SALT["cpl"])
    T1, T2, L = SALT["T1"], SALT["T2"], SALT["L"]
    H1 = r * a * (T1 - 25)
    H2 = H1 + r * (L + c * (T2 - T1))
    return np.where(T <= T1, r * a * (T - 25),
           np.where(T <= T2, H1 + r * (L * (T - T1) / (T2 - T1) + c * (T - T1)),
                    H2 + r * b * (T - T2)))


def T_salt(Hv):
    r, a, b, c = SALT["rho"], SALT["cps"], SALT["cpl"], 0.5 * (SALT["cps"] + SALT["cpl"])
    T1, T2, L = SALT["T1"], SALT["T2"], SALT["L"]
    H1 = r * a * (T1 - 25)
    H2 = H1 + r * (L + c * (T2 - T1))
    return np.where(Hv <= H1, 25 + Hv / (r * a),
           np.where(Hv <= H2, T1 + (Hv - H1) / (r * (L / (T2 - T1) + c)),
                    T2 + (Hv - H2) / (r * b)))


CP_FE = lambda T: 0.46 + 3.5e-4 * T            # grey cast iron, kJ/kgK
CP_SAND = lambda T: 0.78 + 4.5e-4 * T          # dry quartz sand
RHO_FE, RHO_SAND = 7200.0, 1600.0


def rhoc(kind, T):            # kJ/m3K for sensible kinds; air gap tiny
    out = np.empty_like(T)
    out[kind == 0] = 60.0          # air gap: pseudo-capacity for solver stability (gap holds < 0.1 kJ/K)
    out[kind == 2] = RHO_FE * CP_FE(T[kind == 2])
    out[kind == 3] = 0.65 * RHO_FE * CP_FE(T[kind == 3]) + 0.35 * RHO_SAND * CP_SAND(T[kind == 3])
    out[kind == 4] = RHO_SAND * CP_SAND(T[kind == 4])
    out[kind == 5] = 0.50 * RHO_FE * CP_FE(T[kind == 5]) + 0.50 * RHO_SAND * CP_SAND(T[kind == 5])
    return out


def kfield(kind, T):
    kr = np.empty_like(T); kz = np.empty_like(T)
    sand = 0.30 + 4e-4 * T                     # dry sand incl. radiation, W/mK
    liq = T > SALT["T2"]
    mush = (T > SALT["T1"]) & ~liq
    ks = np.where(liq, 3.0, np.where(mush, 1.5, 0.6))   # molten salt: natural convection as k_eff
    g = kind == 0
    kr[g] = kz[g] = 0.6                        # air gap: conduction + radiation equivalent (14 mm)
    for k_, v in ((1, ks), (2, 45.0 + 0 * T), (4, sand)):
        sel = kind == k_
        kr[sel] = v[sel]; kz[sel] = v[sel]
    sel = kind == 3                            # brake disc stack: radial in-plane, axial through contacts
    kr[sel] = 0.65 * 45 * 0.85 + 0.35 * sand[sel]; kz[sel] = 6.0
    sel = kind == 5                            # random chunks: weak point contacts
    kr[sel] = kz[sel] = 2.0 + sand[sel]
    return kr, kz


# ----------------------------------------------------------------- simulation
def simulate(medium, ns, R, Tmax, days=4, dt=None, plate_target=235.0, verbose=False):
    g = build(medium)
    kind, vol, dr, dz = g["kind"], g["vol"], g["dr"], g["dz"]
    Rg = g["R"]
    T = np.full(Rg.shape, 25.0)
    isalt = kind == 1
    # energy state per cell (kJ/m3 rel. 25 C)
    Hs = np.where(isalt, h_salt(T), 0.0)

    # geometry factors
    rf_out = (np.arange(NR) + 1) * dr                     # outer face radius per radial index
    A_r = 2 * math.pi * rf_out[:, None] * dz * np.ones((1, NZ))   # outer radial face areas
    A_z = 2 * math.pi * g["rc"][:, None] * dr * np.ones((1, NZ))  # axial face areas (annulus)
    A_wall = 2 * math.pi * RI * dz                         # per wall cell
    A_bot = A_z[:, 0]
    plate_area_all = math.pi * RI ** 2
    A_cook = math.pi * 0.125 ** 2
    # plate coupling: salt -> via core (in grid) + gap; sensible -> contact under the whole plate
    if medium.startswith("salt"):
        h_contact = None
    else:
        h_contact = 400.0                                  # W/m2K, cast iron faces resting on medium
    C_plate = 4.2 * 0.50 * 1000 + 3.0 * 0.5 * 1000         # plate d250 x12 + top ring, J/K (approx)
    Tp = 25.0
    steel_C = 7850 * 0.003 * 500                           # J/m2K of wall

    # band heater: wall cells with zc in 20..170 mm
    hz = (g["zc"] > 0.020) & (g["zc"] < 0.170)
    nh = hz.sum()
    Twall_max = 400.0 if medium.startswith("salt") else 520.0

    # stability
    if dt is None:
        Ttest = np.full(Rg.shape, 300.0)
        kr, kz = kfield(kind, Ttest)
        rc_ = rhoc(kind, Ttest) * 1000
        rc_[isalt] = SALT["rho"] * 1400
        lim = np.min(rc_ * np.minimum(dr, dz) ** 2 / (2 * (kr + kz)))
        dt = min(20.0, 0.8 * lim)
    steps = int(days * 86400 / dt)

    res = []
    day = None
    acc = None
    for s in range(steps):
        t = s * dt
        th = (t / 3600) % 24
        d = int(t // 86400)
        if day != d:
            if acc:
                res.append(acc)
            acc = dict(day=d + 1, E_pv=0.0, E_heater=0.0, E_loss=0.0, E_bake=0.0, bake_ok_min_eve=0.0,
                       bake_ok_min_morn=0.0, good_min_eve=0.0, good_min_morn=0.0, T_mean_18=None, T_mean_07=None, Tp_max=0.0, Twall_max=0.0)
            day = d
        Ta = ambient(th)
        # temperatures
        if isalt.any():
            T[isalt] = T_salt(Hs[isalt])
        Tm_ins = 0.5 * (T.mean() + Ta)
        kin = k_rw(Tm_ins)
        # losses (W)
        UA_side = 2 * math.pi * kin * dz / math.log((RI + 0.003 + 0.200) / (RI + 0.003)) * 1.30
        UA_bot_cell = kin * A_bot / 0.100 * 1.30
        UA_lid = kin * plate_area_all * 1.25 / 0.100 * 1.30
        q = np.zeros_like(T)                                  # net heat into each cell, W
        kr, kz = kfield(kind, T)
        # radial conduction between cells
        kfr = 2 * kr[:-1] * kr[1:] / (kr[:-1] + kr[1:])
        Gr = kfr * A_r[:-1] / dr
        fr = Gr * (T[:-1] - T[1:])
        q[:-1] -= fr; q[1:] += fr
        kfz = 2 * kz[:, :-1] * kz[:, 1:] / (kz[:, :-1] + kz[:, 1:])
        Gz = kfz * A_z[:, :-1] / dz
        fz = Gz * (T[:, :-1] - T[:, 1:])
        q[:, :-1] -= fz; q[:, 1:] += fz
        # side loss
        q[-1, :] -= UA_side * (T[-1, :] - Ta)
        q[:, 0] -= UA_bot_cell * (T[:, 0] - Ta)
        # PV heater
        G = poa(th)
        Tctrl = T[0, NZ // 2] if not medium.startswith("salt") else T[0, 3]
        on = (Tctrl < Tmax) and (T[-1, hz].max() < Twall_max)
        Ppv = 0.0
        if G > 0:
            Tc = Ta + 0.03 * G
            Ppv = pv_power_R(R, G, Tc, ns) if (s % max(1, int(60 / dt)) == 0 or not hasattr(simulate, "_last")) else simulate._last
            simulate._last = Ppv
            acc["E_pv"] += Ppv * dt / 3.6e6
        Ph = Ppv if on else 0.0
        if Ph > 0:
            q[-1, hz] += Ph / nh
            acc["E_heater"] += Ph * dt / 3.6e6
        # plate coupling
        top = T[:, -1]
        if medium.startswith("salt"):
            # core cells (kind 2) at top touch the plate through the gap with steel; others via air/radiation
            Gtop = np.where(kind[:, -1] == 2, 45.0 * A_z[:, -1] / (dz / 2), 0.6 * A_z[:, -1] / (dz / 2))
        else:
            Gtop_max = 1.0 / (1.0 / (h_contact * A_z[:, -1]) + (dz / 2) / (kz[:, -1] * A_z[:, -1]))
            if "piston" in medium or medium == "scrap_disc":
                Gtop = Gtop_max                              # fixed disc always touches the plate
            else:
                Gtop = np.where(Tp < plate_target, Gtop_max, Gtop_max * 0.08)
        fp = Gtop * (top - Tp)
        q[:, -1] -= fp
        Qp_in = fp.sum()
        baking = (18.0 <= th < 19.0) or (7.0 <= th < 7.5)
        if baking:
            q_load = max(0.0, 40.0 * A_cook * (Tp - 100.0))
            Qp_out = q_load + UA_lid * 0.5 * (Tp - Ta)   # lid off: rim and exposed edge losses
            acc["E_bake"] += q_load * dt / 3.6e6
            if 200 <= Tp <= 260:
                acc["good_min_eve" if th >= 18 else "good_min_morn"] += dt / 60
            if Tp >= 200:
                if th >= 18:
                    acc["bake_ok_min_eve"] += dt / 60
                else:
                    acc["bake_ok_min_morn"] += dt / 60
        else:
            Qp_out = UA_lid * (Tp - Ta)
        Qloss = UA_side * (T[-1, :] - Ta).sum() + (UA_bot_cell * (T[:, 0] - Ta)).sum() + UA_lid * (Tp - Ta)
        acc["E_loss"] += Qloss * dt / 3.6e6
        Tp += (Qp_in - Qp_out) * dt / C_plate
        acc["Tp_max"] = max(acc["Tp_max"], Tp)
        acc["Twall_max"] = max(acc["Twall_max"], float(T[-1, :].max()))
        # update cells (wall steel mass lumped into outer cells)
        Ccell = rhoc(kind, T) * 1000 * vol
        Ccell[-1, :] += steel_C * A_wall
        sens = ~isalt
        T[sens] += q[sens] * dt / Ccell[sens]
        if isalt.any():
            Hs[isalt] += q[isalt] * dt / (vol[isalt] * 1000 + 0) - 0.0
            # steel wall share for salt outer cells: add its capacity by converting part of q
        mean = float((T * vol).sum() / vol.sum())
        if abs(th - 18.0) < dt / 3600 / 2 + 1e-9:
            acc["T_mean_18"] = mean
        if abs(th - 7.0) < dt / 3600 / 2 + 1e-9:
            acc["T_mean_07"] = mean
    res.append(acc)
    return res, dict(dt=dt, mass=mass_report(medium))


def mass_report(medium):
    g = build(medium)
    kind, vol = g["kind"], g["vol"]
    v = lambda k: float(vol[kind == k].sum())
    fe = v(2) * RHO_FE + v(3) * 0.65 * RHO_FE + v(5) * 0.5 * RHO_FE
    sand = v(3) * 0.35 * RHO_SAND + v(4) * RHO_SAND + v(5) * 0.5 * RHO_SAND
    salt = v(1) * SALT["rho"]
    return dict(iron_kg=round(fe, 1), sand_kg=round(sand, 1), salt_kg=round(salt, 1))


def stored_kWh(medium, Thi, Tlo):
    """Energy stored in the medium between two uniform temperatures."""
    g = build(medium)
    kind, vol = g["kind"], g["vol"]
    E = 0.0
    if (kind == 1).any():
        E += float(((h_salt(np.array(Thi)) - h_salt(np.array(Tlo))) * vol[kind == 1].sum()))
    Ts = np.linspace(Tlo, Thi, 50)
    for k in (2, 3, 4, 5):
        if (kind == k).any():
            cap = np.mean([rhoc(np.array([k]), np.array([x]))[0] for x in Ts]) * (Thi - Tlo)
            E += cap * float(vol[kind == k].sum())
    return E / 3600


if __name__ == "__main__":
    print("== PV-direct matching, 592 W 72-cell TOPCon, clear November day ==")
    match = {}
    for ns in (1, 2):
        R, e, em = match_R(ns)
        match[ns] = R
        Vop = math.sqrt(R * 600 * ns) if False else None
        print(f"{ns} panel(s): matched R = {R:.1f} ohm, direct {e:.2f} kWh/day vs MPPT {em:.2f} ({100*e/em:.0f}%)")
        for f in (0.75, 1.33):
            e2, _ = daily_yield(R * f, ns)
            print(f"     R x{f:.2f} = {R*f:.1f} ohm -> {e2:.2f} kWh/day ({100*e2/em:.0f}%)")
    print()
    print("== Energy stored per medium in the P1 vessel (uniform temperatures) ==")
    for med, rngs in (("salt", [(200, 255), (25, 255)]), ("iron_stack", [(230, 300), (230, 400), (25, 400)]),
                      ("iron_random", [(230, 300), (230, 400)]), ("sand", [(230, 300), (230, 400)])):
        print(med, mass_report(med), "; ".join(f"{a}-{b} C: {stored_kWh(med, b, a):.2f} kWh" for a, b in rngs))
