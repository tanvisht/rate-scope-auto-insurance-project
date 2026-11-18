from ratescope import parser


def test_rate_increase_phrase():
    t = "The company is filing an overall rate increase of 7.5% for its commercial auto program, effective 03/01/2024."
    assert parser.parse_rate_change(t) == 7.5
    assert parser.parse_effective_date(t) == "2024-03-01"


def test_rate_decrease_phrase():
    assert parser.parse_rate_change("overall rate decrease of 2.1%") == -2.1


def test_selected_vs_indicated():
    t = "Overall indicated change +12.6%; selected overall change +9.0%. Proposed effective date: 07/01/2023."
    assert parser.parse_rate_change(t) == 9.0
    assert parser.parse_indicated_change(t) == 12.6
    assert parser.parse_effective_date(t) == "2023-07-01"


def test_no_rate_impact():
    assert parser.parse_rate_change("Form filing. No rate impact.") == 0.0
    assert parser.parse_rate_change("Editorial change only") is None


def test_impact_range():
    assert parser.parse_impact_range("ranges from -3.0% to +14.5%") == (-3.0, 14.5)
    assert parser.parse_impact_range("Min/max impact: -1.0% / 9.0%") == (-1.0, 9.0)


def test_coverages():
    t = "Affected coverages: auto liability, collision, uninsured/underinsured motorist (UM/UIM), hired and non-owned auto"
    assert set(parser.parse_coverages(t)) == {"LIAB", "PD_COLL", "UM_UIM", "HNOA"}


def test_liability_limit():
    assert parser.parse_max_liability_limit("limits up to $1,000,000 CSL") == 1_000_000
    assert parser.parse_max_liability_limit("limits up to $1M/$2M") == 2_000_000
