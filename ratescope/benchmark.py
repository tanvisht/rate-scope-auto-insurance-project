"""Benchmark analytics on top of the SQL warehouse views."""
import numpy as np
import pandas as pd

from ratescope.warehouse import query


def coverage_matrix(conn, state=None) -> pd.DataFrame:
    sql = "SELECT * FROM v_coverage_matrix" + (" WHERE state = ?" if state else "")
    df = query(conn, sql, (state,) if state else ())
    return (df.pivot_table(index="canonical_name", columns="coverage_label",
                           values="filings_mentioning", aggfunc="sum", fill_value=0) > 0).astype(int)


def rate_vs_loss_correlation(conn) -> dict:
    df = query(conn, "SELECT * FROM v_rate_vs_loss WHERE rate_filings > 0")
    if len(df) < 3:
        return {"n": len(df), "pearson_r": None, "slope_pct_per_10pt_lr": None}
    r = float(np.corrcoef(df["prior_year_loss_ratio"], df["rate_change_pct"])[0, 1])
    slope = float(np.polyfit(df["prior_year_loss_ratio"], df["rate_change_pct"], 1)[0]) / 10
    return {"n": len(df), "pearson_r": round(r, 3), "slope_pct_per_10pt_lr": round(slope, 2)}


def state_summary(conn) -> pd.DataFrame:
    return query(conn, """
        SELECT l.state,
               ROUND(SUM(l.direct_losses_incurred)/SUM(l.direct_premium_earned), 4) AS market_loss_ratio_5yr,
               (SELECT ROUND(AVG(rate_change_pct),2) FROM v_rate_filings r WHERE r.state=l.state) AS avg_filed_rate_change_pct,
               (SELECT COUNT(*) FROM v_rate_filings r WHERE r.state=l.state) AS rate_filings
        FROM v_loss_ratio l GROUP BY l.state ORDER BY market_loss_ratio_5yr DESC""")


def scorecard(conn, state=None) -> pd.DataFrame:
    sql = "SELECT * FROM v_competitor_scorecard" + (" WHERE state = ?" if state else "")
    return query(conn, sql + " ORDER BY avg_market_share DESC", (state,) if state else ())


def parse_quality(filings: pd.DataFrame) -> dict:
    rate = filings[filings["filing_type"].str.contains("Rate")]
    return {
        "filings": len(filings),
        "rate_change_parsed_pct": float(round(100 * rate["rate_change_pct"].notna().mean(), 1)),
        "effective_date_parsed_pct": float(round(100 * filings["effective_date"].notna().mean(), 1)),
        "naic_resolved_pct": float(round(100 * filings["naic_company_code"].notna().mean(), 1)),
        "fuzzy_matched": int((filings["naic_resolved_by"] == "fuzzy_name").sum()),
    }
