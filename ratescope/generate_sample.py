"""Generate a representative sample of SERFF-style filings and NAIC-style experience.

Real SERFF/NAIC data cannot be redistributed, so this produces structurally
faithful records (tracking numbers, filing narrative text, NAIC codes,
premium/loss figures) to exercise the pipeline end to end.
"""
import json
import random

import numpy as np
import pandas as pd

from ratescope.config import RAW_DIR, STATES

CARRIERS = [
    ("Summit Mutual Insurance Co", "10001", "SUMM"),
    ("Keystone Commercial Casualty", "10002", "KEYC"),
    ("Pioneer Fleet Assurance", "10003", "PION"),
    ("Harbor State Indemnity", "10004", "HARB"),
    ("Granite Transport Insurance", "10005", "GRAN"),
    ("Liberty Ridge Casualty Co", "10006", "LIBR"),
    ("Meridian Auto Underwriters", "10007", "MERI"),
    ("Northstar Commercial Ins Co", "10008", "NORT"),
]
NAME_VARIANTS = {
    "Summit Mutual Insurance Co": ["Summit Mutual Ins. Co.", "SUMMIT MUTUAL INSURANCE COMPANY"],
    "Keystone Commercial Casualty": ["Keystone Comm. Casualty", "KEYSTONE COMMERCIAL CAS CO"],
    "Liberty Ridge Casualty Co": ["Liberty Ridge Cas. Company"],
    "Northstar Commercial Ins Co": ["NorthStar Commercial Insurance Company"],
}
COVERAGE_PHRASES = [
    "auto liability", "comprehensive", "collision", "uninsured/underinsured motorist (UM/UIM)",
    "medical payments", "personal injury protection (PIP)", "hired and non-owned auto",
    "motor truck cargo", "towing and labor", "rental reimbursement", "garagekeepers",
]
YEARS = range(2021, 2026)


def _narrative(rng, change, coverages, eff, lo, hi):
    direction = "increase" if change >= 0 else "decrease"
    cov = ", ".join(coverages)
    templates = [
        f"The company is filing an overall rate {direction} of {abs(change):.1f}% for its "
        f"commercial auto program, effective {eff}. Affected coverages: {cov}. "
        f"Individual policyholder impact ranges from {lo:+.1f}% to {hi:+.1f}%.",
        f"Overall indicated change {change*1.4:+.1f}%; selected overall change {change:+.1f}%. "
        f"Proposed effective date: {eff}. This filing revises base rates for {cov}. "
        f"Min/max impact: {lo:.1f}% / {hi:.1f}%.",
        f"Commercial Automobile - revision of rates and rules. Rate change: {change:+.1f}%. "
        f"Effective {eff} for new and renewal business. Lines impacted include {cov}.",
    ]
    return rng.choice(templates)


def generate(seed: int = 42, out_dir=RAW_DIR):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    filings, experience = [], []
    seq = 1
    for name, naic, code in CARRIERS:
        appetite = np_rng.normal(0, 1)  # carrier-level pricing aggressiveness
        for st in STATES:
            base_prem = np_rng.uniform(40, 400) * 1e6
            lr_trend = np_rng.normal(0.62, 0.06)
            prev_lr = lr_trend
            for yr in YEARS:
                lr = float(np.clip(prev_lr + np_rng.normal(0.015, 0.05), 0.40, 0.95))
                prem = base_prem * (1 + 0.06) ** (yr - 2021)
                experience.append({
                    "naic_company_code": naic,
                    "company_name": rng.choice([name] + NAME_VARIANTS.get(name, [])),
                    "state": st,
                    "year": yr,
                    "line_of_business": "Commercial Auto",
                    "direct_premium_written": round(prem * np_rng.uniform(0.98, 1.04), 0),
                    "direct_premium_earned": round(prem, 0),
                    "direct_losses_incurred": round(prem * lr, 0),
                    "direct_defense_cost_containment": round(prem * lr * 0.11, 0),
                })
                # carriers file more & larger increases after bad years
                n_filings = rng.choices([0, 1, 2], weights=[2, 5, 2])[0]
                for _ in range(n_filings):
                    change = round(float(np_rng.normal(4 + (prev_lr - 0.62) * 60 + appetite, 3)), 1)
                    month = rng.randint(1, 12)
                    eff = f"{month:02d}/01/{yr}"
                    covs = rng.sample(COVERAGE_PHRASES, rng.randint(2, 6))
                    lo = round(change - abs(np_rng.normal(6, 2)), 1)
                    hi = round(change + abs(np_rng.normal(8, 3)), 1)
                    ftype = rng.choice(["Rate", "Rate/Rule", "Form/Rate/Rule", "Rule", "Form"])
                    text = _narrative(rng, change, covs, eff, lo, hi)
                    if ftype in ("Rule", "Form"):
                        text = (f"Commercial Automobile {ftype.lower()} filing effective {eff}. "
                                f"Introduces endorsements for {', '.join(covs)}. No rate impact.")
                    limits = rng.choice(["$1,000,000 CSL", "$500,000 CSL", "$1M/$2M", "$2,000,000 CSL"])
                    filings.append({
                        "serff_tracking_number": f"{code}-{13000000 + seq}",
                        "state": st,
                        "company_name": rng.choice([name] + NAME_VARIANTS.get(name, [])),
                        "naic_company_code": naic if rng.random() > 0.15 else "",
                        "product_name": rng.choice(["Commercial Auto", "Business Auto", "Fleet Auto", "Trucking"]),
                        "type_of_insurance": "20.0 Commercial Auto",
                        "filing_type": ftype,
                        "submission_date": f"{yr-1 if month < 4 else yr}-{(month-3) % 12 + 1:02d}-15",
                        "disposition": rng.choices(["Approved", "Filed", "Withdrawn", "Pending"], [6, 3, 1, 1])[0],
                        "filing_description": text + f" Liability limits offered up to {limits}.",
                    })
                    seq += 1
                prev_lr = lr

    pd.DataFrame(experience).to_csv(out_dir / "naic_experience.csv", index=False)
    # split filings across formats to exercise ingestion paths
    half = len(filings) // 2
    pd.DataFrame(filings[:half]).to_csv(out_dir / "serff_filings_batch1.csv", index=False)
    with open(out_dir / "serff_filings_batch2.json", "w") as f:
        json.dump(filings[half:], f, indent=1)
    return len(filings), len(experience)


if __name__ == "__main__":
    print(generate())
