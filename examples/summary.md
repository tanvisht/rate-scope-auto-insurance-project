# RateScope Benchmark Summary

## Pipeline quality
- **filings**: 260
- **rate_change_parsed_pct**: 100.0
- **effective_date_parsed_pct**: 100.0
- **naic_resolved_pct**: 100.0
- **fuzzy_matched**: 43

## State market view
| state   |   market_loss_ratio_5yr |   avg_filed_rate_change_pct |   rate_filings |
|:--------|------------------------:|----------------------------:|---------------:|
| NY      |                  0.6878 |                        6.77 |             24 |
| GA      |                  0.6765 |                        4.38 |             23 |
| CA      |                  0.6646 |                        4.08 |             18 |
| FL      |                  0.6591 |                        7.5  |             24 |
| IL      |                  0.6521 |                        3.69 |             21 |
| TX      |                  0.5997 |                        1.72 |             21 |

## Rate adequacy signal
Across 89 carrier-state-years with rate filings, prior-year loss ratio vs. next-year filed rate change has Pearson r = **0.849**; each +10 pts of loss ratio is associated with **+7.25 pts** of filed rate.

## Highest 5-year loss ratios (carrier x state)
| canonical_name               | state   |   loss_ratio_5yr |   cumulative_rate_change_pct |
|:-----------------------------|:--------|-----------------:|-----------------------------:|
| Northstar Commercial Ins Co  | FL      |           0.8689 |                        59.51 |
| Harbor State Indemnity       | CA      |           0.8412 |                       nan    |
| Meridian Auto Underwriters   | NY      |           0.7836 |                        41.69 |
| Keystone Commercial Casualty | NY      |           0.779  |                        40.04 |
| Meridian Auto Underwriters   | GA      |           0.7775 |                        36.83 |
