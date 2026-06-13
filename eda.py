# ============================================================
# PROJECT 2 — HR Attrition Analysis
# Script 2: Exploratory Data Analysis (EDA)
# Author: Raghav Tiwari
# ============================================================
# WHAT THIS SCRIPT DOES:
# Generates 8 business charts that tell the complete attrition
# story — from the overall rate down to satisfaction signals.
# All charts save to the charts/ folder automatically.
#
# HOW TO RUN:
# 1. Run data_cleaning.py first to generate hr_attrition_cleaned.csv
# 2. Then run: python eda.py
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

# ── Load cleaned dataset ─────────────────────────────────────
df = pd.read_csv('hr_attrition_cleaned.csv')

print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Attrition rate: {round(df['Attrition_Flag'].mean()*100,1)}%")

# ── Setup ─────────────────────────────────────────────────────
os.makedirs('charts', exist_ok=True)

# Consistent color palette across all charts
C = {
    'stay':   '#2ecc71',  # green  — stayed / low risk
    'leave':  '#e74c3c',  # red    — left / high risk
    'blue':   '#2980b9',  # blue   — neutral
    'orange': '#e67e22',  # orange — moderate risk
    'dark':   '#2c3e50'   # dark   — text and reference lines
}

# Remove top and right borders from all charts — cleaner look
plt.rcParams.update({
    'font.family':          'sans-serif',
    'axes.spines.top':      False,
    'axes.spines.right':    False
})

# ── CHART 1: Overall Attrition Donut ─────────────────────────
# WHY: First chart in any HR project should establish the baseline.
# 16.1% is meaningfully above the typical 10-12% industry benchmark.

fig, ax = plt.subplots(figsize=(7, 7))
sizes  = [df['Attrition_Flag'].sum(), len(df) - df['Attrition_Flag'].sum()]
labels = ['Left (16.1%)', 'Stayed (83.9%)']
ax.pie(sizes, labels=labels, colors=[C['leave'], C['stay']],
       startangle=90, wedgeprops=dict(width=0.5))
ax.text(0, 0, '16.1%\nAttrition', ha='center', va='center',
        fontsize=22, fontweight='bold', color=C['dark'])
ax.set_title('Overall Employee Attrition Rate', fontsize=16,
             fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('charts/01_overall_attrition.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 1 saved — Overall Attrition Donut")

# ── CHART 2: Attrition by Department ─────────────────────────
# WHY: Identifies which business unit HR should prioritize first.
# Sales at 20.6% is 4.5 points above company average.

dept = df.groupby('Department')['Attrition_Flag'].apply(
    lambda x: round(x.mean() * 100, 1)
).sort_values(ascending=False).reset_index()
dept.columns = ['Department', 'Rate']

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(dept['Department'], dept['Rate'],
              color=[C['leave'], C['orange'], C['blue']],
              width=0.5, edgecolor='white')
for bar, val in zip(bars, dept['Rate']):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.3,
            f'{val}%', ha='center', fontsize=13, fontweight='bold')
ax.set_title('Attrition Rate by Department', fontsize=16, fontweight='bold')
ax.set_ylabel('Attrition Rate (%)', fontsize=12)
ax.set_ylim(0, 28)
ax.axhline(y=16.1, color=C['dark'], linestyle='--',
           alpha=0.5, label='Company Average (16.1%)')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/02_attrition_by_department.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 2 saved — Attrition by Department")

# ── CHART 3: Overtime vs Attrition ───────────────────────────
# WHY: The single most powerful finding in this dataset.
# Overtime employees leave at 3x the rate. This drives the
# primary recommendation — address workload, not just salary.

ot = df.groupby('OverTime')['Attrition_Flag'].apply(
    lambda x: round(x.mean() * 100, 1)
).reset_index()
ot.columns = ['OverTime', 'Rate']

fig, ax = plt.subplots(figsize=(7, 5))
bcolors = [C['stay'] if o == 'No' else C['leave'] for o in ot['OverTime']]
bars = ax.bar(ot['OverTime'], ot['Rate'], color=bcolors,
              width=0.4, edgecolor='white')
for bar, val in zip(bars, ot['Rate']):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.3,
            f'{val}%', ha='center', fontsize=15, fontweight='bold')
ax.set_title('Overtime vs Attrition Rate', fontsize=16, fontweight='bold')
ax.set_ylabel('Attrition Rate (%)', fontsize=12)
ax.set_ylim(0, 40)
ax.set_xticks([0, 1])
ax.set_xticklabels(['No Overtime', 'Overtime'], fontsize=12)
plt.tight_layout()
plt.savefig('charts/03_overtime_vs_attrition.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 3 saved — Overtime vs Attrition")

# ── CHART 4: Salary Distribution ─────────────────────────────
# WHY: Shows the $2,046/month salary gap between leavers and stayers.
# Key nuance — is this causation or correlation with junior roles?
# That analysis goes in your executive summary.

fig, ax = plt.subplots(figsize=(9, 5))
for status, color, label in zip(
    ['No',     'Yes'],
    [C['stay'], C['leave']],
    ['Stayed',  'Left']
):
    sub = df[df['Attrition'] == status]['MonthlyIncome']
    ax.hist(sub, bins=30, alpha=0.6, color=color,
            label=f'{label} (avg: ${int(sub.mean()):,})')
    ax.axvline(sub.mean(), color=color, linestyle='--', linewidth=2)

gap = int(
    df[df['Attrition']=='No']['MonthlyIncome'].mean() -
    df[df['Attrition']=='Yes']['MonthlyIncome'].mean()
)
ax.set_title('Monthly Income — Stayed vs Left', fontsize=16, fontweight='bold')
ax.set_xlabel('Monthly Income ($)', fontsize=12)
ax.set_ylabel('Number of Employees', fontsize=12)
ax.legend(fontsize=11)
ax.text(0.97, 0.95, f'Salary gap:\n${gap:,}/month',
        transform=ax.transAxes, ha='right', va='top', fontsize=11,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
plt.tight_layout()
plt.savefig('charts/04_salary_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 4 saved — Salary Distribution")

# ── CHART 5: Attrition by Tenure Band ────────────────────────
# WHY: 28.9% attrition in the first 2 years signals an
# onboarding and early engagement failure — not a pay problem.
# The fix is different: mentorship, structured onboarding, 90-day check-ins.

tenure = df.groupby('TenureBand', observed=False)['Attrition_Flag'].apply(
    lambda x: round(x.mean() * 100, 1)
).reset_index()
tenure.columns = ['TenureBand', 'Rate']

bcolors = [
    C['leave']  if r >= 20 else
    C['orange'] if r >= 13 else
    C['stay']
    for r in tenure['Rate']
]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(tenure['TenureBand'], tenure['Rate'],
              color=bcolors, width=0.5, edgecolor='white')
for bar, val in zip(bars, tenure['Rate']):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.3,
            f'{val}%', ha='center', fontsize=12, fontweight='bold')
ax.set_title('Attrition Rate by Employee Tenure', fontsize=16, fontweight='bold')
ax.set_xlabel('Years at Company', fontsize=12)
ax.set_ylabel('Attrition Rate (%)', fontsize=12)
ax.set_ylim(0, 38)
ax.axhline(y=16.1, color=C['dark'], linestyle='--',
           alpha=0.5, label='Company Average (16.1%)')
r_patch = mpatches.Patch(color=C['leave'],  label='Critical (>=20%)')
o_patch = mpatches.Patch(color=C['orange'], label='Elevated (13-20%)')
g_patch = mpatches.Patch(color=C['stay'],   label='Below Average (<13%)')
ax.legend(handles=[r_patch, o_patch, g_patch], fontsize=10)
plt.tight_layout()
plt.savefig('charts/05_attrition_by_tenure.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 5 saved — Attrition by Tenure Band")

# ── CHART 6: Flight Risk Segment Breakdown ───────────────────
# WHY: Shows that your engineered Flight Risk Score actually works.
# Attrition rises cleanly from 6.6% → 9.0% → 16.5% → 41.0%
# as risk level increases. This is the proof that your model is valid.

seg_order = ['High Flight Risk','Moderate Risk','Stable but Disengaged','Genuinely Retained']
seg = df.groupby('RiskSegment')['Attrition_Flag'].agg(
    ['mean','count']
).reindex(seg_order).reset_index()
seg['pct'] = (seg['mean'] * 100).round(1)
scolors = [C['leave'], C['orange'], C['blue'], C['stay']]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Left panel — segment sizes
bars = ax1.barh(seg['RiskSegment'], seg['count'],
                color=scolors, edgecolor='white')
for bar, val in zip(bars, seg['count']):
    ax1.text(bar.get_width() + 5,
             bar.get_y() + bar.get_height()/2,
             f'{val} employees', va='center', fontsize=11)
ax1.set_title('Segment Size', fontsize=14, fontweight='bold')
ax1.set_xlabel('Number of Employees', fontsize=11)
ax1.set_xlim(0, 800)

# Right panel — actual attrition rate per segment
bars2 = ax2.barh(seg['RiskSegment'], seg['pct'],
                 color=scolors, edgecolor='white')
for bar, val in zip(bars2, seg['pct']):
    ax2.text(bar.get_width() + 0.5,
             bar.get_y() + bar.get_height()/2,
             f'{val}%', va='center', fontsize=12, fontweight='bold')
ax2.set_title('Actual Attrition Rate by Segment', fontsize=14, fontweight='bold')
ax2.set_xlabel('Attrition Rate (%)', fontsize=11)
ax2.set_xlim(0, 55)
ax2.axvline(x=16.1, color=C['dark'], linestyle='--',
            alpha=0.5, label='Avg 16.1%')
ax2.legend(fontsize=10)

fig.suptitle('Flight Risk Segmentation', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/06_risk_segments.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 6 saved — Risk Segment Breakdown")

# ── CHART 7: Attrition by Job Role ───────────────────────────
# WHY: Sales Representative at 39.8% is a crisis — 1 in 2.5 leaves.
# Compare this to Research Director at 2.5%.
# Business implication: the company's revenue frontline is its
# most unstable workforce — that's a strategic risk.

role = df.groupby('JobRole')['Attrition_Flag'].apply(
    lambda x: round(x.mean() * 100, 1)
).sort_values(ascending=True).reset_index()
role.columns = ['JobRole', 'Rate']

rcolors = [
    C['leave']  if r >= 30 else
    C['orange'] if r >= 15 else
    C['stay']
    for r in role['Rate']
]

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(role['JobRole'], role['Rate'],
               color=rcolors, edgecolor='white')
for bar, val in zip(bars, role['Rate']):
    ax.text(bar.get_width() + 0.3,
            bar.get_y() + bar.get_height()/2,
            f'{val}%', va='center', fontsize=11, fontweight='bold')
ax.set_title('Attrition Rate by Job Role', fontsize=16, fontweight='bold')
ax.set_xlabel('Attrition Rate (%)', fontsize=12)
ax.set_xlim(0, 50)
ax.axvline(x=16.1, color=C['dark'], linestyle='--',
           alpha=0.5, label='Company Average (16.1%)')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/07_attrition_by_jobrole.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 7 saved — Attrition by Job Role")

# ── CHART 8: Satisfaction Heatmap ────────────────────────────
# WHY: Compares average satisfaction scores between leavers and stayers
# across 5 dimensions. Shows whether the problem is pay, environment,
# relationships, or work-life balance — critical for targeted action.

sat_cols   = ['JobSatisfaction','EnvironmentSatisfaction',
              'RelationshipSatisfaction','WorkLifeBalance','JobInvolvement']
sat_labels = ['Job Satisfaction','Environment Satisfaction',
              'Relationship Satisfaction','Work Life Balance','Job Involvement']

hmap = pd.DataFrame({
    'Stayed': [df[df['Attrition']=='No'][c].mean()  for c in sat_cols],
    'Left':   [df[df['Attrition']=='Yes'][c].mean() for c in sat_cols]
}, index=sat_labels)

fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(hmap, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=2, vmax=3, linewidths=0.5, ax=ax,
            annot_kws={'size': 13, 'weight': 'bold'})
ax.set_title('Avg Satisfaction Scores — Stayed vs Left\n(Scale: 1=Low, 4=High)',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/08_satisfaction_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 8 saved — Satisfaction Heatmap")

print()
print("=" * 50)
print("All 8 charts saved to charts/ folder")
print("Ready for Step 3 — SQL Queries")
print("=" * 50)
