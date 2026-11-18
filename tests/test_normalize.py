import pandas as pd

from ratescope import normalize


def _dim():
    exp = pd.DataFrame({"naic_company_code": ["1", "1", "2"],
                        "company_name": ["Summit Mutual Insurance Co", "SUMMIT MUTUAL INSURANCE COMPANY",
                                         "Keystone Commercial Casualty"]})
    return normalize.build_company_dim(exp)


def test_canonical_name_prefers_clean_variant():
    assert _dim().set_index("naic_company_code").loc["1", "canonical_name"] == "Summit Mutual Insurance Co"


def test_fuzzy_resolution():
    dim = _dim()
    assert normalize.resolve_naic_code("Summit Mutual Ins. Co.", dim) == "1"
    assert normalize.resolve_naic_code("KEYSTONE COMM. CASUALTY", dim) == "2"
    assert normalize.resolve_naic_code("Totally Different Carrier", dim) is None
