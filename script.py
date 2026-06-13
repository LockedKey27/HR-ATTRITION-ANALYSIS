
import pandas as pd
import numpy as np

# ── STEP 1: Load the dataset ─────────────────────────────────
df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv')

print(f"Raw dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# ── STEP 2: Drop useless columns ─────────────────────────────
# These 3 columns have only ONE unique value across all 1,470 rows.
# A column that never changes cannot explain anything.
# This is a real data quality issue worth mentioning in your README.

useless_cols = ['EmployeeCount', 'Over18', 'StandardHours']
df.drop(columns=useless_cols, inplace=True)
print(f"After dropping useless columns: {df.shape[1]} columns remaining")

# ── STEP 3: Binary encoding ───────────────────────────────────
# Machine learning and correlation analysis needs numbers, not text.
# We convert Yes/No columns to 1/0.
# WHY: This lets us calculate attrition rates, correlations, and
# use these columns in our Flight Risk Score formula.

df['Attrition_Flag'] = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)
df['OverTime_Flag']  = df['OverTime'].apply(lambda x: 1 if x == 'Yes' else 0)

print(f"Attrition rate: {round(df['Attrition_Flag'].mean() * 100, 1)}%")
print(f"Overtime rate:  {round(df['OverTime_Flag'].mean() * 100, 1)}%")

# ── STEP 4: Create Age Groups ─────────────────────────────────
# Grouping ages into bands makes analysis cleaner.
# Instead of 43 unique ages, we get 4 meaningful life stages.

df['AgeGroup'] = pd.cut(
    df['Age'],
    bins   = [17, 25, 35, 45, 60],
    labels = ['18-25', '26-35', '36-45', '46-60']
)

print("\nAge group distribution:")
print(df['AgeGroup'].value_counts().sort_index())

# ── STEP 5: Create Tenure Bands ───────────────────────────────
# Years at company grouped into meaningful career stages.
# WHY: Early tenure (0-2 yrs) is the highest attrition window.
# This band makes that pattern visible clearly.

df['TenureBand'] = pd.cut(
    df['YearsAtCompany'],
    bins   = [-1, 2, 5, 10, 20, 40],
    labels = ['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '20+ yrs']
)

print("\nAttrition rate by tenure band:")
print(df.groupby('TenureBand', observed=False)['Attrition_Flag'].apply(
    lambda x: f"{round(x.mean() * 100, 1)}%"
))

# ── STEP 6: Normalize Key Risk Signals ───────────────────────
# To combine different columns into one score, they must all be
# on the same 0-1 scale. This is called Min-Max Normalization.
# Formula: (value - min) / (max - min)
# WHY: We can't add MonthlyIncome (ranges $1K-$20K) directly
# with JobSatisfaction (ranges 1-4) — the scales are too different.

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

# INVERT satisfaction scores — low satisfaction = HIGH risk
# So we do: 1 - normalized_score
df['sat_risk'] = 1 - normalize(df['JobSatisfaction'])
df['wlb_risk'] = 1 - normalize(df['WorkLifeBalance'])
df['env_risk']  = 1 - normalize(df['EnvironmentSatisfaction'])

# Low income = high risk (direct normalization, then invert)
df['income_risk'] = 1 - normalize(df['MonthlyIncome'])

# Low tenure = high risk (new employees leave more)
df['tenure_risk'] = 1 - normalize(df['YearsAtCompany'])

# ── STEP 7: Build the Flight Risk Score ──────────────────────
# A weighted composite score combining 5 behavioral signals.
# Higher score = higher probability of leaving.
#
# WEIGHT LOGIC (must sum to 1.0):
# - OverTime (0.30) → Strongest predictor. 30.5% vs 10.4% attrition.
# - Job Satisfaction (0.25) → How happy they are in their role.
# - Monthly Income (0.20) → Leavers earn $2,046 less than stayers.
# - Work Life Balance (0.15) → Burnout signal.
# - Tenure (0.10) → New employees leave most in first 2 years.
#
# NOTE: In a real company, these weights would be validated against
# historical retention outcomes. Here they are assumption-based
# and should be noted as such in your methodology section.

df['FlightRiskScore'] = (
    df['OverTime_Flag'] * 0.30 +
    df['sat_risk']      * 0.25 +
    df['income_risk']   * 0.20 +
    df['wlb_risk']      * 0.15 +
    df['tenure_risk']   * 0.10
)

print("\nFlight Risk Score distribution:")
print(df['FlightRiskScore'].describe().round(3))

# ── STEP 8: Assign Risk Segments ─────────────────────────────
# Based on Flight Risk Score thresholds, each employee gets a label.
# These thresholds produce meaningful, business-actionable groups.
# WHY: Segments let HR prioritize — they can't intervene for all
# 1,470 employees at once. They need to know WHO to focus on first.

def assign_segment(score):
    if score >= 0.65:
        return 'High Flight Risk'
    elif score >= 0.45:
        return 'Moderate Risk'
    elif score >= 0.25:
        return 'Stable but Disengaged'
    else:
        return 'Genuinely Retained'

df['RiskSegment'] = df['FlightRiskScore'].apply(assign_segment)

# ── STEP 9: Validate the Segments ────────────────────────────
# A good segmentation model should show INCREASING attrition rate
# as risk level increases. If it doesn't, the weights are wrong.

print("\n=== SEGMENT VALIDATION ===")
print("\nSegment sizes:")
print(df['RiskSegment'].value_counts())

print("\nActual attrition rate by segment:")
validation = df.groupby('RiskSegment')['Attrition_Flag'].agg(['mean', 'sum', 'count'])
validation['attrition_rate'] = (validation['mean'] * 100).round(1)
validation.columns = ['Attrition Rate (decimal)', 'Employees Left', 'Total', 'Attrition Rate (%)']
print(validation[['Total', 'Employees Left', 'Attrition Rate (%)']])


output_cols = [
    # Core identifiers
    'EmployeeNumber',
    # Demographics
    'Age', 'AgeGroup', 'Gender', 'MaritalStatus', 'EducationField',
    # Job info
    'Department', 'JobRole', 'JobLevel', 'BusinessTravel',
    # Compensation
    'MonthlyIncome', 'PercentSalaryHike', 'StockOptionLevel',
    # Satisfaction signals
    'JobSatisfaction', 'EnvironmentSatisfaction',
    'RelationshipSatisfaction', 'WorkLifeBalance', 'JobInvolvement',
    # Tenure signals
    'YearsAtCompany', 'TenureBand', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'TotalWorkingYears', 'NumCompaniesWorked',
    # Work conditions
    'OverTime', 'OverTime_Flag', 'DistanceFromHome',
    # Engineered features
    'FlightRiskScore', 'RiskSegment',
    # Target variable
    'Attrition', 'Attrition_Flag'
]

df_clean = df[output_cols]
df_clean.to_csv('hr_attrition_cleaned.csv', index=False)

print(f"\n✅ Cleaned dataset saved: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
print("📁 File: hr_attrition_cleaned.csv")
