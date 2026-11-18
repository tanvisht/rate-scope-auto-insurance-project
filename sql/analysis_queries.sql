-- RateScope: example analyst queries (run against data/processed/ratescope.db)

-- 1. Largest approved rate increases in the last 2 years, by state
SELECT state, canonical_name, effective_date, rate_change_pct
FROM v_rate_filings
WHERE effective_year >= (SELECT MAX(effective_year) - 1 FROM v_rate_filings)
ORDER BY rate_change_pct DESC
LIMIT 15;

-- 2. Under-pricing risk: loss ratio well above market but rate cuts or no increase next year
SELECT canonical_name, state, experience_year, prior_year_loss_ratio, prior_lr_vs_market, rate_change_pct
FROM v_rate_vs_loss
WHERE prior_lr_vs_market > 0.05 AND rate_change_pct <= 0
ORDER BY prior_lr_vs_market DESC;

-- 3. Coverage gaps: coverages a carrier files in some states but not others
WITH offered AS (
    SELECT DISTINCT canonical_name, state, coverage_label FROM v_coverage_matrix
), carrier_cov AS (
    SELECT DISTINCT canonical_name, coverage_label FROM offered
), carrier_state AS (
    SELECT DISTINCT canonical_name, state FROM offered
)
SELECT cs.canonical_name, cs.state, cc.coverage_label AS missing_coverage
FROM carrier_state cs
JOIN carrier_cov cc USING (canonical_name)
LEFT JOIN offered o
  ON o.canonical_name = cs.canonical_name AND o.state = cs.state AND o.coverage_label = cc.coverage_label
WHERE o.coverage_label IS NULL
ORDER BY cs.canonical_name, cs.state;

-- 4. Filing cadence: average days between rate filings per carrier
WITH ordered AS (
    SELECT canonical_name, state, effective_date,
           LAG(effective_date) OVER (PARTITION BY canonical_name, state ORDER BY effective_date) AS prev_date
    FROM v_rate_filings
)
SELECT canonical_name, ROUND(AVG(julianday(effective_date) - julianday(prev_date)), 0) AS avg_days_between_filings
FROM ordered WHERE prev_date IS NOT NULL
GROUP BY canonical_name ORDER BY avg_days_between_filings;

-- 5. Market share leaders by state (latest year)
SELECT state, canonical_name, ROUND(market_share * 100, 1) AS share_pct, ROUND(loss_ratio * 100, 1) AS lr_pct
FROM v_loss_ratio
WHERE year = (SELECT MAX(year) FROM v_loss_ratio)
ORDER BY state, market_share DESC;

-- 6. Selected vs. indicated: how much of the indication carriers actually take
SELECT canonical_name,
       ROUND(AVG(rate_change_pct), 2)      AS avg_selected,
       ROUND(AVG(indicated_change_pct), 2) AS avg_indicated,
       ROUND(AVG(rate_change_pct) / NULLIF(AVG(indicated_change_pct), 0), 2) AS selection_ratio
FROM v_rate_filings
WHERE indicated_change_pct IS NOT NULL
GROUP BY canonical_name;
