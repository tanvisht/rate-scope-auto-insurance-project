"""Central configuration: states, coverage taxonomy, file paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SQL_DIR = ROOT / "sql"
DB_PATH = PROCESSED_DIR / "ratescope.db"

STATES = {
    "CA": "California",
    "TX": "Texas",
    "FL": "Florida",
    "NY": "New York",
    "IL": "Illinois",
    "GA": "Georgia",
}

# Canonical coverage codes -> regex patterns seen in filing text.
COVERAGE_PATTERNS = {
    "LIAB": r"\b(auto|bodily injury|property damage)?\s*liability\b|\bCSL\b|\bBI/PD\b",
    "PD_COMP": r"\bcomprehensive\b|\bother than collision\b|\bOTC\b",
    "PD_COLL": r"\bcollision\b",
    "UM_UIM": r"\bunder-?insured\b|\buninsured\b|\bUM/UIM\b|\bUM\b",
    "MEDPAY_PIP": r"\bmedical payments\b|\bmed ?pay\b|\bpersonal injury protection\b|\bPIP\b",
    "HNOA": r"\bhired (and|&) non-?owned\b|\bHNOA\b",
    "CARGO": r"\bmotor truck cargo\b|\bcargo\b",
    "TOWING": r"\btowing\b|\broadside\b",
    "RENTAL": r"\brental reimbursement\b|\btransportation expense\b",
    "GARAGE": r"\bgarage(keepers)?\b",
}

COVERAGE_LABELS = {
    "LIAB": "Liability (BI/PD)",
    "PD_COMP": "Physical Damage - Comprehensive",
    "PD_COLL": "Physical Damage - Collision",
    "UM_UIM": "Uninsured/Underinsured Motorist",
    "MEDPAY_PIP": "Med Pay / PIP",
    "HNOA": "Hired & Non-Owned Auto",
    "CARGO": "Motor Truck Cargo",
    "TOWING": "Towing & Labor",
    "RENTAL": "Rental Reimbursement",
    "GARAGE": "Garagekeepers",
}

FILING_TYPES = ["Rate", "Rule", "Form", "Rate/Rule", "Form/Rate/Rule"]
