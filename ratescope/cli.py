"""Command line interface: `python -m ratescope {sample,run,report}`."""
import argparse

from ratescope import benchmark, generate_sample, pipeline, warehouse
from ratescope.config import DB_PATH, STATES


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ratescope", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample", help="generate representative sample data in data/raw")
    s.add_argument("--seed", type=int, default=42)
    sub.add_parser("run", help="run full pipeline")
    r = sub.add_parser("report", help="print a benchmark for one state")
    r.add_argument("--state", choices=list(STATES), required=True)
    args = ap.parse_args(argv)

    if args.cmd == "sample":
        nf, ne = generate_sample.generate(args.seed)
        print(f"Generated {nf} filings and {ne} experience rows in data/raw/")
    elif args.cmd == "run":
        pipeline.run()
    elif args.cmd == "report":
        if not DB_PATH.exists():
            pipeline.run(verbose=False)
        conn = warehouse.connect(DB_PATH)
        print(f"\n=== {STATES[args.state]} competitor scorecard ===")
        print(benchmark.scorecard(conn, args.state).to_string(index=False))
        print("\n=== Coverage availability (1 = filed) ===")
        print(benchmark.coverage_matrix(conn, args.state).to_string())


if __name__ == "__main__":
    main()
