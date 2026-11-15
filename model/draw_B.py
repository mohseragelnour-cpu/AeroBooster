#!/usr/bin/env python3
"""AeroBooster v2, revision B (tracked trough). Drawings regenerated 15 November 2026.
All dimensions are design-stage values; simulated numbers come from runB4.py, runB5.py and runB6.py."""
import math
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Polygon, Arc, Wedge
from matplotlib.backends.backend_pdf import PdfPages

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
A4 = (11.69, 8.27)
YMAX = 63.0
OUT = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "AeroBooster_v2B_drawings_2026-11-15.pdf")
FOOT = ("Revision B, 15 November 2026. Design-stage drawing; to scale only where dimensioned. "
        "All values are calculated, none measured. CC BY 4.0 – M. A. S. Elwasela, 2026")
HOT = "#b3261e"; COLD = "#1f5fa8"; SIG = "0.45"; ELEC = "#2e7d32"; RAY = "#d08a00"
INK = "#0b0b0b"; INK2 = "#52514e"


def sheet(title, n):
    f = plt.figure(figsize=A4)
    ax = f.add_axes([0.04, 0.07, 0.92, 0.82]); ax.set_xlim(0, 100); ax.set_ylim(0, YMAX)
    ax.set_aspect("equal"); ax.axis("off")
    f.text(0.04, 0.94, f"AeroBooster v2 – Fig. {n}: {title}", fontsize=13, weight="bold")
    f.text(0.04, 0.025, FOOT, fontsize=7, color="0.3")
    return f, ax


def box(ax, x, y, w, h, t, fc="white", fs=9, ls="-", lw=1.3, ec="k"):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)


def arr(ax, p, q, c="k", ls="-", lw=1.4, t=None, off=(0, 1.2), fs=7.5, style="-|>"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11, color=c, ls=ls, lw=lw, shrinkA=0, shrinkB=0))
    if t:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], t, ha="center", fontsize=fs, color=c)


def lab(ax, t, xy, xt, fs=8, ha="left"):
    ax.annotate(t, xy=xy, xytext=xt, fontsize=fs, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.7, color="0.2"))


def dim(ax, p, q, t, off=(0, 1.0), fs=8):
    ax.annotate("", xy=p, xytext=q, arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], t, ha="center", va="center", fontsize=fs)


pdf = PdfPages(OUT)

# ------------------------------------------------------------------ Fig 1 system
f, ax = sheet("System schematic, option B (tracked troughs)", 1)
box(ax, 2, 39, 22, 16, "Two tracked parabolic troughs\n6 m² (2 × 1.6 m × 1.9 m)\npolar axis; mirrors turn about\nfixed receivers\nself-locking motor drive", fc="#f3f3f3", fs=8.5)
box(ax, 38, 34, 22, 20, "", fc="#fbe9d7")
ax.text(49, 45, "SALT STORE\n30 L NaNO₃/KNO₃ 60/40\n200–255 °C, ≈2.6 kWh usable\nfinned oil coil + heater", ha="center", va="center")
box(ax, 38, 54, 22, 3.2, "Baking plate + kettle pad + dock", fc="#d9d9d9", fs=7.5)
box(ax, 34, 31, 30, 2.2, "Loss-recovery water jacket in outer insulation", fc="#dcebf7", fs=7.5)
arr(ax, (24, 51), (38, 51), HOT, t="hot oil, up to ≈275 °C")
arr(ax, (38, 41), (24, 41), COLD, t="return oil", off=(3.5, -2.2))
ax.add_patch(Circle((29, 41), 1.6, fc="white", ec="k", zorder=3)); ax.text(29, 41, "P1", ha="center", va="center", fontsize=7, zorder=4)
box(ax, 25.5, 44.2, 10.5, 4.3, "Oil expansion tank\n(cool, closed)", fs=6.5); ax.plot([33.5, 33.5], [48.5, 51], "k", lw=1)
box(ax, 72, 28, 20, 26, "WATER STORE\n120 L, ≤ 90 °C", fc="#dcebf7")
arr(ax, (64, 32.1), (72, 32.1), COLD, t="recovered heat", off=(0, -3.1))
ax.add_patch(Circle((68, 32.1), 1.4, fc="white", ec="k", zorder=3)); ax.text(68, 32.1, "P2", ha="center", va="center", fontsize=7, zorder=4)
arr(ax, (60, 49), (72, 49), HOT, t="dual-window cascade\n(surplus, tail heat)", off=(0, 1.0))
box(ax, 64, 57.2, 28, 4.6, "Remote two-plate cooktop + 40 L oven\n(oil branch through P1, flow valves)", fc="#f3f3f3", fs=7.3)
arr(ax, (60, 52.5), (64, 58.2), HOT, lw=1.0)
box(ax, 78, 5, 16, 11, "Water collector\n≈ 2 m², fixed tilt\nthermosiphon; works\nin diffuse light", fc="#f3f3f3", fs=7.6)
arr(ax, (82.5, 16), (82.5, 28), HOT); arr(ax, (90, 28), (90, 16), COLD)
box(ax, 46, 18, 15, 6, "Tempering valve\n≤ 45 °C", fs=8)
box(ax, 27, 18, 15, 6, "Bathing and\nwashing taps", fs=8); arr(ax, (46, 21), (42, 21))
box(ax, 46, 7, 15, 6, "Hygiene tap\n(hot, out of reach)", fs=8)
box(ax, 27, 7, 15, 6, "Radiator loop\n(room heating)", fs=8)
ax.plot([75.6, 75.6], [28, 21], color=COLD, lw=1.4); arr(ax, (75.6, 21), (61, 21), COLD)
ax.plot([74.2, 74.2], [28, 10], color=HOT, lw=1.4); arr(ax, (74.2, 10), (61, 10), HOT)
ax.plot([72.8, 72.8, 34.5], [28, 4.8, 4.8], color=HOT, lw=1.4); arr(ax, (34.5, 4.8), (34.5, 7), HOT, lw=1.4)
box(ax, 2, 22.5, 18, 9, "PV module ≈ 2 m², 420 W\nfeeds the heater in the store\n(backup in cloud and haze)", fc="#eef5e6", fs=7.5)
arr(ax, (20, 28.5), (41, 35.2), ELEC, ls="--", lw=1.2, t="DC to heater", off=(-1.0, 1.4))
box(ax, 2, 6.5, 18, 12.5, "Controller\nPV 30–50 W + LiFePO₄\ndual-window rule\nruns P1, P2 and the drives\noff-sun logic, data log", fc="#eef5e6", fs=7.3)
ax.plot([2, 0.9, 0.9], [12, 12, 47], color=SIG, lw=0.8, ls="--"); arr(ax, (0.9, 47), (2, 47), SIG, ls="--", lw=0.8)
ax.plot([20, 24.5, 24.5, 29], [15, 15, 36.6, 36.6], color=SIG, lw=0.8, ls="--"); arr(ax, (29, 36.6), (29, 39.4), SIG, ls="--", lw=0.8)
arr(ax, (29, 36.6), (38, 36.6), SIG, ls="--", lw=0.8)
box(ax, 2, 57.2, 18, 4.6, "Portable cartridge\n5 kg salt, ≈0.25 kWh", fc="#fbe9d7", fs=7.5)
arr(ax, (20, 59.3), (38, 56.2), HOT, ls=":", t="docks on plate", off=(0, 1.3))
ax.text(2, 2.3, "Red = hot flow    Blue = cool or return flow    Green dashed = electric    Grey dashed = control signals", fontsize=7.5)
ax.text(2, 0.2, "Mechanical fail-safes: self-locking drive (the sun leaves the focus in 6–12 min), thermal switch just under 300 °C cuts the drive, "
        "bimetallic cold-start bypass (≈120 °C), relief valves.", fontsize=7.5)
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 2 store section
f, ax = sheet("Salt store – vertical cross-section", 2)
ax.add_patch(Rectangle((20, 8), 50, 52, fc="#eeeeee", ec="k", lw=1.5))
ax.add_patch(Rectangle((30, 16), 30, 36, fc="#cfe3f5", ec="k", lw=0.8))
ax.add_patch(Rectangle((31, 17), 28, 34, fc="#f7f0c8", ec="k", lw=0.8))
ax.add_patch(Rectangle((35, 20), 20, 28, fc="#f6c9a0", ec="k", lw=1.8))
ax.add_patch(Rectangle((35, 45), 20, 3, fc="white", ec="k", lw=0.6))
for x in np.arange(37, 54, 2.4):
    ax.plot([x, x], [23.5, 44.5], color="0.25", lw=1.1)
for x, y in [(39, 28), (45, 28), (51, 28), (42, 34), (48, 34), (39, 40), (45, 40), (51, 40)]:
    ax.add_patch(Circle((x, y), 0.9, fc=HOT, ec="k", lw=0.5))
ax.plot([36.5, 53.5, 53.5, 36.5], [22.6, 22.6, 21.4, 21.4], color=ELEC, lw=2.2)          # immersion heater
ax.add_patch(Rectangle((33, 48), 24, 2.2, fc="0.35", ec="k"))
ax.add_patch(Rectangle((31, 50.2), 28, 9, fc="#eeeeee", ec="k", ls="--"))
ax.add_patch(Rectangle((37, 17), 2, 3, fc="0.6", ec="k")); ax.add_patch(Rectangle((51, 17), 2, 3, fc="0.6", ec="k"))
ax.add_patch(Rectangle((16, 4), 58, 4, fc="#e6d7a8", ec="k"))
lab(ax, "Insulated lid 100 mm (on when not cooking)", (45, 56), (72, 59.5))
lab(ax, "Cast baking plate Ø400–450 mm,\ndirect contact = store lid", (57, 49), (72, 54.5))
lab(ax, "Headspace ≥ 10 % (salt expands ≈5 %)", (54, 46.5), (72, 49.5))
lab(ax, "Solar salt 30 L (≈57 kg), never pumped", (54, 37), (72, 45))
lab(ax, "Fins 20–30 mm pitch, steel or aluminium", (52.6, 31), (72, 40.5))
lab(ax, "Oil coil (or two-phase condenser coil):\nwelded, no joints inside the salt", (51.9, 28), (72, 35.5))
lab(ax, "Immersion heater 0.5–1 kW: PV backup\nand bench charging", (53.5, 22), (72, 30))
lab(ax, "Aerogel blanket 20–50 mm (hot face)", (58, 24), (72, 25))
lab(ax, "Recovery water jacket → water store", (59.6, 18.5), (72, 21))
lab(ax, "Thin-wall stainless or ceramic supports", (52, 18), (72, 17))
lab(ax, "Mineral wool 130–200 mm, skin ≤ 60 °C", (68, 12), (72, 13))
lab(ax, "Steel drip tray with dry sand", (70, 6), (76, 3))
ax.text(1.5, 52, "Estimated standby loss\n(0.35 m tank, 240 °C)\n\n150 mm wool         ≈85 W\n20 aerogel+130 wool ≈75 W\n50 aerogel+200 wool ≈55 W\n\nThe last build is the one\nused in the simulations.\nThe jacket is credited with\nreturning 60 % of the loss\nto the water store.",
        fontsize=8, va="top", family="DejaVu Sans Mono")
dim(ax, (35, 14), (55, 14), "tank ≈ 350 mm", off=(0, -1.6), fs=7.5)
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 3 control
f, ax = sheet("Dual-window rule as filed (claims 1 to 5), with the v2-B actions", 3)
x0, y0, H = 12, 9, 50
T = lambda t: y0 + (t - 100) / (280 - 100) * H
ax.add_patch(Rectangle((x0, T(100)), 6, T(200) - T(100), fc="#dcebf7", ec="none"))
ax.add_patch(Rectangle((x0, T(200)), 6, T(215) - T(200), fc="#d0d0d0", ec="none"))
ax.add_patch(Rectangle((x0, T(215)), 6, T(255) - T(215), fc="#f6c9a0", ec="none"))
ax.add_patch(Rectangle((x0, T(255)), 6, T(280) - T(255), fc="white", ec="none", hatch="////"))
ax.add_patch(Rectangle((x0, T(100)), 6, H, fc="none", ec="k", lw=1.2))
for t in range(100, 281, 20):
    ax.plot([x0 - 1, x0], [T(t), T(t)], "k", lw=0.8); ax.text(x0 - 1.6, T(t), f"{t}", ha="right", va="center", fontsize=7.5)
ax.text(x0 + 3, T(100) - 2.4, "Salt store, °C", ha="center", fontsize=8)
rows = [(255, "255 °C  working maximum: charging stops and the troughs turn off-sun", HOT),
        (235, "235 °C  oven floor (the oven may draw only above this)", INK),
        (215, "215 °C  first threshold, and the kisra-griddle floor", INK),
        (200, "200 °C  second threshold", INK),
        (150, "150 °C  stew floor", INK),
        (120, "about 120 °C  bimetallic cold-start bypass closes (mechanical)", COLD)]
for t, s, c in rows:
    ax.plot([x0, x0 + 9], [T(t), T(t)], color=c, lw=1.2); ax.text(x0 + 10, T(t), s, va="center", fontsize=8.5, color=INK)
bx = 62
box(ax, bx, T(215) + 0.6, 36, T(255) - T(215) - 1.2, "UPPER WINDOW, above 215 °C\nSurplus heat may pass to the\nwater store at any hour", fc="#fbe9d7", fs=8)
box(ax, bx, T(200) + 0.25, 36, T(215) - T(200) - 0.5, "DEAD BAND 200–215 °C: no transfer", fc="#e4e4e4", fs=7.5)
box(ax, bx, T(150) + 2.0, 36, T(200) - T(150) - 2.6, "LOWER WINDOW, below 200 °C\nTail heat may pass to the water store\nbetween 08:00 and 20:00 only, so the store\nis not drained overnight", fc="#e7f1fb", fs=8)
box(ax, bx, 1.0, 36, 12.0, "On every transfer\n• store at least 15 K hotter than the water store\n• water store below 90 °C", fc="#eef5e6", fs=8)
box(ax, 22, 1.0, 37, 12.0, "v2-B actions around the rule\noff-sun at 255 °C in the store, at 285 °C in the oil,\nor on any sensor or pump fault;\na thermal switch just under 300 °C cuts the drive", fc="#f3f3f3", fs=8)
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 4 trough geometry
f, ax = sheet("Tracked trough – cross-section and side elevation (to scale)", 4)
s = 21.0; fm = 0.40; Fx, Fy = 26.0, 37.0; yg = Fy - 0.85 * s
xm = np.linspace(-0.8, 0.8, 161)
px = xm; py = xm ** 2 / (4 * fm) - fm                      # relative to focus, metres


def rot(px, py, deg):
    a = math.radians(deg); c, s_ = math.cos(a), math.sin(a)
    return px * c - py * s_, px * s_ + py * c


ax.plot([2, 50], [yg, yg], color="0.3", lw=1.2); ax.add_patch(Rectangle((2, yg - 1.2), 48, 1.2, fc="#e6d7a8", ec="none"))
rx, ry = rot(px, py, 60)
ax.plot(Fx + s * rx, Fy + s * ry, color="0.55", lw=1.4, ls="--")
ax.plot(Fx + s * px, Fy + s * py, "k", lw=2.4)
for xr in (-0.72, -0.5, -0.25, 0.25, 0.5, 0.72):
    yr = xr ** 2 / (4 * fm) - fm
    ax.plot([Fx + s * xr, Fx + s * xr], [53, Fy + s * yr], color=RAY, lw=0.9)
    ax.plot([Fx + s * xr, Fx], [Fy + s * yr, Fy], color=RAY, lw=0.9)
ax.add_patch(Circle((Fx, Fy), 0.035 * s, fc="white", ec="k", lw=0.8, zorder=4))
ax.add_patch(Circle((Fx, Fy), 0.021 * s, fc="#222", ec="k", zorder=5))
ax.add_patch(Wedge((Fx, Fy), 0.075 * s, 20, 160, width=0.035 * s, fc="0.7", ec="k", lw=0.6, zorder=4))
ax.plot([Fx, Fx - 3.2, Fx + 3.2, Fx], [Fy, yg, yg, Fy], color="0.45", lw=1.0, ls=":")
dim(ax, (Fx - 0.8 * s, 54.6), (Fx + 0.8 * s, 54.6), "aperture 1.60 m", off=(-9.5, 1.1))
dim(ax, (6.6, Fy - fm * s), (6.6, Fy), "f = 0.40 m", off=(1.2, 5.6))
ax.plot([6.0, Fx], [Fy - fm * s, Fy - fm * s], color="0.6", lw=0.5); ax.plot([2.6, Fx - 16.9], [Fy, Fy], color="0.6", lw=0.5)
dim(ax, (3.2, yg), (3.2, Fy), "axis ≥ 0.85 m", off=(4.6, -6.5))
ax.annotate("Fixed receiver on the rotation axis (detail in Fig. 5)", xy=(Fx, Fy + 1.9), xytext=(Fx, 59.3), fontsize=7.5, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", lw=0.7, color="0.2"))
lab(ax, "Mirror at 60° from noon (dashed):\nthe rim clears the ground", (Fx + s * rx[0] + 0.3, Fy + s * ry[0] + 0.4), (31, 14.2), fs=7.5)
ax.text(26, 8.2, "Cross-section. Rim angle 90°. One trough: 1.6 m × 1.9 m = 3.0 m²; two troughs = 6 m².\n"
        "Absorber 42 mm, so concentration = 1.6 / (π × 0.042) = 12. Direct-beam light only.", ha="center", fontsize=8)
# side elevation
s2 = 12.5; tilt = math.radians(15.0); ct, st = math.cos(tilt), math.sin(tilt)
P0 = np.array([56.0, yg + (0.85 - 0.25 * st) * s2])
P = lambda t: P0 + s2 * t * np.array([ct, st])
off = s2 * 0.40 * np.array([st, -ct])
ax.plot([53, 99], [yg, yg], color="0.3", lw=1.2); ax.add_patch(Rectangle((53, yg - 1.2), 46, 1.2, fc="#e6d7a8", ec="none"))
ax.add_patch(Polygon([P(0.25), P(2.15), P(2.15) + off, P(0.25) + off], fc="#d9d9d9", ec="k", lw=1.2))
for t in (0.12, 2.28):
    ax.plot([P(t)[0], P(t)[0]], [yg, P(t)[1]], color="k", lw=2.0)
ax.plot([P(0)[0], P(2.4)[0]], [P(0)[1], P(2.4)[1]], color="k", lw=3.0)
ax.plot([P(2.4)[0], 97.5], [P(2.4)[1], P(2.4)[1]], color=HOT, lw=2.0)
ax.plot([P(0)[0], P(0)[0], 97.5], [P(0)[1], yg + 1.0, yg + 1.0], color=COLD, lw=1.6)
ax.text(98, P(2.4)[1] + 1.2, "to store", ha="right", fontsize=7.5, color=HOT); ax.text(98, yg + 1.9, "return", ha="right", fontsize=7.5, color=COLD)
ax.add_patch(Rectangle((P(2.28)[0] + 0.8, P(2.28)[1] - 4.6), 3.0, 2.4, fc="#eef5e6", ec="k", lw=0.8)); ax.text(P(2.28)[0] + 4.3, P(2.28)[1] - 3.4, "worm drive", va="center", fontsize=7)
ax.add_patch(Arc(P0, 14, 14, theta1=0, theta2=15, lw=0.8)); ax.plot([P0[0], P0[0] + 8.5], [P0[1], P0[1]], color="0.6", lw=0.5)
nrm = np.array([-st, ct])
for t in (0.7, 1.2, 1.7):
    a = P(t) + nrm * 15; b = P(t) + nrm * 1.0
    arr(ax, tuple(a), tuple(b), RAY, lw=0.9)
d = math.radians(23.45); dirn = np.array([math.sin(tilt + d), -math.cos(tilt + d)])
b = P(2.02) + off; a = b - dirn * 21
ax.plot([a[0], b[0]], [a[1], b[1]], color=RAY, lw=0.9, ls="--")
refl = dirn - 2 * np.dot(dirn, nrm) * nrm
c = b + refl * (0.40 * s2 / abs(np.dot(refl, nrm)))
ax.plot([b[0], c[0]], [b[1], c[1]], color=RAY, lw=0.9, ls="--")
mid = P(1.2) + off * 0.5
ax.text(mid[0], mid[1], "mirror cradle", fontsize=7.5, rotation=15, ha="center", va="center")
e0, e1 = P(0.0) + nrm * 1.3, P(0.25) + nrm * 1.3
ax.plot([e0[0], e1[0]], [e0[1], e1[1]], color="k", lw=0.8); ax.text(e0[0] - 0.4, e0[1] + 1.5, "0.25 m", fontsize=6.8, ha="center")
ax.text(54, 59.5, "Side elevation. The receiver stays still; the mirror cradle hangs below it and turns about it.\n"
        "Axis tilt = site latitude (15° drawn). Solid rays: equinox noon. Dashed ray: a solstice, when the\n"
        "reflected light lands up to 0.23 m along the axis, so the absorber is 0.25 m longer than the\nmirror at each end.", fontsize=7.6, va="top")
ax.text(P(0.12)[0] + 1.0, yg - 3.0, "low end\n(toward the equator)", fontsize=7, ha="center", va="top")
ax.text(P(2.28)[0], yg - 3.0, "high end\n(toward the pole)", fontsize=7, ha="center", va="top")
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 5 receiver
f, ax = sheet("Receiver – cross-section, supports, and the two ideas not adopted", 5)
k = 0.33; cx, cy = 27.0, 27.0
r_a, r_gi, r_go = 21 * k, 32 * k, 35 * k
th = np.radians(np.linspace(76, 133, 40)); ra = 21.0
ix = ra * np.sin(th) - ra * th * np.cos(th); iy = ra * np.cos(th) + ra * th * np.sin(th)
shell = [(-56, 20.5), (-56, 44), (-30, 60), (30, 60), (56, 44), (56, 20.5)]
inner = [(-ix[-1], iy[-1])] + [(-x, y) for x, y in zip(ix[::-1], iy[::-1])] + [(0, 38.5)] + list(zip(ix, iy))
poly = [(cx + k * x, cy + k * y) for x, y in shell[::-1]] + [(cx + k * x, cy + k * y) for x, y in inner]
ax.add_patch(Polygon(poly, fc="#f7f0c8", ec="k", lw=1.0))
ax.plot([cx + k * x for x, y in inner], [cy + k * y for x, y in inner], color="#3b6fb5", lw=2.6)
ax.add_patch(Circle((cx, cy), r_go, fc="#eaf4fb", ec="k", lw=1.0))
ax.add_patch(Circle((cx, cy), r_gi, fc="white", ec="k", lw=0.6))
for a in (90, 210, 330):
    ax.add_patch(Wedge((cx, cy), r_gi, a - 9, a + 9, width=r_gi - r_a, fc="#c9b28a", ec="k", lw=0.6))
ax.add_patch(Circle((cx, cy), r_a, fc="#1c1c1c", ec="k"))
ax.add_patch(Circle((cx, cy), 18 * k, fc="#e8a33d", ec="k", lw=0.6))
for a in (-78, -50, -22, 22, 50, 78):
    b = math.radians(a - 90)
    p = (cx + 21.5 * math.cos(b), cy + 21.5 * math.sin(b)); q = (cx + (r_a + 0.2) * math.cos(b), cy + (r_a + 0.2) * math.sin(b))
    arr(ax, p, q, RAY, lw=1.0)
pA = (cx - 21.5, cy + 1.0); pB = (cx + k * 30.0, cy + k * 31.4); pC = (cx + r_a * math.cos(math.radians(50)), cy + r_a * math.sin(math.radians(50)))
ax.plot([pA[0], pB[0]], [pA[1], pB[1]], color=RAY, lw=1.0, ls="--"); arr(ax, pB, pC, RAY, lw=1.0, ls="--")
for xx in (-12, 0, 12):
    arr(ax, (cx + xx, 57.5), (cx + xx, cy + k * 61.5), "0.55", lw=0.8)
ax.text(cx, 59.2, "un-concentrated sunlight: shaded by the cap (about 6 % of the aperture)", ha="center", fontsize=7.3, color=INK2)
ax.text(cx, 3.6, "concentrated light from the mirror below, from 90° either side", ha="center", fontsize=7.5, color=INK2)
lab(ax, "Steel absorber tube 42 mm, electroplated\nblack chrome (emittance ≤ 0.25 at 300 °C)", (cx + r_a * 0.72, cy - r_a * 0.72), (52, 15.5), fs=7.8)
lab(ax, "Thermal oil (or the boiling fluid\nof the two-phase loop)", (cx + 2, cy - 1), (52, 21.5), fs=7.8)
lab(ax, "Ceramic support ring: centres the\nabsorber and lets it slide", (cx + r_gi * 0.80, cy - r_gi * 0.47), (52, 27.5), fs=7.8)
lab(ax, "Borosilicate glass envelope ≈70 mm,\nair inside, not evacuated", (cx + r_go * 0.96, cy + r_go * 0.2), (52, 33.5), fs=7.8)
lab(ax, "Reflective inner face (secondary reflector):\nreturns light that passes above the absorber", (cx + k * 40, cy + k * 27.4), (52, 39.5), fs=7.8)
lab(ax, "Cap: ceramic-fibre insulation in a\nweather shell, on the side away from the mirror", (cx + k * 44, cy + k * 46), (52, 45.5), fs=7.8)
# longitudinal sketch
bx0, by0 = 52.0, 52.0
ax.add_patch(Rectangle((bx0, by0), 40, 5.0, fc="#eaf4fb", ec="k", lw=0.8))
ax.add_patch(Rectangle((bx0 - 3, by0 + 1.5), 47.5, 2.0, fc="#1c1c1c", ec="k"))
for xx in (bx0 + 1.5, bx0 + 13.5, bx0 + 25.5, bx0 + 37.5):
    ax.add_patch(Rectangle((xx, by0), 1.0, 1.5, fc="#c9b28a", ec="k", lw=0.5)); ax.add_patch(Rectangle((xx, by0 + 3.5), 1.0, 1.5, fc="#c9b28a", ec="k", lw=0.5))
arr(ax, (bx0 - 3, by0 + 2.5), (bx0 - 6.5, by0 + 2.5), "k", lw=1.0)
ax.text(bx0 - 3.2, by0 + 6.0, "free end:\ngrows ≈6 mm", fontsize=7, ha="center")
ax.text(bx0 + 45, by0 + 6.0, "fixed end\n(store side)", fontsize=7, ha="center")
ax.text(bx0 + 20, by0 + 6.2, "Side view: steel absorber sliding in ceramic rings inside the glass", fontsize=7.5, ha="center")
box(ax, 51.5, 0.6, 47.5, 10.8, "", fc="#f3f3f3", lw=0.9)
ax.text(52.3, 10.6, "Examined on 15 November 2026 and not adopted", fontsize=8, weight="bold", va="top")
ax.text(52.3, 8.6, "• Lens strip above the receiver: it collects only the light on its own area, which\n"
        "   would reach the receiver by the mirror anyway. Net change −1 % to +2 %.\n"
        "• Solid conducting rod to the store: copper, 1.9 m, 150 K end to end, carries\n"
        "   19 W (20 mm) to 174 W (60 mm) of about 1,250 W absorbed. The hollow form\n"
        "   that works is the sealed two-phase loop of Fig. 6.", fontsize=7.4, va="top")
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 6 heat transport
f, ax = sheet("Heat transport from receiver to store – the two forms", 6)
ax.plot([50, 50], [3, 58], color="0.7", lw=0.8, ls="--")
ax.text(3, 59.5, "(a) Pumped thermal oil – the standard build", fontsize=10, weight="bold")
ax.text(53, 59.5, "(b) Sealed two-phase loop – the pump-free variant", fontsize=10, weight="bold")
# (a)
g = 14.0
ax.plot([3, 47], [g, g], color="0.3", lw=1.0)
a0 = np.array([6.0, g + 9.0]); a1 = a0 + 22 * np.array([math.cos(math.radians(15)), math.sin(math.radians(15))])
ax.plot([a0[0], a1[0]], [a0[1], a1[1]], color="k", lw=4)
ax.text(11, a0[1] + 5.8, "receiver (fixed)", fontsize=7.5, rotation=15)
box(ax, 34, g + 3, 11, 13, "SALT\nSTORE", fc="#fbe9d7", fs=8)
ax.plot([a1[0], a1[0] + 2, 34], [a1[1], g + 13.5, g + 13.5], color=HOT, lw=2)
ax.plot([34, 31, 31, a0[0] - 2, a0[0] - 2, a0[0]], [g + 6, g + 6, g + 2.0, g + 2.0, a0[1], a0[1]], color=COLD, lw=2)
ax.add_patch(Circle((20, g + 2.0), 1.5, fc="white", ec="k", zorder=3)); ax.text(20, g + 2.0, "P1", ha="center", va="center", fontsize=7, zorder=4)
box(ax, 28.0, g + 18.5, 9, 4, "expansion\ntank", fs=7); ax.plot([32.5, 32.5], [g + 13.5, g + 18.5], "k", lw=1)
ax.plot([a0[0] + 1.5, a0[0] + 1.5, a1[0] - 1.2, a1[0] - 1.2], [a0[1] + 0.4, a0[1] + 9.5, a0[1] + 9.5, a1[1]], color="0.4", lw=1.0, ls="--")
ax.text(a0[0] + 2.2, a0[1] + 10.3, "bimetallic cold-start bypass (≈120 °C)", fontsize=7)
ax.text(3, 55.5, "• Works at any height and distance.\n• Flow × temperature rise gives the trough's efficiency\n   directly: the measurement the first trough is built for.\n"
        "• Food-grade oil (NSF HT-1) rated to 327 °C bulk.\n• If the pump stops, the controller turns the troughs\n   off-sun; the thermal switch backs it up.\n• Feeds the remote cooktop and oven as well.", fontsize=8, va="top")
ax.text(3, 9.5, "Oil leaves the receiver at up to about 275 °C.\nUnpressurised; closed, cool expansion tank.", fontsize=7.8, va="top")
# (b)
ax.plot([53, 97], [g, g], color="0.3", lw=1.0)
ax.add_patch(Rectangle((80, g), 17, 9.5, fc="#e6d7a8", ec="0.3", lw=0.8)); ax.text(88.5, g + 1.6, "kitchen floor raised", fontsize=7, ha="center")
b0 = np.array([56.0, g + 9.0]); b1 = b0 + 22 * np.array([math.cos(math.radians(15)), math.sin(math.radians(15))])
ax.plot([b0[0], b1[0]], [b0[1], b1[1]], color="k", lw=5)
ax.plot([b0[0] + 0.6, b1[0] - 2.2], [b0[1] + 0.15, b1[1] - 0.6], color="#e8a33d", lw=2.2)
ax.text(59.5, b0[1] + 5.0, "receiver = boiler tube", fontsize=7.5, rotation=15)
sx, sy = 84.0, g + 9.5
box(ax, sx, sy, 11, 13, "", fc="#fbe9d7"); ax.text(sx + 5.5, sy + 4.0, "SALT\nSTORE", ha="center", va="center", fontsize=8)
cyc = sy + 10.0
ax.plot([sx + 1.5, sx + 9.5, sx + 9.5, sx + 1.5, sx + 1.5, sx + 9.5], [cyc + 1.6, cyc + 1.6, cyc + 0.6, cyc + 0.6, cyc - 0.4, cyc - 0.4], color=HOT, lw=1.6)
ax.plot([b1[0], b1[0] + 1.5, b1[0] + 1.5, sx + 1.5], [b1[1], b1[1] + 1.5, cyc + 1.6, cyc + 1.6], color=HOT, lw=2)
ax.plot([sx + 9.5, sx + 12.3, sx + 12.3, b0[0] - 2, b0[0] - 2, b0[0]], [cyc - 0.4, cyc - 0.4, g - 2.2, g - 2.2, b0[1], b0[1]], color=COLD, lw=1.6)
ax.text(b1[0] + 0.9, b1[1] + 4.2, "vapour\nrises", fontsize=7.3, color=HOT, ha="right", va="center")
ax.text(70, g - 3.9, "liquid returns by gravity", fontsize=7.3, color=COLD, ha="center")
ax.plot([b1[0] - 6, sx], [b1[1], b1[1]], color="0.5", lw=0.6, ls=":")
ax.annotate("", xy=(81.6, b1[1]), xytext=(81.6, cyc - 0.4), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(sx + 5.5, sy + 14.4, "condenser coil above the\nreceiver's upper end", fontsize=7, ha="center", va="bottom")
ax.text(53, 55.5, "• Biphenyl and diphenyl oxide fluid, sealed in. It boils in the\n   receiver and condenses in a coil at the top of the store.\n• No pump and no controller to move the heat; no flow back\n   at night.\n"
        "• Condition: the condenser stands above the receiver's upper\n   end, so the kitchen floor is about 0.8 m above the collector's\n   ground at 15° latitude, and more at higher latitudes.\n• No remote cooktop or oven from this loop.", fontsize=8, va="top")
ax.text(53, 9.0, "Pressure, absolute:  200 °C 0.24 bar  ·  250 °C 0.85 bar  ·  282 °C 1.7 bar  ·  316 °C 3.1 bar\n"
        "Freezes at 12 °C; strong odour; harmful to water life. Welded, leak-tested, filled under vacuum,\nfitted with a relief device. Life tests in mild steel: about 40,000 h at 270 and at 300 °C.", fontsize=7.4, va="top")
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 7 cartridge
f, ax = sheet("Portable salt cartridge (5 kg, ≈0.25 kWh)", 7)
ax.add_patch(Rectangle((12, 30), 40, 14, fc="#eeeeee", ec="k", lw=1.4))
ax.add_patch(Rectangle((16, 30), 32, 10, fc="#f6c9a0", ec="k", lw=1.6))
for x in np.arange(18, 47, 3):
    ax.plot([x, x], [30.3, 38.5], color="0.25", lw=1)
ax.add_patch(Rectangle((16, 38.6), 32, 1.4, fc="white", ec="k", lw=0.5))
ax.add_patch(Rectangle((16, 29.2), 32, 0.8, fc="#111", ec="k"))
ax.plot([8, 12], [40, 40], "k", lw=3); ax.plot([52, 56], [40, 40], "k", lw=3)
ax.add_patch(Rectangle((12, 44), 40, 6, fc="#eeeeee", ec="k", ls="--"))
lab(ax, "Removable insulated cover", (40, 47), (58, 58))
lab(ax, "Sealed steel shell, welded; headspace ≥ 10 %", (47, 39.3), (58, 52.5))
lab(ax, "Solar salt ≈ 5 kg with internal fins", (44, 35), (58, 47))
lab(ax, "Insulated wall and handles (≤ 60 °C)", (54, 40), (58, 41.5))
lab(ax, "Contact and sun face: flat steel with\nhigh-temperature black absorber paint", (40, 29.4), (58, 34))
box(ax, 6, 6, 40, 14, "Charge mode A – docking\nPlace the sun face down on the kettle pad of the main store.\nIt charges between meals by conduction.", fs=8, fc="#fbe9d7")
box(ax, 52, 6, 42, 14, "Charge mode B – direct solar\nSun face at the focus of a small dish.\nCheck the patents in force in the country first\n(approvals section of the design document).", fs=8, fc="#f3f3f3")
ax.text(6, 24, "Use: carry to the shelter, turn over, cook on the top face – simmer a pot, bake a few flatbreads, keep tea hot. Ø ≈ 300 mm, mass ≈ 9 kg filled.", fontsize=8)
pdf.savefig(f); plt.close(f)

# ------------------------------------------------------------------ Fig 8 energy and service (simulated)
f = plt.figure(figsize=A4)
f.text(0.04, 0.94, "AeroBooster v2 – Fig. 8: Where the collected heat goes, and the service delivered (simulated)", fontsize=13, weight="bold")
f.text(0.04, 0.025, FOOT, fontsize=7, color="0.3")
SURF = "#fcfcfb"
ax = f.add_axes([0.15, 0.63, 0.80, 0.20]); ax.set_facecolor(SURF)
cats = ["Clear winter day", "Clear summer day"]
parts = [("Cooking loads (stew, morning meal, kisra, oven)", [1.92, 1.92], "#2a78d6"),
         ("Passed to the water store by the dual-window rule", [2.24, 0.18], "#eb6834"),
         ("Standby loss returned to water by the jacket", [0.80, 0.82], "#1baf7a"),
         ("Standby loss not recovered", [0.53, 0.55], "#eda100"),
         ("Turned away off-sun (store full)", [0.45, 6.32], "#e87ba4")]
left = np.zeros(2)
for name, v, c in parts:
    ax.barh(cats, v, left=left, color=c, edgecolor=SURF, linewidth=2.0, height=0.46, label=name)
    for i in range(2):
        if v[i] >= 0.5:
            ax.text(left[i] + v[i] / 2, i, f"{v[i]:.1f}", ha="center", va="center", color="white", fontsize=9, weight="bold")
    left += np.array(v)
for i, (tot, col) in enumerate(zip(left, (5.96, 9.80))):
    ax.text(tot + 0.12, i, f"collected {col:.1f} kWh", va="center", fontsize=8.5, color=INK)
ax.set_xlim(0, 11.6); ax.set_xlabel("kWh per day from two troughs, 6 m², at the solstices", color=INK2)
ax.tick_params(axis="both", colors=INK2, length=0); ax.grid(axis="x", color="0.88", lw=0.8); ax.set_axisbelow(True)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("0.8")
ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.45, 1.02), ncol=3, fontsize=7.8, handlelength=1.2, columnspacing=1.4)
f.text(0.15, 0.548, "Segments under 0.5 kWh are not labelled: summer, 0.2 to the water store; winter, 0.5 turned away.", fontsize=7.6, color=INK2)

tb = f.add_axes([0.04, 0.07, 0.92, 0.43]); tb.axis("off")
cols = ["Case (v2 store; cell = stew · kisra · oven · morning meal)", "Summer, clear", "Summer, poor", "Winter, clear", "Winter, poor"]
ALL = "all"
rowsT = [["A. Filed fixed troughs, 5.59 m², collector as filed", ALL, "6/7 · 4/7 · 1/3 · 4/7", "7/7 · 7/7 · 0/3 · 7/7", "2/7 · 0/7 · 0/3 · 0/7"],
         ["B. 6 m², expected receiver values (adopted)", ALL, "6/7 · 5/7 · 1/3 · 6/7", ALL, "2/7 · 0/7 · 0/3 · 0/7"],
         ["B. 6 m², cautious receiver values", ALL, "6/7 · 4/7 · 1/3 · 4/7", "7/7 · 7/7 · 0/3 · 7/7", "1/7 · 0/7 · 0/3 · 0/7"],
         ["B. 6 m², ordinary black paint on the absorber", "7/7 · 7/7 · 0/3 · 7/7", "6/7 · 0/7 · 0/3 · 2/7", "7/7 · 0/7 · 0/3 · 0/7", "0/7 · 0/7 · 0/3 · 0/7"],
         ["B. 4 m², expected receiver values", ALL, "6/7 · 3/7 · 0/3 · 3/7", "7/7 · 7/7 · 0/3 · 7/7", "0/7 · 0/7 · 0/3 · 0/7"],
         ["PV modules, 6 m², on a heater in the store", ALL, ALL, "7/7 · 7/7 · 0/3 · 7/7", "4/7 · 0/7 · 0/3 · 0/7"],
         ["Adopted B plus one 2 m² PV module", ALL, "7/7 · 7/7 · 1/3 · 7/7", ALL, "3/7 · 2/7 · 0/3 · 1/7"]]
t = tb.table(cellText=rowsT, colLabels=cols, loc="upper center", cellLoc="center", colWidths=[0.40, 0.15, 0.15, 0.15, 0.15])
t.auto_set_font_size(False); t.set_fontsize(8.2); t.scale(1, 1.8)
for (r, c), cell in t.get_celld().items():
    cell.set_edgecolor("0.75"); cell.set_linewidth(0.6)
    if r == 0:
        cell.set_facecolor("#efefec"); cell.set_text_props(weight="bold")
    if c == 0:
        cell.set_text_props(ha="left"); cell._loc = "left"
    if r == 2:
        cell.set_facecolor("#e7f1fb")
tb.text(0.0, 0.03, "“all” = 7/7 · 7/7 · 3/3 · 7/7. Poor weeks are broken cloud. In a week of uniform dust haze the adopted troughs give stew on 2 days and nothing else; "
        "the PV row is unchanged.\nBasis: archived model with a tracked direct-beam input; 50 mm aerogel + 200 mm wool; jacket returning 60 %; latent heat 97 kJ/kg; winter air 20 °C; "
        "direct beam derived from the filed model, not from site data.", fontsize=7.4, color=INK2, va="top", transform=tb.transAxes)
pdf.savefig(f); plt.close(f)
pdf.close()
print("written", OUT)
