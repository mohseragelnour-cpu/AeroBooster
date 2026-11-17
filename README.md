# AeroBooster — open solar-thermal cooking and heating

Design studies, simulation models, an interactive scenario simulator and the first prototype (P1)
specification for **AeroBooster**: a household and communal solar cooking and heating system
built around a nitrate-salt heat store and a dual-window control rule.

- Inventor: **Mohammed Abdelhameed Seragelnour Elwasela** — ORCID [0009-0005-5622-0760](https://orcid.org/0009-0005-5622-0760)
- Filed invention: international patent application **PCT/IB2026/062276** (filed 11 November 2026),
  published openly on Zenodo: [10.5281/zenodo.24154141](https://doi.org/10.5281/zenodo.24154141) (version 1, filed documents)
- This release on Zenodo: [10.5281/zenodo.24250456](https://doi.org/10.5281/zenodo.24250456) (version 2, Revision B / C.3)
- Live simulator: https://mohseragelnour-cpu.github.io/AeroBooster/
- Humanitarian-use pledge: see [PLEDGE.md](PLEDGE.md)

> **Status.** Everything here is designed and simulated. **No prototype has been built or measured yet.**
> The P1 bench store in `prototype/` is the first planned physical test.

> **Relation to the filed application.** The filed application describes a non-tracking
> concentrator embodiment. Revision B (tracked parabolic troughs) and Revision C (photovoltaic
> charging) are later design studies published here as open technical disclosures. They add to the
> public record; they do not amend the filed application. Where they differ, the filed documents
> define the claimed invention.

## Try the simulator

Open `simulator/index.html` in any modern browser — it is one self-contained file and runs offline.
With an internet connection it can also load climate data for any location from NASA POWER.
The same file is served at `docs/index.html` for GitHub Pages.

## Contents

| Folder | What it holds |
|---|---|
| `articles/` | Revision B article with the C.3 addendum, English and Arabic (PDF and DOCX) |
| `model/` | Revision B Python model (`modelB.py`), the archived base model, run files `runB`–`runB7` and their outputs |
| `revC/` | Revision C annual smart-use model (PV path), run files and outputs |
| `simulator/` | Interactive scenario simulator (`index.html`) and its JavaScript sources |
| `prototype/` | P1 bench-store predictions and manufacturing-drawing prompts |
| `drawings/` | Revision B engineering drawings (8 figures) |
| `prompts/` | Image-generation prompts used for the illustrations |

## Reproducing the results

Python 3.10+ with the standard library only (charts need `matplotlib`). Node.js for the simulator sources.

```bash
cd model && python3 runB7.py        # C.3 insulation study
cd revC  && python3 runC.py         # Revision C configurations
cd prototype && node predict.js     # P1 predictions
cd simulator/src && node build.js   # rebuilds simulator/src/dist/index.html
```

Run files `runB`–`runB6` reproduce the published `*_out.txt` files exactly.

## Key numbers (Revision C.3, simulated)

| Item | Value |
|---|---|
| Home store | 45 L solar salt (60/40 NaNO₃/KNO₃), 200 mm rock wool, G ≈ 0.49 W/K |
| Home PV path | 6.5 m² PV (≈1.4 kWp) + 2 m² flat water collector + 120 L water tank |
| Dual-window rule | upper 245 °C, lower 140 °C, gate 08:00–20:00, ΔT 15 K, tank max 75 °C |
| Bake power density | 4.8 kW/m² (home kisra), 5.3 kW/m² (communal) |
| P1 bench store | 12 L salt, ⌀300 × 200 mm, 1 kW heater, 7 thermocouples, ≈ USD 480 in parts |

## Licences

- **Code** (`*.py`, `*.js`, `simulator/`, `docs/`): MIT — see [LICENSE](LICENSE).
- **Documents, drawings, images and data**: CC BY 4.0 — see [LICENSE-docs.md](LICENSE-docs.md).
- The humanitarian-use pledge in [PLEDGE.md](PLEDGE.md) applies to the filed patent application.

## v3.0.0 — P1-B build pack, sourcing catalogue and improvements (Nov 2026)

Everything needed to build and measure the P1-B bench prototype, plus performance improvements documented
against the prior art. All figures are simulation outputs, not measurements, pending the bench tests.

- `prototype/p1b/AeroBooster_P1B_Manufacturing.pdf` — build spec: two fills (P1-S salt / P1-X iron+sand),
  the four corrections, the simplified P1-X build and the first-heat moisture vent, BOM, tests T1–T6.
- `drawings/AeroBooster_P1B_Drawings.pdf` — 9 engineering sheets (incl. the P1-X fill arrangement + vent).
- `prototype/p1b/AeroBooster_P1B_Purchase_List.xlsx` — costed purchase list for both fills.
- `prototype/p1b/AeroBooster_P1B_Sourcing_Catalogue.pdf` (+ `AeroBooster_P1B_Catalogue_source.zip`) — 16
  components with specs and live supplier links, region-neutral, for anyone building the prototype.
- `articles/AeroBooster_Improvements_over_PriorArt.pdf` — insulation, dry-store high-temperature operation,
  contact-conductance and dual-input charging, each cited to prior art and quantified by simulation.
- `model/p1_media.py`, `model/pv_direct.py`, `model/storage_time.py` — storage-media comparison, PV-direct
  matching, and the storage-time / peak-temperature experiment.

**Acknowledgement of prior art.** AeroBooster does not originate electric/PV-charged thermal-storage
cooking. It builds on and cites existing work (NTNU / Morpho Solar with A. H. Tesfay; Ghana sand storage;
Uganda rock storage; Ethiopian electric-*mitad* research); the improvements document lists the citations.
Its contribution is the specific engineering integration and the documented improvements.

## Citation

See [CITATION.cff](CITATION.cff). Contact: mohseragelnour@gmail.com

---

## بالعربية

**AeroBooster** نظام مفتوح للطهي والتدفئة بالطاقة الشمسية، يعتمد على مخزن حراري من أملاح النترات
وقاعدة تحكم بنافذتين. يضم هذا المستودع دراسات التصميم ونماذج المحاكاة بلغة بايثون، ومحاكي
السيناريوهات التفاعلي، ومواصفات النموذج الأولي P1.

- **Zenodo:** الإصدار الأول (الوثائق المودعة) 10.5281/zenodo.24154141، والإصدار الثاني (النسخة B وC.3) 10.5281/zenodo.24250456.
- **المحاكي على الإنترنت:** https://mohseragelnour-cpu.github.io/AeroBooster/
- **الحالة:** كل ما هنا مصمم ومُحاكى حاسوبيًا، **ولم يُبنَ أي نموذج ولم يُقَس شيء بعد.**
- **العلاقة بالطلب المودَع:** يصف طلب PCT/IB2026/062276 تجسيدًا بمركّز ثابت. أما النسخة B
  (أحواض متتبعة) والنسخة C (شحن بالألواح الكهروضوئية) فدراسات تصميم لاحقة منشورة هنا كشفًا
  تقنيًا مفتوحًا، ولا تعدّل الطلب المودَع. وعند الاختلاف تكون الوثائق المودَعة هي المرجع.
- **المحاكي:** افتح `simulator/index.html` في أي متصفح، يعمل دون إنترنت.
- **التراخيص:** الكود بترخيص MIT، والوثائق والرسوم والصور بترخيص CC BY 4.0، وتعهد الاستعمال
  الإنساني في `PLEDGE.md`.
