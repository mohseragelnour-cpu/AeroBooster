"""Storage-time & peak-temperature experiment, reusing the P1 FV physics from p1_media.

Protocol per case: charge the vessel under direct-PV band heating for 2 clear days
(06:00-18:00 sun), then STANDBY from 18:00 of day 2 (no PV, no bake, losses only).
Record peak mean store temperature during charge, and the standby hours until the mean
store temperature falls below 200 C and 150 C.

Two insulation levels:
  baseline  = as-built P1-B: 200 mm side / 100 mm bottom / 100 mm lid rock wool, bridging x1.30
  improved  = +25 mm microporous inner liner, 250/150/150 mm rock wool, bridges minimised x1.12

All numbers are model outputs, not measurements.
"""
import math, numpy as np, p1_media as pm

RI, H, NR, NZ = pm.RI, pm.H, pm.NR, pm.NZ


def lam_mp(Tm):                      # microporous board, W/mK (incl. high-T rise)
    return 0.021 + 8e-5 * Tm


INS = {
    "baseline": dict(side=[(0.200, pm.k_rw)], bot=[(0.100, pm.k_rw)], lid=[(0.100, pm.k_rw)], bridge=1.30),
    "improved": dict(side=[(0.025, lam_mp), (0.250, pm.k_rw)], bot=[(0.025, lam_mp), (0.150, pm.k_rw)],
                     lid=[(0.025, lam_mp), (0.150, pm.k_rw)], bridge=1.12),
}


def ua_side_total(Tmean, Ta, ins):   # W/K for the whole cylindrical wall (height H)
    r = RI + 0.003
    Rth = 0.0
    Tm = 0.5 * (Tmean + Ta)
    for t, kf in ins["side"]:
        Rth += math.log((r + t) / r) / (2 * math.pi * kf(Tm) * H)
        r += t
    return ins["bridge"] / Rth


def ua_planar_total(Tmean, Ta, ins, key, area):   # W/K for bottom or lid
    Rth = 0.0
    Tm = 0.5 * (Tmean + Ta)
    for t, kf in ins[key]:
        Rth += t / (kf(Tm) * area)
    return ins["bridge"] / Rth


def run(medium, ins_name, Tmax, charge_days=2, standby_h=96):
    ins = INS[ins_name]
    g = pm.build(medium)
    kind, vol, dr, dz = g["kind"], g["vol"], g["dr"], g["dz"]
    Rg = g["R"]
    T = np.full(Rg.shape, 25.0)
    isalt = kind == 1
    Hs = np.where(isalt, pm.h_salt(T), 0.0)

    rf_out = (np.arange(NR) + 1) * dr
    A_r = 2 * math.pi * rf_out[:, None] * dz * np.ones((1, NZ))
    A_z = 2 * math.pi * g["rc"][:, None] * dr * np.ones((1, NZ))
    A_wall = 2 * math.pi * RI * dz
    plate_area = math.pi * RI ** 2
    steel_C = 7850 * 0.003 * 500

    hz = (g["zc"] > 0.020) & (g["zc"] < 0.170)
    nh = hz.sum()
    Twall_max = 400.0 if medium.startswith("salt") else 560.0
    ns, R = 1, RMATCH

    # stability dt
    Ttest = np.full(Rg.shape, 320.0)
    kr, kz = pm.kfield(kind, Ttest)
    rc_ = pm.rhoc(kind, Ttest) * 1000
    rc_[isalt] = pm.SALT["rho"] * 1400
    dt = min(20.0, 0.8 * np.min(rc_ * min(dr, dz) ** 2 / (2 * (kr + kz))))

    total_s = int((charge_days * 86400 + standby_h * 3600) / dt)
    charge_end = charge_days * 86400
    peak_mean = 0.0
    peak_top = 0.0
    t_200 = t_150 = None
    mean = 25.0
    _lastP = 0.0

    for s in range(total_s):
        t = s * dt
        th = (t / 3600) % 24
        Ta = pm.ambient(th)
        if isalt.any():
            T[isalt] = pm.T_salt(Hs[isalt])
        mean = float((T * vol).sum() / vol.sum())
        charging = t < charge_end
        if charging:
            peak_mean = max(peak_mean, mean)
            peak_top = max(peak_top, float(T[:, -1].mean()))
        else:
            if t_200 is None and mean < 200:
                t_200 = (t - charge_end) / 3600
            if t_150 is None and mean < 150:
                t_150 = (t - charge_end) / 3600
                break

        kr, kz = pm.kfield(kind, T)
        q = np.zeros_like(T)
        kfr = 2 * kr[:-1] * kr[1:] / (kr[:-1] + kr[1:])
        fr = kfr * A_r[:-1] / dr * (T[:-1] - T[1:]); q[:-1] -= fr; q[1:] += fr
        kfz = 2 * kz[:, :-1] * kz[:, 1:] / (kz[:, :-1] + kz[:, 1:])
        fz = kfz * A_z[:, :-1] / dz * (T[:, :-1] - T[:, 1:]); q[:, :-1] -= fz; q[:, 1:] += fz

        UA_side = ua_side_total(mean, Ta, ins)
        UA_bot = ua_planar_total(mean, Ta, ins, "bot", plate_area)
        UA_lid = ua_planar_total(mean, Ta, ins, "lid", plate_area)
        q[-1, :] -= (UA_side / NZ) * (T[-1, :] - Ta)
        q[:, 0] -= (UA_bot / NR) * (T[:, 0] - Ta)
        q[:, -1] -= (UA_lid / NR) * (T[:, -1] - Ta)       # lid closed during charge & standby

        if charging:
            G = pm.poa(th)
            # control on the MEAN store temperature (fair across media; avoids a cold-sensor overshoot)
            on = (mean < Tmax) and (T[-1, hz].max() < Twall_max)
            if G > 0 and on:
                if s % max(1, int(60 / dt)) == 0:
                    _lastP = pm.pv_power_R(R, G, Ta + 0.03 * G, ns)
                q[-1, hz] += _lastP / nh

        Ccell = pm.rhoc(kind, T) * 1000 * vol
        Ccell[-1, :] += steel_C * A_wall
        sens = ~isalt
        T[sens] += q[sens] * dt / Ccell[sens]
        if isalt.any():
            Hs[isalt] += q[isalt] * dt / (vol[isalt] * 1000)

    if t_200 is None:
        t_200 = float("nan")
    if t_150 is None:
        t_150 = standby_h
    return dict(medium=medium, ins=ins_name, Tmax=Tmax, peak_mean=peak_mean, peak_top=peak_top,
                h_to_200=t_200, h_to_150=t_150, mass=pm.mass_report(medium))


if __name__ == "__main__":
    RMATCH, _, _ = pm.match_R(1)
    print(f"matched R (1 panel) = {RMATCH:.1f} ohm\n")
    cases = [
        ("salt", "baseline", 255), ("salt", "improved", 255),
        ("iron_stack", "baseline", 320), ("iron_stack", "improved", 320),
        ("iron_stack", "baseline", 255),   # iron+sand at the SAME temp as salt (isolates the medium)
    ]
    rows = []
    for med, ins, tmax in cases:
        r = run(med, ins, tmax)
        rows.append(r)
        print(f"{med:11s} {ins:8s} Tmax{tmax:4d}  peak_mean {r['peak_mean']:5.0f}C  peak_top {r['peak_top']:5.0f}C  "
              f"->200C in {r['h_to_200']:4.1f} h  ->150C in {r['h_to_150']:4.1f} h  "
              f"(Fe {r['mass']['iron_kg']}kg sand {r['mass']['sand_kg']}kg salt {r['mass']['salt_kg']}kg)")
    import json
    json.dump(rows, open("results_storage_time.json", "w"), indent=1)
