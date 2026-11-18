# RateScope Tableau Dashboard

Connect Tableau to the CSV extracts in `data/processed/` (or directly to `ratescope.db` via the SQLite ODBC driver).
Run `python -m ratescope run` to refresh, then use **Data → Refresh All Extracts**.

## Data sources
| Extract | Grain | Key fields |
|---|---|---|
| `tableau_rate_filings.csv` | one approved/filed rate filing | canonical_name, state, effective_date, rate_change_pct |
| `tableau_coverage_matrix.csv` | carrier × state × coverage | coverage_label, filings_mentioning, max_liability_limit |
| `tableau_loss_ratio.csv` | carrier × state × year | loss_ratio, market_loss_ratio, lr_vs_market, market_share |
| `tableau_rate_vs_loss.csv` | carrier × state × experience year | prior_year_loss_ratio, rate_change_pct (next year) |
| `tableau_scorecard.csv` | carrier × state | loss_ratio_5yr, cumulative_rate_change_pct, coverages_filed |

## Dashboard 1: Market Overview
- **Filled map** of states colored by 5-yr market loss ratio (`SUM(losses)/SUM(premium)`).
- **Bar chart**: average filed rate change by state.
- Filters: Year, Carrier (applies to all sheets).

## Dashboard 2: Coverage Benchmark
- **Highlight table**: Rows = canonical_name, Columns = coverage_label, Color = `IF SUM([filings_mentioning])>0 THEN "Offered" ELSE "Not filed" END`.
- Tooltip: max liability limit.
- State parameter control.

## Dashboard 3: Rate Actions
- **Timeline / Gantt**: effective_date by carrier, size = |rate_change_pct|, color = sign.
- **Line**: running compounded rate change.
  Calc `Rate Index` = `EXP(RUNNING_SUM(LN(1 + [rate_change_pct]/100)))`.

## Dashboard 4: Loss Ratio vs. Rate Adequacy
- **Scatter**: X = prior_year_loss_ratio, Y = rate_change_pct, color = state, with trend line (shows R²).
- **Line**: carrier loss_ratio vs. market_loss_ratio reference line by year.
- Callout: carriers with `lr_vs_market > 0.05` and rate change < 0 are flagged **"Under-pricing risk"**.

## Design notes for non-technical audiences
- Each sheet's title is phrased as a question ("Who files the biggest increases after a bad year?").
- Percentages shown with 1 decimal place; loss ratios as %, not decimals.
- No more than 3 colors per view; carriers limited to the top 8 by market share.
