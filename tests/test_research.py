"""Tests that keep verified facts and simulated data separate and the maths right."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uae_research import analysis as AN  # noqa: E402
from uae_research import assumptions as A  # noqa: E402
from uae_research import generate as G  # noqa: E402

sources = pd.read_csv(A.VERIFIED / "sources.csv")
facts = pd.read_csv(A.VERIFIED / "verified_facts.csv")
comp = pd.read_csv(A.VERIFIED / "competitor_programmes.csv")


def test_every_source_has_https_url_and_access_date():
    assert sources["source_id"].is_unique
    assert sources["url"].str.startswith("https://").all()
    assert sources["accessed"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()


@pytest.mark.parametrize("df", [facts, comp], ids=["facts", "competitors"])
def test_every_verified_row_cites_known_sources(df):
    known = set(sources["source_id"])
    for ids in df["source_ids"]:
        cited = set(ids.split(";"))
        assert cited and cited <= known, f"unknown source in {ids}"


def test_no_simulated_files_inside_verified_folder():
    for f in A.VERIFIED.glob("*.csv"):
        assert "SIMULATED" not in f.name and "ASSUMPTION" not in f.name


def test_simulated_outputs_are_labelled():
    s = G.survey(n=50)
    assert (s["data_type"] == "SIMULATED").all()
    assert (G.employer_scenarios()["data_type"] == "ASSUMPTION").all()


def test_generator_reproducible_and_in_range():
    a, b = G.survey(n=200, seed=1), G.survey(n=200, seed=1)
    pd.testing.assert_frame_equal(a, b)
    for c in A.COURSES:
        assert a[f"interest_{c}"].between(1, 5).all()
        assert set(a[f"intent_{c}"].unique()) <= {0, 1}


def test_assumption_shares_sum_to_one():
    assert sum(A.SEGMENTS.values()) == pytest.approx(1)
    assert sum(A.EMIRATES.values()) == pytest.approx(1)
    for mix in [*A.MODE_MIX.values()]:
        assert sum(mix.values()) == pytest.approx(1)
    for mix in [*A.BUDGET_MIX.values(), *A.PRIORITY_MIX.values()]:
        assert sum(mix) == pytest.approx(1)


def test_top2_and_wilson():
    assert AN.top2(pd.Series([1, 4, 5, 3])) == 0.5
    lo, hi = AN.wilson(0.5, 100)
    assert lo == pytest.approx(0.4038, abs=1e-3) and hi == pytest.approx(0.5962, abs=1e-3)
    lo0, hi0 = AN.wilson(0.0, 50)
    assert lo0 == pytest.approx(0, abs=1e-12) and 0 < hi0 < 0.1


def test_enrolment_scenario_formula():
    s = pd.DataFrame({"intent_lis": [1, 0, 0, 0], "intent_cogai": [1, 1, 0, 0]})
    t = AN.enrolment_scenarios(s).set_index(["course", "scenario"])
    expected = A.ADDRESSABLE_POOL["cogai"] * 0.5 * A.CONVERSION["Base"] * A.YIELD["cogai"]
    assert t.loc[(A.COURSES["cogai"], "Base"), "first_year_intake"] == round(expected)
    order = [t.loc[(A.COURSES["lis"], k), "first_year_intake"] for k in ["Conservative", "Base", "Optimistic"]]
    assert order == sorted(order)


def test_sensitivity_brackets_base():
    s = G.survey(n=300)
    for c in A.COURSES:
        t = AN.sensitivity(s, c)
        assert (t["intake_low"] <= t["intake_base"]).all() and (t["intake_high"] >= t["intake_base"]).all()
