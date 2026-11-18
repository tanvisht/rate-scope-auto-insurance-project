"""Static PNG charts mirroring the Tableau dashboards (for README / slides)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ratescope import benchmark  # noqa: E402
from ratescope.warehouse import query  # noqa: E402


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def state_overview(conn, out):
    st = benchmark.state_summary(conn).sort_values("state")
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(st))
    ax1.bar(x, st["market_loss_ratio_5yr"] * 100, color="#4C78A8", label="5-yr market loss ratio")
    ax1.set_ylabel("Loss ratio (%)")
    ax1.set_xticks(x, st["state"])
    ax2 = ax1.twinx()
    ax2.plot(x, st["avg_filed_rate_change_pct"], "o-", color="#F58518", label="Avg filed rate change")
    ax2.set_ylabel("Avg filed rate change (%)")
    ax1.set_title("Which states run hottest, and how hard are carriers pricing?")
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.88), fontsize=8)
    return _save(fig, out / "chart_state_overview.png")


def rate_vs_loss(conn, out):
    df = query(conn, "SELECT * FROM v_rate_vs_loss WHERE rate_filings > 0")
    fig, ax = plt.subplots(figsize=(7, 5))
    for st, g in df.groupby("state"):
        ax.scatter(g["prior_year_loss_ratio"] * 100, g["rate_change_pct"], label=st, alpha=0.75, s=28)
    m, b = np.polyfit(df["prior_year_loss_ratio"] * 100, df["rate_change_pct"], 1)
    xs = np.linspace(df["prior_year_loss_ratio"].min() * 100, df["prior_year_loss_ratio"].max() * 100, 50)
    ax.plot(xs, m * xs + b, "k--", lw=1)
    r = benchmark.rate_vs_loss_correlation(conn)["pearson_r"]
    ax.set(xlabel="Prior-year loss ratio (%)", ylabel="Next-year filed rate change (%)",
           title=f"Who files the biggest increases after a bad year? (r = {r})")
    ax.legend(title="State", fontsize=8)
    return _save(fig, out / "chart_rate_vs_loss.png")


def coverage_heatmap(conn, out, state="TX"):
    m = benchmark.coverage_matrix(conn, state)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.imshow(m.values, cmap="Blues", vmin=0, vmax=1.4, aspect="auto")
    ax.set_xticks(range(m.shape[1]), m.columns, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(m.shape[0]), m.index, fontsize=8)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ax.text(j, i, "✓" if m.values[i, j] else "–", ha="center", va="center", fontsize=9)
    ax.set_title(f"Coverage availability by carrier: {state}")
    return _save(fig, out / f"chart_coverage_{state}.png")


def build_all(conn, out):
    out.mkdir(parents=True, exist_ok=True)
    return [state_overview(conn, out), rate_vs_loss(conn, out), coverage_heatmap(conn, out)]
