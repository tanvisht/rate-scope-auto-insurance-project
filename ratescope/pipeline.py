"""End-to-end orchestration."""
from ratescope import benchmark, export, ingest, normalize, warehouse
from ratescope.config import DB_PATH, PROCESSED_DIR, RAW_DIR


def run(raw_dir=RAW_DIR, out_dir=PROCESSED_DIR, db_path=DB_PATH, verbose=True):
    log = print if verbose else (lambda *a: None)
    filings = ingest.load_filings(raw_dir)
    experience = ingest.load_experience(raw_dir)
    log(f"[ingest]    {len(filings)} filings, {len(experience)} experience rows")

    company_dim = normalize.build_company_dim(experience)
    filings = normalize.normalize_filings(filings, company_dim)
    bridge = normalize.explode_coverages(filings)
    quality = benchmark.parse_quality(filings)
    log(f"[parse]     {quality}")

    if db_path.exists():
        db_path.unlink()
    conn = warehouse.connect(db_path)
    warehouse.build(conn, filings, bridge, experience, company_dim)
    log(f"[warehouse] {db_path}")

    export.export_tableau(conn, out_dir)
    export.export_excel(conn, out_dir / "RateScope_Benchmark.xlsx", quality)
    export.write_summary(conn, out_dir / "summary.md", quality)
    try:
        from ratescope import charts
        charts.build_all(conn, out_dir.parent.parent / "docs" / "images" if out_dir.name == "processed" else out_dir)
        log("[charts]    PNG charts written")
    except ImportError:
        log("[charts]    matplotlib not installed; skipping charts")
    log(f"[export]    Tableau CSVs, Excel workbook, summary.md -> {out_dir}")
    return conn, quality
