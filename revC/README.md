# AeroBooster v2 – Revision C: smart-use annual model

15 November 2026. CC BY 4.0, with the humanitarian pledge of the first Zenodo record (DOI 10.5281/zenodo.24154141).
All results are calculated from synthetic weather; nothing is measured.

| File | Content |
|---|---|
| aerobooster_revC_model.py | Self-contained model (Python 3, standard library only). Run it to check one case. |
| runC.py / runC_out.txt | The ten configurations in the release document, section 6. |
| runC2.py / runC2_out.txt | Thresholds, kisra every day, surplus uses off, other weather years, annual energy flows. |
| chartsC.py | Makes chart_service.png and chart_store_year.png (needs matplotlib). |

Configure a case with `Config(...)`: trough_m2, receiver, pv_m2, store_l, eg_frac, thr_hi, thr_lo,
kisra_per_week, oven_per_week, bonus, seed. `summary(run(cfg))` returns the service shares and energy flows.
The salt-store energy balance is printed as `bal` and should be about zero.

**Note on outputs (15 November 2026).** `runC_out.txt` and `runC2_out.txt` were regenerated from the model
as published here, which includes the C.1 correction. Some service shares differ by 1–6 points from the
first Revision C table. `runC1_compare_out.txt` shows the before/after comparison. The C.3 insulation
correction (G ≈ 0.49 W/K with 200 mm rock wool) is studied in `../model/runB7.py`.
