# RateScope: Commercial Auto Product & Filing Analyzer

**Python · SQL · Tableau · Excel**

RateScope turns public commercial auto insurance filings into a benchmarking dataset that analysts can explore. It parses rate/rule/form filings in the style of **SERFF** (System for Electronic Rates & Forms Filing) and annual statement experience in the style of the **NAIC** across **6 states (CA, TX, FL, NY, IL, GA)**. It loads them into a SQL warehouse and exports Tableau-ready extracts plus an Excel workbook that compares **coverages, rate changes, and loss ratios** across competitors.

---

## Why this exists

I interviewed **15 insurance product, actuarial, and compliance professionals**. The same pain point kept coming up: **competitor research means hours of manual filing review**. Analysts download PDFs one at a time from state SERFF portals, then copy rate changes, effective dates, and coverage changes into spreadsheets by hand, and finally try to line them up against NAIC loss experience.

RateScope automates that workflow end to end:

| Manual process | RateScope |
|---|---|
| Search each state's SERFF portal by hand | Batch ingest of filing exports (CSV/JSON/HTML summaries) |
| Copy rate change %, effective dates, and coverages into Excel | Regex- and rule-based parser normalizes fields |
| Reconcile company names across filings and NAIC data | Entity resolution on NAIC company codes and fuzzy names |
| Build pivot tables per state | SQL views and Tableau extracts, refreshed in one command |

**Result:** about **40% less competitor research time** in user testing, with findings presented to **20+ non-technical peers**.

---

## Architecture

```
 SERFF filing exports ─┐
 (rate / rule / form)  │     ┌────────────┐    ┌──────────────┐    ┌──────────────────┐
                       ├──▶  │  ingest/   │──▶ │  parse &     │──▶ │  SQLite / SQL    │
 NAIC experience data ─┘     │  loaders   │    │  normalize   │    │  warehouse       │
 (premium, losses)           └────────────┘    └──────────────┘    └────────┬─────────┘
                                                                            │ SQL views
                                                    ┌───────────────────────┼──────────────────┐
                                                    ▼                       ▼                  ▼
                                            Tableau extracts        Excel benchmark       CLI reports
                                            (data/processed/*.csv)  workbook (.xlsx)      (markdown)
```

## Repository layout

```
RateScope/
├── ratescope/
│   ├── config.py          # states, coverage taxonomy, paths
│   ├── generate_sample.py # builds a representative sample dataset (see Data note)
│   ├── ingest.py          # loaders for SERFF filing + NAIC experience files
│   ├── parser.py          # extracts rate change %, coverages, limits, dates from filing text
│   ├── normalize.py       # company entity resolution, coverage mapping
│   ├── warehouse.py       # SQLite load + runs SQL views
│   ├── benchmark.py       # coverage / rate / loss ratio benchmarking logic
│   ├── export.py          # Tableau CSV extracts + Excel workbook
│   ├── pipeline.py        # end-to-end orchestration
│   └── cli.py             # `python -m ratescope run`
├── sql/
│   ├── schema.sql         # star schema: dim_company, dim_state, fact_filing, fact_experience
│   └── views.sql          # benchmarking views consumed by Tableau
├── dashboards/
│   └── TABLEAU_GUIDE.md   # dashboard spec: sheets, calcs, filters
├── docs/
│   ├── user_research.md   # interview synthesis (15 professionals)
│   └── data_dictionary.md
├── data/raw/              # input files (sample data generated here)
├── data/processed/        # Tableau extracts + Excel output
└── tests/
```

## Quickstart

```bash
git clone https://github.com/tanvisht/rate-scope-auto-insurance-project.git
cd rate-scope-auto-insurance-project
pip install -r requirements.txt

# 1. generate the representative sample data (or drop real exports into data/raw/)
python -m ratescope sample

# 2. full pipeline: ingest → parse → normalize → SQL warehouse → benchmarks → exports
python -m ratescope run

# 3. quick terminal benchmark for one state
python -m ratescope report --state TX
```

Outputs:
- `data/processed/ratescope.db`: SQLite warehouse with views
- `data/processed/tableau_*.csv`: extracts for the Tableau dashboard
- `data/processed/RateScope_Benchmark.xlsx`: Excel workbook for non-technical stakeholders
- `data/processed/summary.md`: headline findings

## What gets benchmarked

1. **Coverages**: which carriers offer which commercial auto coverages (Liability, Physical Damage, UM/UIM, Med Pay/PIP, Hired & Non-Owned, Cargo, and others), plus limit ranges per state.
2. **Rates**: filed overall rate change %, filing cadence, and cumulative rate change by carrier and state.
3. **Loss ratios**: direct incurred loss ratio (incurred losses ÷ earned premium) from NAIC-style experience, compared with each carrier's rate actions. Did carriers with deteriorating loss ratios file for bigger increases?

## Data note

SERFF Filing Access and NAIC statement data are public, but they are served through state portals and licensed products with no bulk open API, and their terms limit redistribution. This repo therefore **ships no scraped filings**. `ratescope/generate_sample.py` creates a **representative sample dataset** with the same fields and structure (SERFF tracking numbers, filing text snippets, NAIC company codes, premium/loss columns), so you can run the pipeline end to end. To use real data, export filings or experience tables in the documented format (see `docs/data_dictionary.md`), place them in `data/raw/`, and run `python -m ratescope run`.

## Sample output (representative dataset)

| State | 5-yr market loss ratio | Avg filed rate change | Rate filings |
|---|---|---|---|
| NY | 68.8% | +6.8% | 24 |
| GA | 67.7% | +4.4% | 23 |
| CA | 66.5% | +4.1% | 18 |
| FL | 65.9% | +7.5% | 24 |
| IL | 65.2% | +3.7% | 21 |
| TX | 60.0% | +1.7% | 21 |

- Parser extracted rate change and effective date from **100%** of the sample's rate filings. **43** filings that had no NAIC code were resolved by fuzzy name matching.
- **Rate adequacy signal:** in the sample, prior-year loss ratio correlates with next-year filed rate change at **r = 0.85**. Each +10 pts of loss ratio goes with about **+7 pts** of filed rate.

## Tests

```bash
pytest -q
```

## License

MIT
