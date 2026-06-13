# Employee Retention Analysis — IBM HR Dataset

**Is the company losing people because of low pay — or because of how it treats them?**

This project analyzes 1,470 employee records to identify the root causes of attrition, segment employees by flight risk, and deliver actionable retention recommendations. Built as an industry-level analytics project covering the full workflow from raw data to deployed application.

🔗 **Live App:** https://hr-attrition-analysis-raghav.streamlit.app

---

## The Business Problem

A mid-sized company is experiencing 16.1% annual attrition — 4 points above the industry benchmark of 10–12%. Every departure costs 6–9 months of that employee's salary in recruitment, onboarding, and lost productivity. The HR director needs to know: who is leaving, why, and what to do about it.

---

## What I Found

**The company doesn't have a compensation problem. It has a workload problem.**

Employees who work overtime earn *more* on average ($6,549 vs $6,485/month) yet leave at **3x the rate** — 30.5% vs 10.4%. Salary alone does not explain attrition. Overwork does.

Key findings:

- **16.1% overall attrition** — significantly above the 10–12% industry benchmark
- **Sales is the most at-risk department** at 20.6%, followed by HR at 19.0%
- **Sales Representatives leave at 39.8%** — nearly 1 in 2.5 — while Research Directors leave at just 2.5%
- **29.8% of employees leave within their first 2 years** — signalling a broken onboarding process
- **$2,046/month salary gap** between leavers and stayers — but this reflects role seniority, not a direct pay problem
- **Employees who left score lower on all 5 satisfaction dimensions** — job satisfaction, environment, relationships, work-life balance, and job involvement

---

## The Four Risk Segments

Since no loyalty or risk score existed in the data, I engineered a **Flight Risk Score** from five behavioral signals:

| Signal | Weight | Logic |
|---|---|---|
| Overtime | 30% | Strongest predictor — 3x attrition multiplier |
| Job Satisfaction | 25% | Low satisfaction = high exit intent |
| Monthly Income | 20% | Lower earners leave more frequently |
| Work-Life Balance | 15% | Burnout signal |
| Tenure | 10% | New employees leave most in first 2 years |

This produced four segments:

| Segment | Size | Attrition Rate | What it means |
|---|---|---|---|
| High Flight Risk | 261 (17.8%) | **41.0%** | Immediate HR intervention needed |
| Moderate Risk | 485 (33.0%) | 16.5% | Monitor and engage proactively |
| Stable but Disengaged | 624 (42.4%) | 6.6% | Long tenure but low satisfaction — future risk |
| Genuinely Retained | 100 (6.8%) | 9.0% | Study what keeps them — replicate it |

---

## Recommendations

**1. Address overtime before anything else.**
Overtime is the single strongest driver of attrition and operates independently of salary. The fix is workload redistribution — not pay raises. Start with Sales and R&D where overtime concentration is highest.

**2. Fix the first two years.**
29.8% of employees leave within 2 years — before the company recovers its hiring cost. Implement structured 30/60/90-day onboarding, assign mentors to new hires, and schedule mandatory check-ins at 6 months.

**3. Prioritise the High Flight Risk segment.**
261 employees currently score above 0.65 on the Flight Risk Score and are still employed. HR should begin individual conversations with this group, starting with those working overtime and earning below $5,000/month.

**4. Investigate the Sales Representative role specifically.**
39.8% attrition in a revenue-generating role is a strategic risk. This requires a dedicated review of quota pressure, compensation structure, and career progression in the Sales function.

---

## Project Structure

```
hr-attrition-analysis/
│
├── app.py                      # Streamlit app — dashboard, segments, AI chatbot
├── data_cleaning.py            # Data cleaning and flight risk segmentation
├── eda.py                      # Exploratory data analysis — 8 charts
├── queries.sql                 # 8 SQL queries answering core business questions
├── hr_attrition_cleaned.csv    # Cleaned and engineered dataset
├── requirements.txt            # Python dependencies
│
├── charts/                     # All EDA and segmentation visuals
│   ├── 01_overall_attrition.png
│   ├── 02_attrition_by_department.png
│   ├── 03_overtime_vs_attrition.png
│   ├── 04_salary_distribution.png
│   ├── 05_attrition_by_tenure.png
│   ├── 06_risk_segments.png
│   ├── 07_attrition_by_jobrole.png
│   └── 08_satisfaction_heatmap.png
│
└── .streamlit/
    └── config.toml             # App theme configuration
```

---

## SQL Queries

Eight business questions answered in SQL (SQLite):

| Query | Business Question |
|---|---|
| Q1 | What is the overall attrition rate? |
| Q2 | Which department has the highest attrition? |
| Q3 | Does overtime cause attrition? |
| Q4 | Which job roles are most at risk? |
| Q5 | At what tenure point do employees most commonly leave? |
| Q6 | What is the salary gap between leavers and stayers? |
| Q7 | Does the Flight Risk Score actually predict attrition? |
| Q8 | Which specific employees should HR prioritise this week? |

---

## Streamlit App Features

The deployed app has three pages:

**Overview** — Live KPI cards, attrition by department, overtime analysis, job role breakdown, tenure analysis, and satisfaction heatmap.

**Segment Analysis** — Interactive filters by department, risk segment, and overtime status. Shows segment breakdown, attrition rates, and a sortable employee detail table.

**Ask the Data** — Natural language chatbot powered by Groq (LLaMA 3). Ask any question about the dataset and get a specific, data-backed answer with an actionable recommendation.

---

## Methodology Note

This dataset has no order dates — every row is a single customer snapshot, not a transaction log. This meant traditional cohort analysis and time-series RFM were not possible. The Flight Risk Score is cross-sectional — it captures a moment in time rather than tracking change. In a real setting, the weights would be validated against actual 90-day retention outcomes and adjusted accordingly.

---

## Tech Stack

Python (Pandas, Matplotlib, Seaborn) · SQL (SQLite) · Streamlit · Groq API (LLaMA 3)

---

*Dataset: IBM HR Analytics Employee Attrition — publicly available on Kaggle*
