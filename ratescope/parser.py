"""Extract structured fields from free-text SERFF filing descriptions."""
import re
from datetime import datetime

from ratescope.config import COVERAGE_PATTERNS

_PCT = r"([+-]?\d+(?:\.\d+)?)\s*%"
RATE_PATTERNS = [
    (re.compile(r"selected overall (?:rate )?change(?: of)?\s*:?\s*" + _PCT, re.I), 1),
    (re.compile(r"overall rate (increase|decrease) of\s*" + _PCT, re.I), None),
    (re.compile(r"rate change\s*:?\s*" + _PCT, re.I), 1),
]
INDICATED = re.compile(r"(?:overall )?indicated (?:rate )?change\s*:?\s*" + _PCT, re.I)
NO_RATE = re.compile(r"no rate impact|rule only|form only", re.I)
EFF_DATE = re.compile(r"effective(?: date)?\s*:?\s*(?:date\s*:?\s*)?(\d{1,2}/\d{1,2}/\d{4})", re.I)
RANGE = re.compile(r"(?:ranges? from|min/max impact:?)\s*" + _PCT + r"\s*(?:to|/)\s*" + _PCT, re.I)
LIMIT = re.compile(r"\$\s?(\d[\d,]*)(?:,000)?\s*(?:CSL)?|\$(\d+)M", re.I)


def parse_rate_change(text: str):
    """Return the filed overall rate change in percent, 0.0 for no-rate filings, None if absent."""
    for rx, grp in RATE_PATTERNS:
        m = rx.search(text)
        if m:
            if grp is None:
                val = float(m.group(2))
                return -val if m.group(1).lower() == "decrease" else val
            return float(m.group(grp))
    if NO_RATE.search(text):
        return 0.0
    return None


def parse_indicated_change(text: str):
    m = INDICATED.search(text)
    return float(m.group(1)) if m else None


def parse_effective_date(text: str):
    m = EFF_DATE.search(text)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%m/%d/%Y").date().isoformat()


def parse_impact_range(text: str):
    m = RANGE.search(text)
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def parse_coverages(text: str) -> list[str]:
    found = [code for code, pat in COVERAGE_PATTERNS.items() if re.search(pat, text, re.I)]
    # "collision" pattern shouldn't double count "other than collision"
    if "PD_COLL" in found and re.search(r"other than collision", text, re.I) and not re.search(
        r"(?<!than )collision", text, re.I):
        found.remove("PD_COLL")
    return found


def parse_max_liability_limit(text: str):
    """Largest dollar liability limit mentioned (USD)."""
    vals = []
    for m in re.finditer(r"\$\s?(\d[\d,]*)\s*(CSL)?", text):
        vals.append(int(m.group(1).replace(",", "")))
    for m in re.finditer(r"\$(\d+(?:\.\d+)?)M", text):
        vals.append(int(float(m.group(1)) * 1_000_000))
    vals = [v for v in vals if v >= 100_000]
    return max(vals) if vals else None


def parse_filing(text: str) -> dict:
    lo, hi = parse_impact_range(text)
    return {
        "rate_change_pct": parse_rate_change(text),
        "indicated_change_pct": parse_indicated_change(text),
        "effective_date": parse_effective_date(text),
        "impact_min_pct": lo,
        "impact_max_pct": hi,
        "coverages": parse_coverages(text),
        "max_liability_limit": parse_max_liability_limit(text),
    }
