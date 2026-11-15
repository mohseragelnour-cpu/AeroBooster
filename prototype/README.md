# Prototype P1 — bench salt store

The first physical test of AeroBooster. It checks the salt store, its insulation and the baking plate
on mains power, before any collector is built. **Not yet built; all numbers below are predictions.**

## Specification

| Item | Value |
|---|---|
| Vessel | ⌀300 × 200 mm, 3 mm mild steel, flanged top |
| Salt | solar salt 60/40 NaNO₃/KNO₃, ≈20.5–23 kg, 10 % headspace (see note) |
| Heater | 1 kW cartridge heater, PID or on/off control, 260 °C thermostat cutout |
| Plate | cast-iron baking plate on the lid flange |
| Sensors | 7 × type-K thermocouples (salt centre, salt wall, plate centre, plate edge, mid-insulation, outer skin, ambient) |
| Insulation stages | A: 50 mm ceramic fibre · B: + 100 mm rock wool · C: + 50 mm rock wool |
| Parts cost | ≈ USD 480 |

## Tests (as in article section 11)

| Test | Procedure | Confirms |
|---|---|---|
| T1 | Full charge from 180 °C to 250 °C, heater energy metered | latent heat and total stored energy |
| T2 | Fully charged, insulated, no load; log every 60 s for 12 h | standby conductance G (W/K) |
| T3 | Plate at 220 °C, wet dough, time to cook through | contact heat flux (W/m²) |
| T4 | Draw 0.8 kWh through a coil or pot on the plate over 90 min | load delivery capacity |
| T5 | 20 charge/discharge cycles, then inspect | salt creep, weld stress, plate warping |
| T6 | Repeat T2 at each insulation stage | calibration of the model's G |

**Pass marks.** At least 1.0 kWh usable above 200 °C; a kisra baked within 3 minutes of the simulated time;
measured G at the final insulation stage within 20 % of the simulation. Failure at any stage stops the
project at that point.

## Predictions (`predict.js` → `predict_out.txt`)

| Rock wool equivalent | G (W/K) | Hold at 245 °C | 255 → 200 °C | 255 → 150 °C |
|---|---|---|---|---|
| 100 mm | 0.378 | 81 W | 14.9 h | 23.8 h |
| 150 mm | 0.305 | 66 W | 18.5 h | 29.6 h |
| 200 mm | 0.268 | 58 W | 21.0 h | 33.6 h |

Usable latent plus sensible energy between 200 and 255 °C is ≈1.04 kWh. Charging from 25 °C takes ≈2.8 kWh
(salt and steel). The home kisra flux of 4.8 kW/m² equals ≈340 W on a ⌀300 mm plate.

**Notes.** The article gives ≈23 kg of salt (12 L at solid density); `predict.js` assumes 90 % fill of
12 L, i.e. 20.5 kg. Weigh the salt actually loaded and use that mass when comparing T1 with prediction.
`predict.js` uses the full ⌀300 mm vessel area for the plate. The manufacturing drawings use a
⌀250 mm plate with a raised rim, whose area is about 30 % smaller. Compare T3 results per square metre,
not per plate.

## Manufacturing drawings

`AeroBooster_P1_blueprint_prompts_2026-11-15.txt` holds eight detailed drawing specifications: tank
general arrangement, section A-A, baking plate, insulated lid, insulation assembly, thermocouple layout,
heater installation, and the complete assembly with its bill of materials. They are written as prompts for
an image generator. Generated drawings are illustrations: check every dimension against the text before
cutting steel, and have a qualified fabricator review the welds and the heater installation.

**Safety.** Nitrate salt at 250 °C is a strong oxidiser and causes severe burns. Keep it away from
organic material and water. Wear a face shield and heat-resistant gloves. Never heat salt in a sealed
vessel; the headspace must vent.
