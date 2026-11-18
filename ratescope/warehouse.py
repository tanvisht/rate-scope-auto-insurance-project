"""Load normalized data into SQLite and materialize benchmarking views."""
import math
import sqlite3
from pathlib import Path

import pandas as pd

from ratescope.config import COVERAGE_LABELS, SQL_DIR, STATES


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.create_function("LN", 1, lambda x: math.log(x) if x and x > 0 else None)
    conn.create_function("EXP", 1, lambda x: math.exp(x) if x is not None else None)
    return conn


def build(conn, filings: pd.DataFrame, coverage_bridge: pd.DataFrame,
          experience: pd.DataFrame, company_dim: pd.DataFrame) -> None:
    conn.executescript((SQL_DIR / "schema.sql").read_text())
    pd.DataFrame(STATES.items(), columns=["state_code", "state_name"]).to_sql(
        "dim_state", conn, if_exists="append", index=False)
    company_dim[["naic_company_code", "canonical_name", "clean_name"]].to_sql(
        "dim_company", conn, if_exists="append", index=False)
    pd.DataFrame(COVERAGE_LABELS.items(), columns=["coverage_code", "coverage_label"]).to_sql(
        "dim_coverage", conn, if_exists="append", index=False)

    cols = ["serff_tracking_number", "state", "naic_company_code", "naic_resolved_by", "product_name",
            "filing_type", "disposition", "submission_date", "effective_date", "effective_year",
            "rate_change_pct", "indicated_change_pct", "impact_min_pct", "impact_max_pct",
            "max_liability_limit", "filing_description"]
    f = filings.rename(columns={"company_name": "company_name_raw"})
    f = f[f["naic_company_code"].notna()]
    f[cols + ["company_name_raw"]].to_sql("fact_filing", conn, if_exists="append", index=False)
    coverage_bridge[coverage_bridge["serff_tracking_number"].isin(f["serff_tracking_number"])][
        ["serff_tracking_number", "coverage_code"]].drop_duplicates().to_sql(
        "bridge_filing_coverage", conn, if_exists="append", index=False)

    exp_cols = ["naic_company_code", "state", "year", "direct_premium_written", "direct_premium_earned",
                "direct_losses_incurred", "direct_defense_cost_containment"]
    exp = experience.reindex(columns=exp_cols)
    exp.groupby(["naic_company_code", "state", "year"], as_index=False).sum().to_sql(
        "fact_experience", conn, if_exists="append", index=False)

    conn.executescript((SQL_DIR / "views.sql").read_text())
    conn.commit()


def query(conn, sql: str, params=()) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)
