"""Entity resolution of company names and enrichment of parsed filings."""
import re
from difflib import SequenceMatcher

import pandas as pd

from ratescope.parser import parse_filing

_SUFFIXES = {
    "insurance": "ins", "ins.": "ins", "company": "co", "co.": "co", "casualty": "cas",
    "cas.": "cas", "commercial": "comm", "comm.": "comm", "indemnity": "indem",
}


def clean_name(name: str) -> str:
    tokens = re.sub(r"[^\w\s.]", " ", str(name).lower()).split()
    tokens = [_SUFFIXES.get(t, t).rstrip(".") for t in tokens]
    tokens = [t for t in tokens if t not in {"co", "ins", "the", "inc"}]
    return " ".join(tokens)


def _pick_canonical(names: pd.Series) -> str:
    """Prefer the most frequent mixed-case, unabbreviated variant."""
    counts = names.value_counts()
    def rank(n):
        return (n.isupper(), "." in n, -counts[n], len(n))
    return sorted(counts.index, key=rank)[0]


def build_company_dim(experience: pd.DataFrame) -> pd.DataFrame:
    """One row per NAIC code, using the most common name variant as canonical."""
    dim = (experience.groupby("naic_company_code")["company_name"]
           .agg(_pick_canonical).reset_index())
    dim["clean_name"] = dim["company_name"].map(clean_name)
    return dim.rename(columns={"company_name": "canonical_name"})


def resolve_naic_code(name: str, company_dim: pd.DataFrame, threshold: float = 0.8):
    cn = clean_name(name)
    best, score = None, 0.0
    for code, ref in zip(company_dim["naic_company_code"], company_dim["clean_name"]):
        s = SequenceMatcher(None, cn, ref).ratio()
        if s > score:
            best, score = code, s
    return best if score >= threshold else None


def normalize_filings(filings: pd.DataFrame, company_dim: pd.DataFrame) -> pd.DataFrame:
    df = filings.copy()
    blank = df["naic_company_code"].str.strip() == ""
    df.loc[blank, "naic_company_code"] = df.loc[blank, "company_name"].map(
        lambda n: resolve_naic_code(n, company_dim))
    df["naic_resolved_by"] = blank.map({True: "fuzzy_name", False: "filing"})
    parsed = df["filing_description"].map(parse_filing).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    df = df.merge(company_dim[["naic_company_code", "canonical_name"]], on="naic_company_code", how="left")
    df["effective_year"] = pd.to_datetime(df["effective_date"]).dt.year
    return df


def explode_coverages(filings: pd.DataFrame) -> pd.DataFrame:
    out = filings[["serff_tracking_number", "naic_company_code", "state", "coverages"]].explode("coverages")
    return out.dropna(subset=["coverages"]).rename(columns={"coverages": "coverage_code"})
