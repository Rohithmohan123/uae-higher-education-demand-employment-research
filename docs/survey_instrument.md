# Prospective-student survey instrument (template)

This is the questionnaire the **simulated** dataset imitates. Use it as a starting point for real fieldwork. Translate it into Arabic, pilot it with 15-20 respondents, and get ethics or consent approval before collecting data.

**Target respondents:** Grade 11-12 students (UAE nationals and expatriates), working professionals, and career changers living in the UAE.
**Suggested sample:** at least 300 per segment for ±6-point precision on top-2-box shares.

| # | Question | Response options | Dataset column |
|---|---|---|---|
| Q1 | Which emirate do you live in? | 7 emirates | `emirate` |
| Q2 | Which best describes you? | Grade 12 – UAE national · Grade 12 – expatriate · Working professional · Career changer | `segment` |
| Q3 | *Short course description shown.* How interested are you in a **BSc Library & Information Science**? | 1 Not at all – 5 Extremely | `interest_lis` |
| Q4 | *Short course description shown.* How interested are you in a **BSc Cognitive Science & AI**? | 1 – 5 | `interest_cogai` |
| Q5 | If offered next year, how likely are you to apply to each? | Definitely · Probably · Might · Probably not · Definitely not (top two coded 1) | `intent_lis`, `intent_cogai` |
| Q6 | How would you prefer to study? | Full-time on campus · Part-time / evening · Hybrid / online | `preferred_mode` |
| Q7 | What is the most you could pay per year in tuition (after any scholarship)? | Under AED 30k · AED 30-50k · AED 50-80k · Over AED 80k | `annual_budget` |
| Q8 | What matters most when choosing a programme? | Career prospects · Fees and scholarships · Accreditation · Flexible schedule · Location | `top_priority` |

**Analysis notes**
- Report top-2-box shares with 95% confidence intervals. Weight results to the population by segment and emirate.
- Stated intention overstates actual applications, so apply a conversion factor and test its sensitivity (see `assumptions.py`).
- Complement the survey with 15-20 employer interviews per course, using a separate guide covering roles, skills gaps, hiring volumes and internship capacity.
