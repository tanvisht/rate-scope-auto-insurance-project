from ratescope import benchmark, generate_sample, pipeline
from ratescope.warehouse import query


def test_end_to_end(tmp_path):
    raw, out = tmp_path / "raw", tmp_path / "out"
    generate_sample.generate(seed=7, out_dir=raw)
    conn, quality = pipeline.run(raw, out, out / "t.db", verbose=False)
    assert quality["naic_resolved_pct"] >= 95
    assert quality["rate_change_parsed_pct"] >= 95
    states = set(query(conn, "SELECT DISTINCT state FROM v_loss_ratio")["state"])
    assert states == {"CA", "TX", "FL", "NY", "IL", "GA"}
    lr = query(conn, "SELECT loss_ratio FROM v_loss_ratio")["loss_ratio"]
    assert lr.between(0, 2).all()
    assert (out / "RateScope_Benchmark.xlsx").exists()
    assert len(list(out.glob("tableau_*.csv"))) == 5
    assert benchmark.rate_vs_loss_correlation(conn)["pearson_r"] > 0
