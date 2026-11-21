"""Generate the SIMULATED prospective-student survey and scenario tables.

Every value comes from the assumptions in assumptions.py plus seeded random noise.
The files are written to data/synthetic/ and every row carries data_type = "SIMULATED".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import assumptions as A


def _choice(rng, options: dict | list, p=None):
    if isinstance(options, dict):
        keys = list(options)
        return keys[rng.choice(len(keys), p=np.array(list(options.values())) / sum(options.values()))]
    return options[rng.choice(len(options), p=p)]


def survey(n: int = A.N_RESPONDENTS, seed: int = A.SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        seg = _choice(rng, A.SEGMENTS)
        row = {"respondent_id": f"R{i + 1:04d}", "emirate": _choice(rng, A.EMIRATES), "segment": seg}
        for c in A.COURSES:
            score = int(np.clip(np.round(rng.normal(A.INTEREST_MEAN[c][seg], A.INTEREST_SD)), 1, 5))
            row[f"interest_{c}"] = score
            row[f"intent_{c}"] = int(rng.random() < A.INTENT_GIVEN_INTEREST[score])
        row["preferred_mode"] = _choice(rng, A.MODE_MIX[seg])
        row["annual_budget"] = _choice(rng, A.BUDGET_BANDS, A.BUDGET_MIX[seg])
        row["top_priority"] = _choice(rng, A.PRIORITIES, A.PRIORITY_MIX[seg])
        row["data_type"] = "SIMULATED"
        rows.append(row)
    return pd.DataFrame(rows)


def employer_scenarios() -> pd.DataFrame:
    df = pd.DataFrame(A.EMPLOYER_SCENARIO, columns=["course", "sector", "assumed_openings_low", "assumed_openings_high", "growth_outlook"])
    df["course_name"] = df["course"].map(A.COURSES)
    df["data_type"] = "ASSUMPTION"
    return df


def main() -> None:
    A.SYNTHETIC.mkdir(parents=True, exist_ok=True)
    s = survey()
    s.to_csv(A.SYNTHETIC / "prospective_student_survey_SIMULATED.csv", index=False, encoding="utf-8-sig")
    e = employer_scenarios()
    e.to_csv(A.SYNTHETIC / "employer_demand_scenario_inputs_ASSUMPTIONS.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {len(s):,} simulated survey responses and {len(e)} employer scenario rows to data/synthetic/")


if __name__ == "__main__":
    main()
