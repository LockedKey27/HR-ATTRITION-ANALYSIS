-- ============================================================
-- QUERY 1: Overall Attrition Rate
-- BUSINESS QUESTION: How serious is the attrition problem?
-- BENCHMARK: Industry average is 10-12%. Above that = urgent.
-- ============================================================

SELECT
    COUNT(*)                                        AS total_employees,
    SUM(Attrition_Flag)                             AS employees_left,
    ROUND(AVG(Attrition_Flag) * 100, 1)            AS attrition_rate_pct,
    COUNT(*) - SUM(Attrition_Flag)                  AS employees_stayed
FROM hr_attrition;


-- ============================================================
-- QUERY 2: Attrition Rate by Department
-- BUSINESS QUESTION: Which department should HR prioritize first?
-- INSIGHT: Sales at 20.6% is 4.5 points above company average.
-- ============================================================

SELECT
    Department,
    COUNT(*)                                        AS total_employees,
    SUM(Attrition_Flag)                             AS employees_left,
    ROUND(AVG(Attrition_Flag) * 100, 1)            AS attrition_rate_pct
FROM hr_attrition
GROUP BY Department
ORDER BY attrition_rate_pct DESC;


-- ============================================================
-- QUERY 3: Overtime Impact on Attrition
-- BUSINESS QUESTION: Is workload driving people out?
-- INSIGHT: Overtime employees leave at 3x the rate (30.5% vs 10.4%)
-- WHY IT MATTERS: This reframes the problem from pay to workload.
-- ============================================================

SELECT
    OverTime,
    COUNT(*)                                        AS total_employees,
    SUM(Attrition_Flag)                             AS employees_left,
    ROUND(AVG(Attrition_Flag) * 100, 1)            AS attrition_rate_pct,
    ROUND(AVG(MonthlyIncome), 0)                   AS avg_monthly_income
FROM hr_attrition
GROUP BY OverTime
ORDER BY attrition_rate_pct DESC;


-- ============================================================
-- QUERY 4: Attrition by Job Role
-- BUSINESS QUESTION: Which roles are a revolving door?
-- INSIGHT: Sales Representative at 39.8% — nearly 1 in 2.5 leaves.
-- WHY IT MATTERS: Revenue-generating frontline is the most unstable.
-- ============================================================

SELECT
    JobRole,
    COUNT(*)                                        AS total_employees,
    SUM(Attrition_Flag)                             AS employees_left,
    ROUND(AVG(Attrition_Flag) * 100, 1)            AS attrition_rate_pct,
    ROUND(AVG(MonthlyIncome), 0)                   AS avg_monthly_income,
    ROUND(AVG(JobSatisfaction), 2)                 AS avg_job_satisfaction
FROM hr_attrition
GROUP BY JobRole
ORDER BY attrition_rate_pct DESC;


-- ============================================================
-- QUERY 5: Early Tenure Attrition — The Onboarding Problem
-- BUSINESS QUESTION: Are we losing people before we recover
--                    the cost of hiring them?
-- INSIGHT: 28.9% attrition in first 2 years vs 6.7% for 11-20 yr employees
-- WHY IT MATTERS: Cost to replace one employee = 6-9 months salary.
-- ============================================================

SELECT
    TenureBand,
    COUNT(*)                                        AS total_employees,
    SUM(Attrition_Flag)                             AS employees_left,
    ROUND(AVG(Attrition_Flag) * 100, 1)            AS attrition_rate_pct,
    ROUND(AVG(MonthlyIncome), 0)                   AS avg_monthly_income
FROM hr_attrition
GROUP BY TenureBand
ORDER BY
    CASE TenureBand
        WHEN '0-2 yrs'   THEN 1
        WHEN '3-5 yrs'   THEN 2
        WHEN '6-10 yrs'  THEN 3
        WHEN '11-20 yrs' THEN 4
        WHEN '20+ yrs'   THEN 5
    END;


-- ============================================================
-- QUERY 6: Salary Gap Analysis
-- BUSINESS QUESTION: How much more do retained employees earn?
-- INSIGHT: $2,046/month gap — but is it salary causing attrition,
--          or are junior roles (lower pay + higher turnover) skewing it?
-- ============================================================

SELECT
    Attrition                                       AS attrition_status,
    COUNT(*)                                        AS total_employees,
    ROUND(AVG(MonthlyIncome), 0)                   AS avg_monthly_income,
    ROUND(MIN(MonthlyIncome), 0)                   AS min_income,
    ROUND(MAX(MonthlyIncome), 0)                   AS max_income,
    ROUND(AVG(YearsAtCompany), 1)                  AS avg_tenure_years,
    ROUND(AVG(JobSatisfaction), 2)                 AS avg_job_satisfaction
FROM hr_attrition
GROUP BY Attrition;


-- ============================================================
-- QUERY 7: Flight Risk Segment Performance
-- BUSINESS QUESTION: Does our engineered Flight Risk Score
--                    actually predict attrition?
-- INSIGHT: Attrition rises cleanly 6.6% → 9% → 16.5% → 41%
--          This validates the model.
-- ============================================================

SELECT
    RiskSegment,
    COUNT(*)                                        AS total_employees,
    SUM(Attrition_Flag)                             AS employees_left,
    ROUND(AVG(Attrition_Flag) * 100, 1)            AS attrition_rate_pct,
    ROUND(AVG(MonthlyIncome), 0)                   AS avg_monthly_income,
    ROUND(AVG(FlightRiskScore), 3)                 AS avg_risk_score,
    ROUND(AVG(JobSatisfaction), 2)                 AS avg_satisfaction
FROM hr_attrition
GROUP BY RiskSegment
ORDER BY avg_risk_score DESC;


-- ============================================================
-- QUERY 8: High Priority Employee List — Who to Save First
-- BUSINESS QUESTION: Give me the names... give me the profiles
--                    of employees HR should call this week.
-- LOGIC: High Flight Risk + Still employed + Overtime = urgent
-- WHY IT MATTERS: This is where analysis becomes action.
-- ============================================================

SELECT
    EmployeeNumber,
    Department,
    JobRole,
    MonthlyIncome,
    OverTime,
    YearsAtCompany,
    JobSatisfaction,
    WorkLifeBalance,
    ROUND(FlightRiskScore, 3)                      AS FlightRiskScore,
    RiskSegment
FROM hr_attrition
WHERE
    RiskSegment   = 'High Flight Risk'
    AND Attrition = 'No'
    AND OverTime  = 'Yes'
ORDER BY FlightRiskScore DESC
LIMIT 20;