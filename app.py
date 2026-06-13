# ============================================================
# Employee Retention Dashboard
# HR Attrition Analysis — IBM Dataset
# Author: Raghav Tiwari
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from groq import Groq
import os

if "initialized" not in st.session_state:
    st.session_state.clear()
    st.session_state.initialized = True

st.set_page_config(
    page_title="Employee Retention Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #1A1A2E; padding-top: 2rem; }
    section[data-testid="stSidebar"] * { color: #EAEAEA !important; }
    h1 { font-size: 1.8rem !important; font-weight: 700 !important; color: #1A1A2E !important; border-bottom: 2px solid #C0392B; padding-bottom: 0.5rem; margin-bottom: 0.2rem !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; color: #1A1A2E !important; text-transform: uppercase; letter-spacing: 0.05rem; margin-top: 1.5rem !important; }
    div[data-testid="metric-container"] { background-color: #F4F6F8; border-left: 4px solid #C0392B; padding: 1rem 1.2rem; border-radius: 4px; }
    div[data-testid="metric-container"] label { font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08rem; color: #666666 !important; font-weight: 600; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; color: #1A1A2E !important; }
    hr { border-color: #E8E8E8; margin: 1rem 0; }
    .stButton button { background-color: #F4F6F8; color: #1A1A2E; border: 1px solid #CCCCCC; border-radius: 4px; font-size: 0.85rem; padding: 0.4rem 0.8rem; text-align: left; width: 100%; }
    .stButton button:hover { background-color: #1A1A2E; color: #FFFFFF; border-color: #1A1A2E; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
button[data-testid="collapsedControl"] { display: block !important; visibility: visible !important; }
            /* File uploader */
[data-testid="stFileUploader"] section {
    background-color: #1A1A2E !important;
    border: 1px dashed #555 !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] button {
    background-color: #2A2A4E !important;
    color: #EAEAEA !important;
    border: 1px solid #555 !important;
}

[data-testid="stFileUploader"] section * {
    color: #EAEAEA !important;
}
</style>
""", unsafe_allow_html=True)

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.spines.left': True, 'axes.spines.bottom': True,
    'axes.edgecolor': '#CCCCCC', 'axes.linewidth': 0.8,
    'axes.facecolor': '#FFFFFF', 'figure.facecolor': '#FFFFFF',
    'axes.grid': True, 'grid.color': '#F0F0F0', 'grid.linewidth': 0.6,
    'xtick.color': '#666666', 'ytick.color': '#666666',
})

C = {
    'red': '#C0392B', 'orange': '#E67E22', 'navy': '#1A1A2E',
    'blue': '#2980B9', 'green': '#27AE60', 'grey': '#95A5A6', 'light': '#F4F6F8',
}

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Employee Retention Dashboard")
    st.markdown("IBM HR Analytics · 1,470 Employees")
    st.markdown("---")
    page = st.radio("Navigation", ["Overview", "Segment Analysis", "Ask the Data"], label_visibility="collapsed")
    st.markdown("---")
    uploaded_file = st.file_uploader("Load Dataset", type=["csv"])
    st.markdown("---")
    st.markdown("<small style='color:#888'>Built by Raghav Tiwari<br>Python · SQL · Streamlit · Groq</small>", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("hr_attrition_cleaned.csv")
    except Exception:
        st.error("Dataset not found. Please upload hr_attrition_cleaned.csv")
        st.stop()

# ════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("Employee Retention Dashboard")
    st.caption("Analysis of workforce attrition patterns and risk indicators · IBM HR Dataset")
    st.markdown("---")

    total = len(df)
    left = int(df["Attrition_Flag"].sum())
    rate = round(left / total * 100, 1)
    avg_income = int(df["MonthlyIncome"].mean())
    ot_rate = round(df[df["OverTime"] == "Yes"].shape[0] / total * 100, 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Employees", f"{total:,}")
    c2.metric("Attrition Rate", f"{rate}%", f"+{round(rate-12,1)}% vs benchmark")
    c3.metric("Employees Left", f"{left}")
    c4.metric("Avg Monthly Income", f"${avg_income:,}")
    c5.metric("On Overtime", f"{ot_rate}%")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Attrition by Department")
        dept = df.groupby("Department")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).sort_values(ascending=False).reset_index()
        dept.columns = ["Department", "Rate"]
        fig, ax = plt.subplots(figsize=(6, 3.5))
        bars = ax.bar(dept["Department"], dept["Rate"], color=[C["red"], C["orange"], C["blue"]], width=0.45, zorder=3)
        for bar, val in zip(bars, dept["Rate"]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f"{val}%", ha="center", fontsize=11, fontweight="600", color=C["navy"])
        ax.axhline(y=16.1, color=C["grey"], linestyle="--", linewidth=1, label="Avg 16.1%")
        ax.set_ylim(0, 28)
        ax.set_ylabel("Attrition Rate (%)", fontsize=9, color="#666")
        ax.legend(fontsize=9, framealpha=0)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("### Impact of Overtime on Attrition")
        ot = df.groupby("OverTime")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).reset_index()
        ot.columns = ["OverTime", "Rate"]
        fig, ax = plt.subplots(figsize=(6, 3.5))
        bcolors = [C["green"] if o == "No" else C["red"] for o in ot["OverTime"]]
        bars = ax.bar(["No Overtime", "Overtime"], ot["Rate"], color=bcolors, width=0.35, zorder=3)
        for bar, val in zip(bars, ot["Rate"]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4, f"{val}%", ha="center", fontsize=13, fontweight="700", color=C["navy"])
        ax.set_ylim(0, 40)
        ax.set_ylabel("Attrition Rate (%)", fontsize=9, color="#666")
        ax.text(0.98, 0.95, "3x higher risk with overtime", transform=ax.transAxes, ha="right", va="top", fontsize=9, color=C["red"], style="italic")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Attrition by Job Role")
        role = df.groupby("JobRole")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).sort_values(ascending=True).reset_index()
        role.columns = ["JobRole", "Rate"]
        rcolors = [C["red"] if r >= 30 else C["orange"] if r >= 15 else C["green"] for r in role["Rate"]]
        fig, ax = plt.subplots(figsize=(6, 4.5))
        bars = ax.barh(role["JobRole"], role["Rate"], color=rcolors, zorder=3)
        for bar, val in zip(bars, role["Rate"]):
            ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height()/2, f"{val}%", va="center", fontsize=10, fontweight="600", color=C["navy"])
        ax.set_xlim(0, 50)
        ax.axvline(x=16.1, color=C["grey"], linestyle="--", linewidth=1, label="Avg 16.1%")
        ax.set_xlabel("Attrition Rate (%)", fontsize=9, color="#666")
        ax.legend(fontsize=9, framealpha=0)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("### Attrition by Years at Company")
        tenure = df.groupby("TenureBand", observed=False)["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).reset_index()
        tenure.columns = ["TenureBand", "Rate"]
        tcolors = [C["red"] if r >= 20 else C["orange"] if r >= 13 else C["green"] for r in tenure["Rate"]]
        fig, ax = plt.subplots(figsize=(6, 4.5))
        bars = ax.bar(tenure["TenureBand"], tenure["Rate"], color=tcolors, width=0.5, zorder=3)
        for bar, val in zip(bars, tenure["Rate"]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f"{val}%", ha="center", fontsize=11, fontweight="600", color=C["navy"])
        ax.set_ylim(0, 38)
        ax.set_ylabel("Attrition Rate (%)", fontsize=9, color="#666")
        ax.set_xlabel("Tenure Band", fontsize=9, color="#666")
        r_p = mpatches.Patch(color=C["red"], label="Critical >=20%")
        o_p = mpatches.Patch(color=C["orange"], label="Elevated 13-20%")
        g_p = mpatches.Patch(color=C["green"], label="Stable <13%")
        ax.legend(handles=[r_p, o_p, g_p], fontsize=8, framealpha=0)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("### Satisfaction Scores — Employees Who Left vs Stayed")
    sat_cols = ["JobSatisfaction", "EnvironmentSatisfaction", "RelationshipSatisfaction", "WorkLifeBalance", "JobInvolvement"]
    sat_labels = ["Job Satisfaction", "Environment", "Relationships", "Work-Life Balance", "Job Involvement"]
    hmap = pd.DataFrame({
        "Stayed": [df[df["Attrition"] == "No"][c].mean() for c in sat_cols],
        "Left":   [df[df["Attrition"] == "Yes"][c].mean() for c in sat_cols]
    }, index=sat_labels)
    fig, ax = plt.subplots(figsize=(10, 2.8))
    sns.heatmap(hmap, annot=True, fmt=".2f", cmap="RdYlGn", vmin=2.2, vmax=3.0, linewidths=0.5, linecolor="#E8E8E8", ax=ax, annot_kws={"size": 12, "weight": "bold"})
    ax.set_title("Scale: 1 = Very Low   4 = Very High", fontsize=9, color="#666", pad=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

# ════════════════════════════════════════════════════════════
# PAGE 2 — SEGMENT ANALYSIS
# ════════════════════════════════════════════════════════════
elif page == "Segment Analysis":
    st.title("Flight Risk Segment Analysis")
    st.caption("Employees classified into four risk tiers based on behavioral signals")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.multiselect("Department", options=list(df["Department"].unique()), default=list(df["Department"].unique()))
    with col2:
        seg_filter = st.multiselect("Risk Segment", options=list(df["RiskSegment"].unique()), default=list(df["RiskSegment"].unique()))
    with col3:
        ot_filter = st.multiselect("Overtime", options=["Yes", "No"], default=["Yes", "No"])

    filtered = df[(df["Department"].isin(dept_filter)) & (df["RiskSegment"].isin(seg_filter)) & (df["OverTime"].isin(ot_filter))]
    st.markdown("---")

    if len(filtered) == 0:
        st.warning("No employees match the selected filters.")
        st.stop()

    f_total = len(filtered)
    f_left = int(filtered["Attrition_Flag"].sum())
    f_rate = round(f_left / f_total * 100, 1)
    f_income = int(filtered["MonthlyIncome"].mean())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Employees Selected", f"{f_total:,}")
    c2.metric("Attrition Rate", f"{f_rate}%")
    c3.metric("Employees Left", f"{f_left}")
    c4.metric("Avg Monthly Income", f"${f_income:,}")
    st.markdown("---")

    seg_color_map = {"High Flight Risk": C["red"], "Moderate Risk": C["orange"], "Stable but Disengaged": C["blue"], "Genuinely Retained": C["green"]}

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Segment Breakdown")
        seg = filtered["RiskSegment"].value_counts().reset_index()
        seg.columns = ["Segment", "Count"]
        scolors = [seg_color_map.get(s, C["blue"]) for s in seg["Segment"]]
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(seg["Segment"], seg["Count"], color=scolors, zorder=3)
        for bar, val in zip(bars, seg["Count"]):
            ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, f"{val} employees", va="center", fontsize=10)
        ax.set_xlabel("Number of Employees", fontsize=9, color="#666")
        ax.set_xlim(0, seg["Count"].max() * 1.3)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("### Attrition Rate by Segment")
        seg_rate = filtered.groupby("RiskSegment")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).reset_index()
        seg_rate.columns = ["Segment", "Rate"]
        srcolors = [seg_color_map.get(s, C["blue"]) for s in seg_rate["Segment"]]
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(seg_rate["Segment"], seg_rate["Rate"], color=srcolors, zorder=3)
        for bar, val in zip(bars, seg_rate["Rate"]):
            ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height()/2, f"{val}%", va="center", fontsize=11, fontweight="600")
        ax.set_xlim(0, 55)
        ax.set_xlabel("Attrition Rate (%)", fontsize=9, color="#666")
        ax.axvline(x=16.1, color=C["grey"], linestyle="--", linewidth=1, label="Avg 16.1%")
        ax.legend(fontsize=9, framealpha=0)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    st.markdown("### Employee Detail — Sorted by Flight Risk Score")
    st.caption(f"Showing {len(filtered):,} employees based on current filters")
    st.dataframe(
        filtered[["EmployeeNumber", "Department", "JobRole", "MonthlyIncome", "OverTime", "YearsAtCompany", "JobSatisfaction", "WorkLifeBalance", "FlightRiskScore", "RiskSegment", "Attrition"]].sort_values("FlightRiskScore", ascending=False).reset_index(drop=True),
        use_container_width=True, height=400
    )

# ════════════════════════════════════════════════════════════
# PAGE 3 — ASK THE DATA
# ════════════════════════════════════════════════════════════
elif page == "Ask the Data":
    st.title("Ask the Data")
    st.caption("Natural language interface · Powered by Groq")
    st.markdown("---")

    total = len(df)
    left = int(df["Attrition_Flag"].sum())
    rate = round(left / total * 100, 1)
    avg_income_left = int(df[df["Attrition"] == "Yes"]["MonthlyIncome"].mean())
    avg_income_stayed = int(df[df["Attrition"] == "No"]["MonthlyIncome"].mean())
    ot_yes = round(df[df["OverTime"] == "Yes"]["Attrition_Flag"].mean() * 100, 1)
    ot_no = round(df[df["OverTime"] == "No"]["Attrition_Flag"].mean() * 100, 1)
    dept_rates = df.groupby("Department")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).to_dict()
    role_rates = df.groupby("JobRole")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).sort_values(ascending=False).to_dict()
    seg_rates = df.groupby("RiskSegment")["Attrition_Flag"].apply(lambda x: round(x.mean() * 100, 1)).to_dict()

    data_context = f"""
You are an HR analytics assistant. Answer questions using only the data below.
Be concise, specific, and business-focused. Always use exact numbers.
End every response with one clear, actionable recommendation for HR.
Write in clean professional paragraphs, not bullet points.

DATASET: IBM HR Analytics — {total} employees

ATTRITION SUMMARY:
- Overall attrition rate: {rate}% (industry benchmark: 10-12%)
- Employees who left: {left} | Employees who stayed: {total - left}
- Average income of leavers: ${avg_income_left:,}/month
- Average income of stayers: ${avg_income_stayed:,}/month
- Monthly income gap: ${avg_income_stayed - avg_income_left:,}

OVERTIME:
- Attrition with overtime: {ot_yes}%
- Attrition without overtime: {ot_no}%
- Key insight: overtime employees earn MORE yet leave at 3x the rate

DEPARTMENT RATES: {dept_rates}
JOB ROLE RATES: {role_rates}
RISK SEGMENTS: {seg_rates}

TENURE:
- 0-2 years: 28.9% attrition
- 3-5 years: 13.8%
- 6-10 years: 12.3%
- 11-20 years: 6.7%
- 20+ years: 12.1%
"""

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Suggested questions
questions = [
    "Which department has the highest attrition rate?",
    "Does overtime cause attrition or is it a salary issue?",
    "What is the salary gap between employees who left and stayed?",
    "Which job role is the biggest retention risk?",
    "What should HR prioritize to reduce attrition this quarter?",
    "How does tenure affect the likelihood of leaving?"
]

if len(st.session_state.messages) == 0:

    st.markdown("### Suggested Questions")

    col1, col2 = st.columns(2)

    for i, q in enumerate(questions):

        target = col1 if i % 2 == 0 else col2

        if target.button(q, key=f"sq{i}"):

            with st.spinner("Analyzing..."):

                full_prompt = f"{data_context}\n\nQuestion: {q}"

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=500
                )

                answer = response.choices[0].message.content

            st.session_state.messages.append(
                {"role": "user", "content": q}
            )

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

            st.rerun()

# Normal chat input
prompt = st.chat_input("Type your question here...")

if prompt:

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Analyzing..."):

            full_prompt = f"{data_context}\n\nQuestion: {prompt}"

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=500
            )

            answer = response.choices[0].message.content

        st.write(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    if len(st.session_state.messages) > 0:
        st.markdown("---")
        if st.button("Clear conversation"):
            st.session_state.messages = []
            st.rerun()