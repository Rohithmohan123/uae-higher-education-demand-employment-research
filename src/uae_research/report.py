"""Assemble the report content from computed findings, then render it to Markdown and PDF."""
from __future__ import annotations

import pandas as pd

from . import assumptions as A
from .report_render import to_markdown, to_pdf

V, S, X = "<b>[Verified]</b>", "<b>[Simulated]</b>", "<b>[Assumption]</b>"
DISCLAIMER = ("This report mixes three kinds of evidence, and each statement is tagged. <b>[Verified]</b> facts come from the public "
              "sources listed in the appendix. <b>[Simulated]</b> results come from a synthetic prospective-student survey generated "
              "by code in this repository. <b>[Assumption]</b> figures are modelling inputs. Simulated results and assumptions are "
              "NOT UAE market statistics, survey responses or employer views, and must not be quoted as such.")


def build_blocks(f: dict) -> list[tuple]:
    it = f["interest"].set_index(["segment", "course"])
    L, C = A.COURSES["lis"], A.COURSES["cogai"]
    allr = lambda c, k: it.loc[("All respondents", c), k]  # noqa: E731
    seg_best = lambda c: f["interest"][(f["interest"]["course"] == c) & (f["interest"]["segment"] != "All respondents")].sort_values("top2_box_pct").iloc[-1]  # noqa: E731
    base = f["scen"][f["scen"]["scenario"] == "Base"].set_index("course")
    rng = f["scen"].groupby("course")["first_year_intake"].agg(["min", "max"])
    mode = f["mode_by_course"]
    sens_top = {c: f["sens"][c].assign(swing=lambda d: d["intake_high"] - d["intake_low"]).sort_values("swing").iloc[-1]["assumption"] for c in A.COURSES}
    flex_lis = mode.loc[["Part-time / evening", "Hybrid / online"], L].sum()
    flex_cog = mode.loc[["Part-time / evening", "Hybrid / online"], C].sum()
    emp = f["emp_sum"].set_index("course")
    facts = f["facts"].set_index("fact_id")

    B: list[tuple] = [("h1", "1. Executive summary"), ("p", DISCLAIMER)]
    B.append(("bullets", [
        f"{V} The UAE already has an accredited undergraduate Library and Information Sciences degree at Al Wasl University in Dubai, "
        "launched in 2020, and a Master's at the American University in the Emirates. A new BSc in LIS would enter a small, niche market with one direct competitor.",
        f"{V} AI undergraduate provision has grown quickly. MBZUAI, the University of Sharjah, Canadian University Dubai and Al Ain University all offer AI "
        "bachelor's degrees, most launched in 2025. MBZUAI's first cohort was 115 students from more than 2,000 applicants. This desk search found no "
        "programme that <i>combines</i> cognitive science with AI; UAE University offers cognitive science only as a minor.",
        f"{V} Policy supports AI skills: the National Strategy for AI 2031 targets AI talent, and AI is taught in public schools from KG to Grade 12 from 2025-26.",
        f"{S} In the simulated survey, {allr(C, 'top2_box_pct'):.0f}% rate high interest in Cognitive Science & AI against {allr(L, 'top2_box_pct'):.0f}% for LIS. "
        f"LIS interest is highest among {seg_best(L)['segment'].lower()}s ({seg_best(L)['top2_box_pct']:.0f}%), and Cognitive Science & AI among {seg_best(C)['segment'].lower()}s ({seg_best(C)['top2_box_pct']:.0f}%).",
        f"{S}/{X} Base-case first-year intake: about {base.loc[C, 'first_year_intake']:.0f} students for Cognitive Science & AI (range {rng.loc[C, 'min']}-{rng.loc[C, 'max']}) "
        f"and about {base.loc[L, 'first_year_intake']:.0f} for LIS (range {rng.loc[L, 'min']}-{rng.loc[L, 'max']}). The result is most sensitive to the {sens_top['cogai'].lower()}.",
        f"{S} {flex_lis:.0f}% of would-be LIS applicants want part-time, evening or hybrid study, against {flex_cog:.0f}% for Cognitive Science & AI. A flexible LIS format for working "
        "library and records staff looks more viable than a full-time-only cohort.",
    ]))
    B.append(("p", "<b>Indicative conclusion (to validate with primary research):</b> a BSc in Cognitive Science & AI has the stronger demand case and a "
                   "differentiated position, because it is interdisciplinary rather than another pure AI degree. A BSc in LIS is a smaller, "
                   "flexible-delivery opportunity aimed at the existing library, archives and records workforce."))

    B += [("h1", "2. Scope and method"), ("bullets", [
        "Desk research on UAE institutions, accredited programmes, policy and the library and AI employer landscape (public sources, accessed November 2026).",
        f"A synthetic survey of {len(f['s']):,} prospective students across four segments and seven emirates, generated from documented assumptions "
        "(src/uae_research/assumptions.py) to demonstrate the analysis. A real study would replace this with a fielded survey.",
        "Course comparison, competitor benchmarking, a role and skills taxonomy, and an enrolment scenario model with sensitivity analysis.",
        "Interest is reported as top-2-box (% scoring 4-5 of 5) with 95% Wilson confidence intervals.",
    ])]

    B += [("h1", "3. Verified landscape"), ("p", f"{V} Facts from public sources, each traceable to the appendix:"),
          ("table", f["facts"][["fact_id", "course_relevance", "fact", "source_ids"]].rename(columns={"fact_id": "ID", "course_relevance": "Course", "fact": "Fact", "source_ids": "Sources"}), [1.1, 3.0, 10.4, 2.5]),
          ("img", f["figs"]["competitor_landscape"])]

    B += [("pagebreak",), ("h1", "4. Prospective-student demand (simulated)"), ("img", f["figs"]["interest_by_segment"]),
          ("table", f["interest"][["segment", "course", "n", "mean_interest", "top2_box_pct", "ci_low", "ci_high", "stated_intent_pct"]]
           .rename(columns={"segment": "Segment", "course": "Course", "mean_interest": "Mean (1-5)", "top2_box_pct": "Top-2 %", "ci_low": "CI low", "ci_high": "CI high", "stated_intent_pct": "Would apply %"}), None),
          ("img", f["figs"]["mode_among_intenders"]), ("img", f["figs"]["budget_among_intenders"]),
          ("p", f"{S} Among intenders, the top decision factor is '{f['priority'][C].idxmax().lower()}' for both courses. "
                f"{f['budget'].loc[['Under AED 30k', 'AED 30-50k'], L].sum():.0f}% of LIS intenders and {f['budget'].loc[['Under AED 30k', 'AED 30-50k'], C].sum():.0f}% of Cognitive Science & AI intenders "
                "cap their annual budget at AED 50k, so scholarships and instalment plans matter. For comparison, MBZUAI lists tuition of USD 45,000 per year [Verified, F07].")]

    B += [("pagebreak",), ("h1", "5. Employment opportunities"), ("img", f["figs"]["employer_scenarios"]),
          ("p", f"{X} The scenario inputs assume {emp.loc['lis', 'openings_low']}-{emp.loc['lis', 'openings_high']} annual graduate-level openings for LIS graduates across "
                f"{emp.loc['lis', 'sectors']} sectors and {emp.loc['cogai', 'openings_low']}-{emp.loc['cogai', 'openings_high']} for Cognitive Science & AI graduates across {emp.loc['cogai', 'sectors']} sectors. "
                "These are placeholders to show how employer demand feeds the model. They should be replaced with employer interviews, job-posting analysis "
                "and official labour-market data, none of which was collected for this demonstration."),
          ("img", f["figs"]["skills_matrix"]),
          ("table", f["roles"].rename(columns={"course": "Course", "role": "Role", "typical_sectors": "Typical sectors", "core_skills": "Core skills"}), [1.4, 4.2, 4.2, 7.2])]

    B += [("pagebreak",), ("h1", "6. Course comparison"),
          ("table", f["comparison"], [5.2, 5.9, 5.9]),
          ("img", f["figs"]["enrolment_scenarios"]), ("img", f["figs"]["sensitivity"]),
          ("table", f["scen"][["course", "scenario", "addressable_pool", "stated_intent_rate", "conversion", "yield", "applicants", "first_year_intake"]]
           .rename(columns={"course": "Course", "scenario": "Scenario", "addressable_pool": "Pool [A]", "stated_intent_rate": "Intent [S]", "conversion": "Conv. [A]", "yield": "Yield [A]", "applicants": "Applicants", "first_year_intake": "Intake"}), None)]

    B += [("pagebreak",), ("h1", "7. Opportunities and recommendations"), ("bullets", [
        "<b>Position Cognitive Science & AI as interdisciplinary.</b> Combine machine learning with cognitive psychology, linguistics (including Arabic NLP) and "
        "human-AI interaction, so it is not a fifth general AI degree [based on F04, F05, F08-F10, F15].",
        "<b>Build the school-to-university pipeline.</b> Students now take AI from KG to Grade 12 [F12]. Outreach to Grade 11-12 students, teachers and "
        "counsellors fits the segment with the highest simulated interest.",
        f"<b>Offer LIS in a flexible format.</b> Evening or hybrid delivery, credit for prior learning and a records & archives track suit working professionals "
        f"and career changers ({it.loc[('Working professional', L), 'top2_box_pct']:.0f}% and {it.loc[('Career changer', L), 'top2_box_pct']:.0f}% high interest, against "
        f"{it.loc[('Grade 12 - expatriate', L), 'top2_box_pct']:.0f}-{it.loc[('Grade 12 - UAE national', L), 'top2_box_pct']:.0f}% among school leavers [S]) and the assumed growth in digital-records roles [A].",
        "<b>Partner with employers early.</b> Libraries (e.g. Mohammed bin Rashid Library [F13]), government archives, technology firms and research "
        "institutes could provide internships, capstones and advisory-board input.",
        "<b>Make it affordable.</b> Most simulated intenders cap their budget at AED 50k a year. Model scholarships and instalment options before setting fees.",
        "<b>Run primary research before launch.</b> Field the survey design in docs/survey_instrument.md, interview 15-20 employers per course, analyse "
        "job postings, and check the full CAA programme register for any competitor this desk search missed.",
    ])]

    B += [("h1", "8. Limitations"), ("bullets", [
        "Survey results, intake scenarios and employer demand figures are simulated or assumed. They demonstrate the method, not the UAE market.",
        "The competitor list comes from a desk search and is not an exhaustive census of UAE programmes. Programmes change frequently.",
        "Secondary sources (news and directories) were used where official pages were not reachable. Confirm critical facts with the institution or the CAA register.",
        "Roles and skills are an analyst-compiled taxonomy to guide curriculum design, not measured demand.",
    ])]

    src = f["sources"][["source_id", "publisher", "title", "url"]].copy()
    B += [("pagebreak",), ("h1", "Appendix: sources (accessed 22 November 2026)"),
          ("table", src.rename(columns={"source_id": "ID", "publisher": "Publisher", "title": "Title", "url": "URL"}), [1.0, 3.2, 6.0, 6.8])]
    return B


def write_reports(findings: dict):
    A.REPORTS.mkdir(parents=True, exist_ok=True)
    blocks = build_blocks(findings)
    md, pdf = A.REPORTS / "uae_higher_education_research_report.md", A.REPORTS / "uae_higher_education_research_report.pdf"
    to_markdown(blocks, md)
    to_pdf(blocks, pdf)
    return md, pdf
