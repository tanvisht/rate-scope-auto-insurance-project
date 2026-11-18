"""Tableau-ready CSV extracts, Excel benchmark workbook, and markdown summary."""
import pandas as pd

from ratescope import benchmark
from ratescope.warehouse import query

TABLEAU_VIEWS = {
    "tableau_rate_filings.csv": "SELECT serff_tracking_number, canonical_name, state, state_name, filing_type, "
                                "effective_date, effective_year, rate_change_pct, indicated_change_pct, "
                                "impact_min_pct, impact_max_pct FROM v_rate_filings",
    "tableau_coverage_matrix.csv": "SELECT * FROM v_coverage_matrix",
    "tableau_loss_ratio.csv": "SELECT * FROM v_loss_ratio",
    "tableau_rate_vs_loss.csv": "SELECT * FROM v_rate_vs_loss",
    "tableau_scorecard.csv": "SELECT * FROM v_competitor_scorecard",
}


def export_tableau(conn, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, sql in TABLEAU_VIEWS.items():
        p = out_dir / name
        query(conn, sql).to_csv(p, index=False)
        paths.append(p)
    return paths


def export_excel(conn, out_path, quality):
    with pd.ExcelWriter(out_path, engine="openpyxl") as xw:
        pd.DataFrame(quality.items(), columns=["metric", "value"]).to_excel(xw, sheet_name="README", index=False)
        benchmark.state_summary(conn).to_excel(xw, sheet_name="State Summary", index=False)
        benchmark.scorecard(conn).to_excel(xw, sheet_name="Competitor Scorecard", index=False)
        benchmark.coverage_matrix(conn).to_excel(xw, sheet_name="Coverage Matrix")
        query(conn, "SELECT * FROM v_rate_by_year").to_excel(xw, sheet_name="Rate by Year", index=False)
        lr = query(conn, "SELECT canonical_name, state, year, loss_ratio FROM v_loss_ratio")
        lr.pivot_table(index=["canonical_name", "state"], columns="year", values="loss_ratio").round(3) \
          .to_excel(xw, sheet_name="Loss Ratio Trend")
        for ws in xw.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(
                    45, max(10, max(len(str(c.value or "")) for c in col) + 2))
    return out_path


def write_summary(conn, out_path, quality):
    st = benchmark.state_summary(conn)
    corr = benchmark.rate_vs_loss_correlation(conn)
    sc = benchmark.scorecard(conn)
    worst = sc.sort_values("loss_ratio_5yr", ascending=False).head(5)
    lines = [
        "# RateScope Benchmark Summary", "",
        "## Pipeline quality",
        *[f"- **{k}**: {v}" for k, v in quality.items()], "",
        "## State market view",
        st.to_markdown(index=False), "",
        "## Rate adequacy signal",
        f"Across {corr['n']} carrier-state-years with rate filings, prior-year loss ratio vs. next-year "
        f"filed rate change has Pearson r = **{corr['pearson_r']}**; each +10 pts of loss ratio is "
        f"associated with **{corr['slope_pct_per_10pt_lr']:+} pts** of filed rate.", "",
        "## Highest 5-year loss ratios (carrier x state)",
        worst[["canonical_name", "state", "loss_ratio_5yr", "cumulative_rate_change_pct"]].to_markdown(index=False),
    ]
    out_path.write_text("\n".join(lines) + "\n")
    return out_path
