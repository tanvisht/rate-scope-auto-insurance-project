-- RateScope star schema (SQLite dialect, portable to Postgres with minor edits)
DROP TABLE IF EXISTS dim_state;
DROP TABLE IF EXISTS dim_company;
DROP TABLE IF EXISTS dim_coverage;
DROP TABLE IF EXISTS fact_filing;
DROP TABLE IF EXISTS bridge_filing_coverage;
DROP TABLE IF EXISTS fact_experience;

CREATE TABLE dim_state (
    state_code TEXT PRIMARY KEY,
    state_name TEXT NOT NULL
);

CREATE TABLE dim_company (
    naic_company_code TEXT PRIMARY KEY,
    canonical_name    TEXT NOT NULL,
    clean_name        TEXT
);

CREATE TABLE dim_coverage (
    coverage_code  TEXT PRIMARY KEY,
    coverage_label TEXT NOT NULL
);

CREATE TABLE fact_filing (
    serff_tracking_number TEXT PRIMARY KEY,
    state                 TEXT REFERENCES dim_state(state_code),
    naic_company_code     TEXT REFERENCES dim_company(naic_company_code),
    company_name_raw      TEXT,
    naic_resolved_by      TEXT,
    product_name          TEXT,
    filing_type           TEXT,
    disposition           TEXT,
    submission_date       TEXT,
    effective_date        TEXT,
    effective_year        INTEGER,
    rate_change_pct       REAL,
    indicated_change_pct  REAL,
    impact_min_pct        REAL,
    impact_max_pct        REAL,
    max_liability_limit   INTEGER,
    filing_description    TEXT
);

CREATE TABLE bridge_filing_coverage (
    serff_tracking_number TEXT REFERENCES fact_filing(serff_tracking_number),
    coverage_code         TEXT REFERENCES dim_coverage(coverage_code),
    PRIMARY KEY (serff_tracking_number, coverage_code)
);

CREATE TABLE fact_experience (
    naic_company_code     TEXT REFERENCES dim_company(naic_company_code),
    state                 TEXT REFERENCES dim_state(state_code),
    year                  INTEGER,
    direct_premium_written REAL,
    direct_premium_earned  REAL,
    direct_losses_incurred REAL,
    direct_defense_cost_containment REAL,
    PRIMARY KEY (naic_company_code, state, year)
);

CREATE INDEX ix_filing_state_co ON fact_filing(state, naic_company_code);
CREATE INDEX ix_exp_state_year  ON fact_experience(state, year);
