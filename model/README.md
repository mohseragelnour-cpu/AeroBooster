# AeroBooster option B – simulation model

**Revision B + C.3 corrections, November 2026**

## What this is

A thin wrapper (`modelB.py`) around the archived AeroBooster oven-and-heating
model, filed as part of PCT/IB2026/062276.  The wrapper patches three things
in memory so it can simulate tracked parabolic troughs, photovoltaic
charging, and the improved store build, while the underlying model remains
unchanged.  Every result is reproducible by running the patched code against
the archived source file.

## Revision C.3 corrections (November 2026)

The following corrections were identified during the November 2026 audit and
are documented in the run files:

1. **Insulation reality check.** The original Rev B assumed 50 mm aerogel +
   200 mm wool giving G ≈ 0.289 W/K. This requires microporous insulation at
   ~$12,000/m³, unrealistic for a humanitarian product. The C.3 baseline uses
   200 mm rock wool (k ≈ 0.055 W/m·K), giving G ≈ 0.49 W/K. This raises PV
   area from ~4 m² to ~6.5 m² for the C-PV home unit.

2. **Dual-window thresholds.** Upper threshold raised from 215 °C to 245 °C
   to avoid oven full-weeks discrepancy (89% JS vs 96% Python). Lower
   threshold lowered from 200 °C to 140 °C.

3. **Water collector critical role.** Without the 2 m² flat collector, bake
   service collapses (96% → 72% home, 94% → 26% central).

4. **Tea from tank.** Option added: serve tea from the water store instead of
   the salt store, reducing morning draw on salt.

## Files

| File | Purpose |
|------|---------|
| `modelB.py` | Wrapper and patches; concentrating-branch irradiance, Erbs decomposition, tracked-trough and CPC models, C.3 insulation presets |
| `runB.py` | Main parametric study: aperture sweep, receiver variants, insulation layers, dust haze, tracker availability |
| `runB2.py` | Adopted design: 6 m² tracked trough with cap + secondary reflector, v2 build, season × cloud matrix |
| `runB3.py` | Sensitivity tests: latent heat, insulation conductivity, cloud factor |
| `runB4.py` | Thermal-oil vs two-phase, water-collector contribution, bake power density |
| `runB5.py` | PV-only vs hybrid, benchmarking PV against concentrator |
| `runB6.py` | Portable cartridge, communal kitchen sizing, central store analysis |
| `runB7.py` | **NEW** – C.3 insulation correction study: realistic vs optimistic insulation, PV area sweep with G ≈ 0.49 W/K |
| `aerobooster_oven_heating.py` | Archived base model (unchanged), loaded by `modelB.py` |
| `draw_B.py` | Generates the engineering drawings PDF (8 figures) |
| `*_out.txt` | Console output from each run file |

## Basis

- Site: Khartoum-like (15.6°N, peak GHI 1.0 kW/m² summer, 0.80 winter)
- Salt: solar salt 60/40 NaNO₃/KNO₃, latent heat 97 kJ/kg, range 200–255 °C
- Loads (filed): stew 0.80 kWh/day, kisra 0.73 kWh daily, oven 0.54 kWh 3×/week, morning 0.30 kWh, light 0.05 kWh
- Receiver (expected): η₀ = 0.55, a₁ = 6.6, a₂ = 0.016, C = 12
  (with cap + secondary: η₀ = 0.58, a₁ = 5.61, a₂ = 0.0136)
- PV: 0.172 of plane-of-array global (21% module × 0.88 hot-climate × 0.93 wiring)

## Running

`modelB.py` loads the archived base model `aerobooster_oven_heating.py` from
the same folder, so the run files work from any location.  `runB`–`runB6`
reproduce their `*_out.txt` files exactly.

```bash
python3 -I runB.py   > runB_out.txt
python3 -I runB7.py  > runB7_out.txt
```

## Limitations

1. All values are calculated, none measured.
2. Direct beam is derived from KT = 0.72, not from site data.
3. No wind, no shading between troughs, no soiling model.
4. Insulation conductivity is taken at a single temperature, not integrated.
5. The model has no cost side.

## Prototype P1 (bench store, 12 L)

The first physical test is a 12 L bench store — see the P1 prototype document
for dimensions, thermocouple placement, test protocol (T1–T6), and predicted
curves.  P1 validates the salt store and insulation independently of any
collector, so it can proceed before the troughs are built.

## Licence

Code: MIT. Output files: CC BY 4.0. – M. A. S. Elwasela, 2026
