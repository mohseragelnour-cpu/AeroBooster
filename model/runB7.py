#!/usr/bin/env python3
"""runB7 – C.3 insulation correction study.

The original Rev B assumed 50 mm aerogel + 200 mm wool (G ≈ 0.289 W/K).
That requires ~100 mm microporous insulation at $12,000/m³.

This run file explores realistic insulation options and their effect on
PV area requirements:

  - 200 mm rock wool only (k ≈ 0.055):  G ≈ 0.49 W/K  → needs ~6.5 m² PV
  - 20 mm aerogel + 200 mm wool:        G ≈ 0.37 W/K  → needs ~5.5 m² PV
  - 50 mm aerogel + 200 mm wool (RevB): G ≈ 0.289 W/K → needs ~4 m² PV

Also tests the effect of the revised dual-window thresholds (thrHi 245,
thrLo 140) and the water collector contribution.
"""
import sys, math
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from modelB import *

INC = math.cos(math.radians(23.45))
capsec = dict(eta0=0.58, a1=6.6*0.85, a2=0.016*0.85)
NONE = dict(mode='trk', area=0.0, K=dict(eta0=0.0, a1=0.0, a2=0.0, C=1.0, pipe=1.0))

# ---- Section 19: Insulation reality check ----
sec("19. INSULATION REALITY CHECK – G values for different builds (30 L store, ⌀0.35 m)")
print("  Microporous required for G=0.289: ~100 mm at k≈0.020, costs ~$12,000/m³")
print("  Rock wool 200 mm at k=0.055 (at working temperature) is realistic")
print()

# Three insulation levels, each with jacket and 2 m² flat
for label, ins in [
    ("RevB original: 50 aerogel + 200 wool, G≈0.289", INS_REVB),
    ("C.3 compromise: 20 aerogel + 200 wool, G≈0.37",  INS_C3_AER20),
    ("C.3 realistic: 200 mm rock wool only, G≈0.49",   INS_C3_REAL),
]:
    sec(f"  {label}")
    block(f"trough 6 m², {label}", trough(6.0, **capsec), inc=INC, jacket=0.6, n_W=1.0, **ins)

# ---- Section 20: PV area sweep with realistic insulation ----
sec("20. PV AREA SWEEP – realistic insulation (200 mm rock wool, G≈0.49 W/K)")
for apv in (4.0, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0):
    block(f"PV {apv:.1f} m², rock wool 200 mm, jacket 60%, flat 2 m²",
          NONE, A_pv=apv, jacket=0.6, n_W=1.0, **INS_C3_REAL)

# ---- Section 21: Water collector contribution with C.3 insulation ----
sec("21. WATER COLLECTOR CONTRIBUTION – C.3 realistic insulation")
block("PV 6.5 m², WITH 2 m² flat collector",
      NONE, A_pv=6.5, jacket=0.6, n_W=1.0, **INS_C3_REAL)
block("PV 6.5 m², WITHOUT flat collector",
      NONE, A_pv=6.5, jacket=0.6, n_W=0.0, **INS_C3_REAL)
block("trough 6 m², WITH 2 m² flat collector",
      trough(6.0, **capsec), inc=INC, jacket=0.6, n_W=1.0, **INS_C3_REAL)
block("trough 6 m², WITHOUT flat collector",
      trough(6.0, **capsec), inc=INC, jacket=0.6, n_W=0.0, **INS_C3_REAL)

# ---- Section 22: Hybrid with C.3 insulation ----
sec("22. HYBRID (trough + PV) with C.3 realistic insulation")
block("trough 6 m² + PV 2 m², broken cloud",
      trough(6.0, **capsec), inc=INC, A_pv=2.0, jacket=0.6, n_W=1.0, **INS_C3_REAL)
block("trough 4 m² + PV 2 m², broken cloud",
      trough(4.0, **capsec), inc=INC, A_pv=2.0, jacket=0.6, n_W=1.0, **INS_C3_REAL)

print("\n" + "=" * 118)
print("CONCLUSION: With realistic insulation (G≈0.49 W/K), the C-PV home unit")
print("needs 6.5 m² PV (≈1.4 kWp) to match the trough-based service levels.")
print("The 2 m² flat water collector remains critical for bake service.")
print("=" * 118)
