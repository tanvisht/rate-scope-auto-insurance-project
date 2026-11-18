-- Benchmarking views consumed by Tableau / Excel exports

DROP VIEW IF EXISTS v_rate_filings;
CREATE VIEW v_rate_filings AS
SELECT f.*, c.canonical_name, s.state_name
FROM fact_filing f
JOIN dim_company c USING (naic_company_code)
JOIN dim_state  s ON s.state_code = f.state
WHERE f.disposition IN ('Approved', 'Filed')
  AND f.filing_type LIKE '%Rate%'
  AND f.rate_change_pct IS NOT NULL;

-- Coverage availability matrix: carrier x state x coverage
DROP VIEW IF EXISTS v_coverage_matrix;
CREATE VIEW v_coverage_matrix AS
SELECT c.canonical_name, f.state, b.coverage_code, dc.coverage_label,
       COUNT(DISTINCT f.serff_tracking_number) AS filings_mentioning,
       MAX(f.max_liability_limit)              AS max_liability_limit
FROM bridge_filing_coverage b
JOIN fact_filing f  USING (serff_tracking_number)
JOIN dim_company c  USING (naic_company_code)
JOIN dim_coverage dc USING (coverage_code)
WHERE f.disposition <> 'Withdrawn'
GROUP BY c.canonical_name, f.state, b.coverage_code, dc.coverage_label;

-- Annual rate action per carrier/state (compounded when multiple filings in a year)
DROP VIEW IF EXISTS v_rate_by_year;
CREATE VIEW v_rate_by_year AS
SELECT canonical_name, naic_company_code, state, effective_year AS year,
       COUNT(*)                         AS rate_filings,
       ROUND(AVG(rate_change_pct), 2)   AS avg_rate_change_pct,
       ROUND((EXP(SUM(LN(1 + rate_change_pct / 100.0))) - 1) * 100, 2) AS compounded_rate_change_pct
FROM v_rate_filings
GROUP BY canonical_name, naic_company_code, state, effective_year;

-- Loss ratio per carrier/state/year, with state market benchmark
DROP VIEW IF EXISTS v_loss_ratio;
CREATE VIEW v_loss_ratio AS
WITH lr AS (
    SELECT e.naic_company_code, c.canonical_name, e.state, e.year,
           e.direct_premium_earned, e.direct_losses_incurred,
           e.direct_losses_incurred * 1.0 / NULLIF(e.direct_premium_earned, 0) AS loss_ratio
    FROM fact_experience e JOIN dim_company c USING (naic_company_code)
), mkt AS (
    SELECT state, year,
           SUM(direct_losses_incurred) * 1.0 / SUM(direct_premium_earned) AS market_loss_ratio,
           SUM(direct_premium_earned) AS market_premium
    FROM fact_experience GROUP BY state, year
)
SELECT lr.*, mkt.market_loss_ratio,
       lr.loss_ratio - mkt.market_loss_ratio            AS lr_vs_market,
       lr.direct_premium_earned / mkt.market_premium     AS market_share
FROM lr JOIN mkt USING (state, year);

-- Did carriers price for their loss experience? Prior-year LR vs current-year rate action
DROP VIEW IF EXISTS v_rate_vs_loss;
CREATE VIEW v_rate_vs_loss AS
SELECT l.canonical_name, l.state, l.year AS experience_year, r.year AS rate_year,
       ROUND(l.loss_ratio, 4) AS prior_year_loss_ratio,
       ROUND(l.lr_vs_market, 4) AS prior_lr_vs_market,
       COALESCE(r.compounded_rate_change_pct, 0) AS rate_change_pct,
       COALESCE(r.rate_filings, 0) AS rate_filings
FROM v_loss_ratio l
LEFT JOIN v_rate_by_year r
  ON r.naic_company_code = l.naic_company_code AND r.state = l.state AND r.year = l.year + 1
WHERE l.year < (SELECT MAX(year) FROM fact_experience);

-- One-row-per-carrier/state scorecard
DROP VIEW IF EXISTS v_competitor_scorecard;
CREATE VIEW v_competitor_scorecard AS
SELECT l.canonical_name, l.state,
       ROUND(SUM(l.direct_losses_incurred) / SUM(l.direct_premium_earned), 4) AS loss_ratio_5yr,
       ROUND(AVG(l.market_share), 4) AS avg_market_share,
       (SELECT COUNT(*) FROM v_rate_filings r
         WHERE r.naic_company_code = l.naic_company_code AND r.state = l.state) AS rate_filings,
       (SELECT ROUND((EXP(SUM(LN(1 + rate_change_pct / 100.0))) - 1) * 100, 2) FROM v_rate_filings r
         WHERE r.naic_company_code = l.naic_company_code AND r.state = l.state) AS cumulative_rate_change_pct,
       (SELECT COUNT(DISTINCT coverage_code) FROM bridge_filing_coverage b
          JOIN fact_filing f USING (serff_tracking_number)
         WHERE f.naic_company_code = l.naic_company_code AND f.state = l.state) AS coverages_filed
FROM v_loss_ratio l
GROUP BY l.canonical_name, l.naic_company_code, l.state;
