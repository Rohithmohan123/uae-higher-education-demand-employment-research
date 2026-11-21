"""Every simulated input lives here, in one place, so a reader can see and change it.

NOTHING IN THIS FILE IS A UAE MARKET STATISTIC. These are illustrative modelling assumptions
used to demonstrate a market-research method. Replace them with primary research
(a real prospective-student survey, employer interviews) before using the outputs for decisions.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIED = ROOT / "data" / "verified"
REFERENCE = ROOT / "data" / "reference"
SYNTHETIC = ROOT / "data" / "synthetic"
FIGURES = ROOT / "outputs" / "figures"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "reports"

SEED = 2026
COURSES = {"lis": "BSc Library & Information Science", "cogai": "BSc Cognitive Science & AI"}
COURSE_AREA = {"lis": "Library & Information Science", "cogai": "Cognitive Science & AI"}

EMIRATES = {"Abu Dhabi": 0.30, "Dubai": 0.34, "Sharjah": 0.17, "Ajman": 0.07, "Ras Al Khaimah": 0.06, "Fujairah": 0.03, "Umm Al Quwain": 0.03}

# Simulated survey: respondent segments and their share of the sample
SEGMENTS = {
    "Grade 12 - UAE national": 0.30,
    "Grade 12 - expatriate": 0.30,
    "Working professional": 0.25,
    "Career changer": 0.15,
}
N_RESPONDENTS = 1200

# Mean interest on a 1-5 scale per segment (assumption), before individual noise
INTEREST_MEAN = {
    "lis":   {"Grade 12 - UAE national": 2.6, "Grade 12 - expatriate": 2.2, "Working professional": 3.0, "Career changer": 2.9},
    "cogai": {"Grade 12 - UAE national": 3.6, "Grade 12 - expatriate": 3.8, "Working professional": 3.1, "Career changer": 3.4},
}
INTEREST_SD = 1.05

# Preferred study mode by segment (assumption)
MODE_MIX = {
    "Grade 12 - UAE national": {"Full-time on campus": 0.78, "Part-time / evening": 0.07, "Hybrid / online": 0.15},
    "Grade 12 - expatriate": {"Full-time on campus": 0.74, "Part-time / evening": 0.08, "Hybrid / online": 0.18},
    "Working professional": {"Full-time on campus": 0.12, "Part-time / evening": 0.48, "Hybrid / online": 0.40},
    "Career changer": {"Full-time on campus": 0.30, "Part-time / evening": 0.35, "Hybrid / online": 0.35},
}

BUDGET_BANDS = ["Under AED 30k", "AED 30-50k", "AED 50-80k", "Over AED 80k"]
BUDGET_MIX = {
    "Grade 12 - UAE national": [0.30, 0.30, 0.25, 0.15],  # many expect government scholarships
    "Grade 12 - expatriate": [0.20, 0.38, 0.30, 0.12],
    "Working professional": [0.35, 0.40, 0.18, 0.07],
    "Career changer": [0.40, 0.35, 0.18, 0.07],
}

PRIORITIES = ["Career prospects", "Fees and scholarships", "Accreditation", "Flexible schedule", "Location"]
PRIORITY_MIX = {
    "Grade 12 - UAE national": [0.38, 0.20, 0.22, 0.05, 0.15],
    "Grade 12 - expatriate": [0.36, 0.30, 0.18, 0.04, 0.12],
    "Working professional": [0.28, 0.20, 0.17, 0.30, 0.05],
    "Career changer": [0.35, 0.25, 0.15, 0.20, 0.05],
}

# Stated intention ("definitely / probably would apply") is modelled from interest
INTENT_GIVEN_INTEREST = {1: 0.00, 2: 0.03, 3: 0.12, 4: 0.35, 5: 0.62}

# ---- Enrolment scenario model (assumptions) ----
# Addressable pool per intake year: prospective applicants in the UAE who would consider a
# bachelor's in the broad field (an assumption, not a measured figure).
ADDRESSABLE_POOL = {"lis": 1800, "cogai": 9000}
# Share of the stated-intention rate that converts to actual applications at a new programme
CONVERSION = {"Conservative": 0.10, "Base": 0.18, "Optimistic": 0.28}
# Share of applicants who enrol at this institution (admission yield, competition)
YIELD = {"lis": 0.45, "cogai": 0.30}

# ---- Employer demand scenario inputs (assumptions, NOT survey responses) ----
# Assumed annual graduate-level openings in the UAE per sector for each course's graduates.
EMPLOYER_SCENARIO = [
    # course, sector, low, high, growth outlook (assumption)
    ("lis", "Public & national libraries", 25, 60, "Stable"),
    ("lis", "University & school libraries", 40, 90, "Stable"),
    ("lis", "Government records & archives", 30, 80, "Growing"),
    ("lis", "Corporate knowledge management", 20, 70, "Growing"),
    ("lis", "Museums & cultural heritage", 10, 35, "Growing"),
    ("cogai", "Technology & software", 150, 400, "Fast-growing"),
    ("cogai", "Government digital services", 80, 220, "Fast-growing"),
    ("cogai", "Healthcare & health-tech", 40, 120, "Growing"),
    ("cogai", "Banking & fintech", 60, 180, "Growing"),
    ("cogai", "Education & ed-tech", 30, 90, "Growing"),
    ("cogai", "Research institutes", 20, 60, "Growing"),
]
