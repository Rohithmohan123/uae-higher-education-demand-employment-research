"""Analyse verified + simulated inputs and draw the charts. Returns a findings dict for the report."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from . import assumptions as A  # noqa: E402

INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
COURSE_COLOR = {"lis": "#2a78d6", "cogai": "#eb6834"}  # fixed categorical slots 1 and 2
MODE_COLOR = {"Full-time on campus": "#2a78d6", "Part-time / evening": "#eb6834", "Hybrid / online": "#1baf7a"}
SEQ = LinearSegmentedColormap.from_list("seq", ["#f0f5fc", "#9ec5f4", "#3987e5", "#1c5cab"])
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 24,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "legend.frameon": False, "legend.fontsize": 9, "legend.labelcolor": INK2,
})
SIM_NOTE = "SIMULATED data for demonstration: not a UAE market statistic."


def _finish(fig, path, note=SIM_NOTE):
    r = fig.canvas.get_renderer()
    y = (fig.get_tightbbox(r).y0 - 0.12) / fig.get_figheight()
    fig.text(0.01, y, note, fontsize=7.5, color=MUTED, ha="left", va="top", transform=fig.transFigure)
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def _sub(ax, text):
    ax.text(0, 1.015, text, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom")


def top2(series: pd.Series) -> float:
    """Share of respondents scoring 4 or 5 on a 1-5 scale."""
    return float((series >= 4).mean())


def wilson(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a proportion."""
    if n == 0:
        return (np.nan, np.nan)
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return (c - h, c + h)


def interest_table(s: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for seg in [*A.SEGMENTS, "All respondents"]:
        g = s if seg == "All respondents" else s[s["segment"] == seg]
        for c in A.COURSES:
            p = top2(g[f"interest_{c}"])
            lo, hi = wilson(p, len(g))
            rows.append({"segment": seg, "course": A.COURSES[c], "n": len(g), "mean_interest": round(g[f"interest_{c}"].mean(), 2),
                         "top2_box_pct": round(100 * p, 1), "ci_low": round(100 * lo, 1), "ci_high": round(100 * hi, 1),
                         "stated_intent_pct": round(100 * g[f"intent_{c}"].mean(), 1)})
    return pd.DataFrame(rows)


def enrolment_scenarios(s: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in A.COURSES:
        intent = s[f"intent_{c}"].mean()
        for name, conv in A.CONVERSION.items():
            applicants = A.ADDRESSABLE_POOL[c] * intent * conv
            rows.append({"course": A.COURSES[c], "scenario": name, "addressable_pool": A.ADDRESSABLE_POOL[c],
                         "stated_intent_rate": round(intent, 3), "conversion": conv, "yield": A.YIELD[c],
                         "applicants": round(applicants), "first_year_intake": round(applicants * A.YIELD[c])})
    return pd.DataFrame(rows)


def sensitivity(s: pd.DataFrame, course: str) -> pd.DataFrame:
    """One-at-a-time sensitivity: base intake when each assumption moves -25% / +25%."""
    intent = s[f"intent_{course}"].mean()
    base = dict(pool=A.ADDRESSABLE_POOL[course], intent=intent, conv=A.CONVERSION["Base"], yld=A.YIELD[course])
    f = lambda d: d["pool"] * d["intent"] * d["conv"] * d["yld"]  # noqa: E731
    rows = []
    for k, label in [("pool", "Addressable pool"), ("intent", "Stated intention rate"), ("conv", "Intention-to-application conversion"), ("yld", "Admission yield")]:
        lo, hi = dict(base), dict(base)
        lo[k] *= 0.75
        hi[k] *= 1.25
        rows.append({"assumption": label, "intake_low": round(f(lo)), "intake_base": round(f(base)), "intake_high": round(f(hi))})
    return pd.DataFrame(rows)


def run() -> dict:
    for d in (A.FIGURES, A.TABLES):
        d.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(A.SYNTHETIC / "prospective_student_survey_SIMULATED.csv", encoding="utf-8-sig")
    emp = pd.read_csv(A.SYNTHETIC / "employer_demand_scenario_inputs_ASSUMPTIONS.csv", encoding="utf-8-sig")
    facts = pd.read_csv(A.VERIFIED / "verified_facts.csv")
    sources = pd.read_csv(A.VERIFIED / "sources.csv")
    comp = pd.read_csv(A.VERIFIED / "competitor_programmes.csv")
    roles = pd.read_csv(A.REFERENCE / "roles_and_skills_ANALYST_COMPILED.csv")

    interest = interest_table(s)
    mode = (s.assign(any_intent=(s["intent_lis"] | s["intent_cogai"]).astype(bool))
            .groupby("segment")["preferred_mode"].value_counts(normalize=True).mul(100).round(1).rename("pct").reset_index())
    mode_by_course = pd.concat([s[s[f"intent_{c}"] == 1]["preferred_mode"].value_counts(normalize=True).mul(100).round(1)
                                .rename(A.COURSES[c]) for c in A.COURSES], axis=1).fillna(0).reindex(list(A.MODE_MIX["Career changer"]))
    budget = pd.concat([s[s[f"intent_{c}"] == 1]["annual_budget"].value_counts(normalize=True).mul(100).round(1)
                        .rename(A.COURSES[c]) for c in A.COURSES], axis=1).reindex(A.BUDGET_BANDS).fillna(0)
    priority = pd.concat([s[s[f"intent_{c}"] == 1]["top_priority"].value_counts(normalize=True).mul(100).round(1)
                          .rename(A.COURSES[c]) for c in A.COURSES], axis=1).reindex(A.PRIORITIES).fillna(0)
    emirate = s.groupby("emirate")[["intent_lis", "intent_cogai"]].mean().mul(100).round(1).reindex(list(A.EMIRATES))
    emirate["n"] = s["emirate"].value_counts().reindex(list(A.EMIRATES))
    scen = enrolment_scenarios(s)
    sens = {c: sensitivity(s, c) for c in A.COURSES}

    emp["mid"] = (emp["assumed_openings_low"] + emp["assumed_openings_high"]) / 2
    emp_sum = emp.groupby("course").agg(sectors=("sector", "count"), openings_low=("assumed_openings_low", "sum"),
                                        openings_high=("assumed_openings_high", "sum")).reset_index()

    comp_counts = comp.groupby(["course_area", "level"]).size().rename("programmes_found").reset_index()
    bach = comp[comp["level"] == "Bachelor"].groupby("course_area").size()

    base = scen[scen["scenario"] == "Base"].set_index("course")
    all_int = interest[interest["segment"] == "All respondents"].set_index("course")
    comparison = pd.DataFrame({
        "Criterion": ["Bachelor programmes found in UAE (verified)", "Closest existing offer (verified)",
                      "Policy tailwind (verified)", "Top-2-box interest (simulated)", "Stated intention to apply (simulated)",
                      "Base-case first-year intake (scenario)", "Assumed annual openings across sectors (assumption)",
                      "Most preferred study mode among intenders (simulated)", "Typical roles (analyst-compiled)"],
        A.COURSES["lis"]: [str(int(bach.get(A.COURSE_AREA["lis"], 0))), "Al Wasl University BLIS (Dubai, launched 2020)",
                           "Library sector investment, e.g. Mohammed bin Rashid Library (2022)",
                           f"{all_int.loc[A.COURSES['lis'], 'top2_box_pct']:.0f}%", f"{all_int.loc[A.COURSES['lis'], 'stated_intent_pct']:.0f}%",
                           f"{base.loc[A.COURSES['lis'], 'first_year_intake']:.0f} students",
                           f"{emp_sum.set_index('course').loc['lis', 'openings_low']}-{emp_sum.set_index('course').loc['lis', 'openings_high']}",
                           mode_by_course[A.COURSES["lis"]].idxmax(), "; ".join(roles[roles.course == "lis"]["role"].head(3))],
        A.COURSES["cogai"]: [f"{int(bach.get(A.COURSE_AREA['cogai'], 0))} AI bachelors; 0 combined CogSci + AI found",
                             "AI bachelors (MBZUAI, UoS, CUD, AAU); UAEU cognitive science minor",
                             "National AI Strategy 2031; K-12 AI curriculum from 2025-26",
                             f"{all_int.loc[A.COURSES['cogai'], 'top2_box_pct']:.0f}%", f"{all_int.loc[A.COURSES['cogai'], 'stated_intent_pct']:.0f}%",
                             f"{base.loc[A.COURSES['cogai'], 'first_year_intake']:.0f} students",
                             f"{emp_sum.set_index('course').loc['cogai', 'openings_low']}-{emp_sum.set_index('course').loc['cogai', 'openings_high']}",
                             mode_by_course[A.COURSES["cogai"]].idxmax(), "; ".join(roles[roles.course == "cogai"]["role"].head(3))],
    })

    tables = {"01_interest_by_segment": interest, "02_preferred_mode_by_segment": mode, "03_mode_among_intenders": mode_by_course.reset_index(names="mode"),
              "04_budget_among_intenders": budget.reset_index(names="budget"), "05_priority_among_intenders": priority.reset_index(names="priority"),
              "06_intent_by_emirate": emirate.reset_index(), "07_enrolment_scenarios": scen, "08_sensitivity_lis": sens["lis"],
              "09_sensitivity_cogai": sens["cogai"], "10_employer_scenario_inputs": emp, "11_competitor_programmes_verified": comp,
              "12_course_comparison": comparison, "13_verified_facts": facts, "14_roles_and_skills": roles}
    for k, t in tables.items():
        t.to_csv(A.TABLES / f"{k}.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(A.TABLES / "uae_higher_education_research_tables.xlsx", engine="openpyxl") as xw:
        pd.DataFrame({"read me": ["Sheets ending _verified / 13_verified_facts come from cited public sources (see sources sheet).",
                                  "All survey, scenario and employer-demand figures are SIMULATED or ASSUMPTIONS for demonstration.",
                                  "They are not UAE market statistics and must not be quoted as such."]}).to_excel(xw, "README", index=False)
        sources.to_excel(xw, "sources", index=False)
        for k, t in tables.items():
            t.to_excel(xw, k[:31], index=False)
        for ws in xw.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(70, max(10, *(len(str(c.value or "")) for c in col)) + 2)
            ws.freeze_panes = "A2"

    figs = {k: A.FIGURES / f"{i:02d}_{k}.png" for i, k in enumerate(
        ["interest_by_segment", "mode_among_intenders", "budget_among_intenders", "competitor_landscape", "employer_scenarios", "enrolment_scenarios", "sensitivity", "skills_matrix"], 1)}

    # 1. Interest by segment (top-2-box with CI)
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    segs = list(A.SEGMENTS)
    y = np.arange(len(segs))[::-1]
    for off, c in [(0.17, "lis"), (-0.17, "cogai")]:
        t = interest[(interest["course"] == A.COURSES[c])].set_index("segment").reindex(segs)
        ax.barh(y + off, t["top2_box_pct"], height=0.32, color=COURSE_COLOR[c], label=A.COURSES[c], edgecolor=SURFACE, linewidth=2)
        ax.hlines(y + off, t["ci_low"], t["ci_high"], color=INK2, linewidth=1.2)
        for yi, v in zip(y + off, t["top2_box_pct"]):
            ax.text(v + 1.2, yi, f"{v:.0f}%", va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(y, segs)
    ax.tick_params(axis="y", colors=INK, length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% rating interest 4 or 5 out of 5 (line = 95% CI)")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.14), ncol=2)
    ax.set_title("Interest in each course by prospective-student segment")
    _sub(ax, f"Simulated survey, n = {len(s):,}")
    _finish(fig, figs["interest_by_segment"])

    # 2. Mode among intenders (100% stacked)
    fig, ax = plt.subplots(figsize=(8.6, 2.9))
    y = np.arange(len(A.COURSES))[::-1]
    left = np.zeros(len(A.COURSES))
    for m in mode_by_course.index:
        vals = mode_by_course.loc[m].to_numpy()
        ax.barh(y, vals, left=left, color=MODE_COLOR[m], height=0.55, edgecolor=SURFACE, linewidth=2, label=m)
        for yi, l, v in zip(y, left, vals):
            if v >= 8:
                ax.text(l + v / 2, yi, f"{v:.0f}%", ha="center", va="center", color="#ffffff", fontsize=9)
        left += vals
    ax.set_yticks(y, list(A.COURSES.values()))
    ax.tick_params(axis="y", colors=INK, length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.22), ncol=3)
    ax.set_title("Preferred study mode among respondents who would apply")
    _finish(fig, figs["mode_among_intenders"])

    # 3. Budget among intenders (grouped bars)
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    x = np.arange(len(A.BUDGET_BANDS))
    for off, c in [(-0.2, "lis"), (0.2, "cogai")]:
        v = budget[A.COURSES[c]].to_numpy()
        ax.bar(x + off, v, width=0.38, color=COURSE_COLOR[c], label=A.COURSES[c], edgecolor=SURFACE, linewidth=2)
        for xi, vi in zip(x + off, v):
            ax.text(xi, vi + 0.8, f"{vi:.0f}%", ha="center", fontsize=8.5, color=INK2)
    ax.set_xticks(x, A.BUDGET_BANDS)
    ax.set_ylabel("% of intenders")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right")
    ax.set_title("Maximum annual tuition budget among intenders")
    _finish(fig, figs["budget_among_intenders"])

    # 4. Competitor landscape (verified)
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    comp_sorted = comp.sort_values(["course_area", "level"])
    yy = np.arange(len(comp_sorted))[::-1]
    marker = {"Bachelor": "o", "Master": "s", "Minor": "D"}
    for yi, (_, r) in zip(yy, comp_sorted.iterrows()):
        c = "lis" if r["course_area"] == A.COURSE_AREA["lis"] else "cogai"
        ax.scatter(0, yi, s=90, marker=marker[r["level"]], color=COURSE_COLOR[c], edgecolor=SURFACE, linewidth=1.5, zorder=3)
        ax.text(0.04, yi, f"{r['institution']} ({r['emirate']})", va="center", fontsize=9, color=INK)
        ax.text(0.04, yi - 0.32, f"{r['programme']} · {r['launch_or_status']} · sources {r['source_ids'].replace(';', ', ')}", va="center", fontsize=7.5, color=INK2)
    ax.set_xlim(-0.05, 1)
    ax.set_ylim(-0.8, len(comp_sorted) - 0.4)
    ax.axis("off")
    ax.set_title("Competitor and adjacent programmes found (verified)")
    _sub(ax, "● Bachelor   ■ Master   ◆ Minor · blue = Library & Information Science, orange = Cognitive Science & AI area")
    _finish(fig, figs["competitor_landscape"], note="Verified from cited public sources (see data/verified/sources.csv). Desk search, Nov 2026; not an exhaustive census.")

    # 5. Employer scenario ranges
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    e = emp.sort_values(["course", "mid"])
    yy = np.arange(len(e))
    for yi, (_, r) in zip(yy, e.iterrows()):
        ax.hlines(yi, r["assumed_openings_low"], r["assumed_openings_high"], color=COURSE_COLOR[r["course"]], linewidth=6, alpha=0.85)
        ax.text(r["assumed_openings_high"] + 6, yi, f"{r['assumed_openings_low']}-{r['assumed_openings_high']} · {r['growth_outlook']}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(yy, e["sector"])
    ax.tick_params(axis="y", colors=INK, length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, e["assumed_openings_high"].max() * 1.4)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.set_xlabel("Assumed annual graduate-level openings (scenario range)")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0], [0], color=COURSE_COLOR[c], lw=6, label=A.COURSES[c]) for c in A.COURSES], loc="upper left", bbox_to_anchor=(0, -0.11), ncol=2)
    ax.set_title("Employer demand by sector: scenario ranges")
    _sub(ax, "Analyst assumptions for modelling, not employer survey responses or official vacancy data")
    _finish(fig, figs["employer_scenarios"], note="ASSUMPTIONS for demonstration: replace with employer interviews and labour-market data.")

    # 6. Enrolment scenarios
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    x = np.arange(len(A.CONVERSION))
    for off, c in [(-0.2, "lis"), (0.2, "cogai")]:
        v = scen[scen["course"] == A.COURSES[c]]["first_year_intake"].to_numpy()
        ax.bar(x + off, v, width=0.38, color=COURSE_COLOR[c], label=A.COURSES[c], edgecolor=SURFACE, linewidth=2)
        for xi, vi in zip(x + off, v):
            ax.text(xi, vi + max(scen["first_year_intake"]) * 0.02, f"{vi:.0f}", ha="center", fontsize=9, color=INK2)
    ax.set_xticks(x, list(A.CONVERSION))
    ax.set_ylabel("First-year intake (students)")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left")
    ax.set_title("First-year intake scenarios for a new programme")
    _sub(ax, "Addressable pool × stated intention × conversion × admission yield (all assumptions)")
    _finish(fig, figs["enrolment_scenarios"])

    # 7. Sensitivity (tornado, CogAI)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.4), sharey=True)
    for ax, c in zip(axes, A.COURSES):
        t = sens[c].iloc[::-1]
        yy = np.arange(len(t))
        b = t["intake_base"].iloc[0]
        ax.barh(yy, t["intake_high"] - b, left=b, color=COURSE_COLOR[c], height=0.55, edgecolor=SURFACE)
        ax.barh(yy, t["intake_low"] - b, left=b, color=COURSE_COLOR[c], alpha=0.45, height=0.55, edgecolor=SURFACE)
        ax.axvline(b, color=INK, linewidth=1)
        ax.set_yticks(yy, t["assumption"])
        ax.tick_params(axis="y", colors=INK, length=0)
        ax.set_title(A.COURSES[c], fontsize=10.5, pad=10)
        ax.set_xlabel("Base intake if one input moves ±25%")
    fig.suptitle("Which assumptions matter most?", x=0.01, ha="left", fontweight="bold", fontsize=12.5, color=INK, y=1.05)
    _finish(fig, figs["sensitivity"])

    # 8. Skills matrix (analyst-compiled, qualitative)
    skills = sorted({sk.strip() for v in roles["core_skills"] for sk in v.split(";")}, key=str.lower)
    mat = pd.DataFrame(0, index=roles["role"], columns=skills)
    for _, r in roles.iterrows():
        for sk in r["core_skills"].split(";"):
            mat.loc[r["role"], sk.strip()] = 1
    keep = mat.columns[mat.sum() >= 1]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.imshow(mat[keep].values, cmap=SEQ, aspect="auto", vmin=0, vmax=1.3)
    ax.set_xticks(range(len(keep)), keep, rotation=60, ha="right", fontsize=7.5)
    ax.set_yticks(range(len(mat)), [f"{'LIS' if c == 'lis' else 'CogAI'} · {r}" for c, r in zip(roles["course"], roles["role"])], fontsize=8.5)
    ax.tick_params(length=0, colors=INK)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(keep)), minor=True)
    ax.set_yticks(np.arange(-.5, len(mat)), minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    ax.tick_params(which="minor", length=0)
    ax.set_title("Typical roles and the skills they draw on")
    _sub(ax, "Analyst-compiled role taxonomy to guide curriculum design (qualitative)")
    _finish(fig, figs["skills_matrix"], note="Analyst-compiled from general knowledge of the roles; validate with employers.")

    return {"s": s, "interest": interest, "mode_by_course": mode_by_course, "budget": budget, "priority": priority, "emirate": emirate,
            "scen": scen, "sens": sens, "emp": emp, "emp_sum": emp_sum, "comp": comp, "comp_counts": comp_counts, "facts": facts,
            "sources": sources, "roles": roles, "comparison": comparison, "figs": figs}
