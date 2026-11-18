# Data Dictionary & Input Formats

Drop files into `data/raw/`. Any file matching `serff_*.csv` or `serff_*.json` is ingested as filings, and `naic_experience.csv` is ingested as experience.

## SERFF filing export (`serff_*.csv|json`)
| Column | Description |
|---|---|
| serff_tracking_number | SERFF tracking # (unique key) |
| state | 2-letter state code |
| company_name | Filing company name as shown on SERFF |
| naic_company_code | NAIC company code (may be blank; resolved by fuzzy name match) |
| product_name | Product / program name |
| type_of_insurance | TOI (e.g. 20.0 Commercial Auto) |
| filing_type | Rate, Rule, Form, or combinations |
| submission_date | YYYY-MM-DD |
| disposition | Approved / Filed / Withdrawn / Pending |
| filing_description | Free text from the filing summary or memo; parsed for rates, dates, coverages, and limits |

## NAIC experience (`naic_experience.csv`)
Commercial auto direct experience by company/state/year (State Page-style).
| Column | Description |
|---|---|
| naic_company_code, company_name, state, year | Keys |
| direct_premium_written / direct_premium_earned | USD |
| direct_losses_incurred | USD |
| direct_defense_cost_containment | USD (DCC) |

## Derived fields
- **rate_change_pct**: selected overall change; 0 for rule/form filings with no rate impact.
- **loss_ratio** = direct_losses_incurred / direct_premium_earned.
- **compounded_rate_change_pct** = (Π(1 + rᵢ) − 1) × 100 across filings in the period.
