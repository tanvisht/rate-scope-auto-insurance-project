"""Loaders for SERFF filing exports (CSV/JSON) and NAIC experience files."""
import json
from pathlib import Path

import pandas as pd

FILING_COLS = [
    "serff_tracking_number", "state", "company_name", "naic_company_code", "product_name",
    "type_of_insurance", "filing_type", "submission_date", "disposition", "filing_description",
]
EXPERIENCE_COLS = [
    "naic_company_code", "company_name", "state", "year", "direct_premium_earned",
    "direct_losses_incurred",
]


def load_filings(raw_dir: Path) -> pd.DataFrame:
    frames = []
    for p in sorted(raw_dir.glob("serff_*")):
        if p.suffix == ".csv":
            frames.append(pd.read_csv(p, dtype=str))
        elif p.suffix == ".json":
            frames.append(pd.DataFrame(json.loads(p.read_text())).astype(str))
    if not frames:
        raise FileNotFoundError(f"No serff_* files in {raw_dir}. Run `python -m ratescope sample`.")
    df = pd.concat(frames, ignore_index=True)
    missing = set(FILING_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Filing export missing columns: {missing}")
    df = df.fillna("").replace({"nan": ""})
    return df.drop_duplicates("serff_tracking_number").reset_index(drop=True)


def load_experience(raw_dir: Path) -> pd.DataFrame:
    p = raw_dir / "naic_experience.csv"
    df = pd.read_csv(p, dtype={"naic_company_code": str})
    missing = set(EXPERIENCE_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Experience file missing columns: {missing}")
    return df
