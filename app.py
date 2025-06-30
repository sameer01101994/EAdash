import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="HR Attrition Insights", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("EA.csv")
    return df

df = load_data()

# --- GLOBAL SIDEBAR FILTERS ---------------------------------------------------
st.sidebar.header("Global Filters")

# Department filter
departments = st.sidebar.multiselect(
    "Department", options=sorted(df["Department"].unique()),
    default=sorted(df["Department"].unique())
)

# Job Role filter (dependent on Department filter)
job_roles = st.sidebar.multiselect(
    "Job Role", options=sorted(df[df["Department"].isin(departments)]["JobRole"].unique()),
    default=sorted(df[df["Department"].isin(departments)]["JobRole"].unique())
)

# Gender filter
genders = st.sidebar.multiselect(
    "Gender", options=sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

# Age slider
age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age Range", min_value=age_min, max_value=age_max,
                              value=(age_min, age_max))

# Attrition filter
attrition_filter = st.sidebar.multiselect(
    "Attrition Status", options=df["Attrition"].unique(), default=df["Attrition"].unique()
)

# Apply filtering
filtered_df = df[
    (df["Department"].isin(departments)) &
    (df["JobRole"].isin(job_roles)) &
    (df["Gender"].isin(genders)) &
    (df["Age"].between(*age_range)) &
    (df["Attrition"].isin(attrition_filter))
]

# --- KPI SECTION --------------------------------------------------------------
st.title("HR Attrition & Workforce Analytics Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    total_emp = len(filtered_df)
    st.metric("Total Employees", f"{total_emp:,}")
    st.caption("Number of employees after applying selected filters.")

with col2:
    attrition_count = filtered_df[filtered_df["Attrition"] == "Yes"].shape[0]
    st.metric("Employees Left", f"{attrition_count:,}")
    st.caption("Employees who have left the company.")

with col3:
    attrition_rate = (attrition_count / total_emp * 100) if total_emp else 0
    st.metric("Attrition Rate", f"{attrition_rate:.1f}%")
    st.caption("Percentage of employees who have left.")

st.divider()

# --- TABS ---------------------------------------------------------------------
overview_tab, demographics_tab, job_tab, comp_tab, tenure_tab, advanced_tab = st.tabs(
    ["Overview", "Demographics", "Job & Satisfaction", "Compensation", "Tenure", "Advanced Analysis"]
)

# ---------------------- OVERVIEW TAB ------------------------------------------
with overview_tab:
    st.subheader("Overall Attrition Snapshot")

    # 1 Pie chart - Attrition distribution
    pie_fig = px.pie(
        filtered_df, names="Attrition", title="Overall Attrition Distribution",
        color="Attrition", hole=0.4
    )
    st.plotly_chart(pie_fig, use_container_width=True)
    st.caption("Shows proportion of current vs. exited employees.")

    # 2 Bar chart - Attrition rate by Department
    dept_attr = (
        filtered_df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
        .sort_values(by="AttritionRate", ascending=False)
    )
    bar_fig = px.bar(
        dept_attr, x="Department", y="AttritionRate", title="Attrition Rate by Department",
        text_auto=".1f"
    )
    bar_fig.update_layout(yaxis_title="Attrition Rate (%)")
    st.plotly_chart(bar_fig, use_container_width=True)
    st.caption("Highlights departments with higher turnover for targeted interventions.")

# ---------------------- DEMOGRAPHICS TAB --------------------------------------
with demographics_tab:
    st.subheader("Demographic Insights")

    # 3 Bar chart - Attrition by Gender
    gender_attr = (
        filtered_df.groupby("Gender")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
    )
    gender_fig = px.bar(
        gender_attr, x="Gender", y="AttritionRate", title="Attrition Rate by Gender",
        text_auto=".1f"
    )
    gender_fig.update_layout(yaxis_title="Attrition Rate (%)")
    st.plotly_chart(gender_fig, use_container_width=True)
    st.caption("Compares attrition rates between genders.")

    # 4 Histogram - Age distribution colored by Attrition
    age_hist = px.histogram(
        filtered_df, x="Age", color="Attrition", barmode="group",
        title="Age Distribution by Attrition Status"
    )
    st.plotly_chart(age_hist, use_container_width=True)
    st.caption("Identifies vulnerable age groups with higher attrition.")

    # 5 Boxplot - Age by Attrition
    age_box = px.box(
        filtered_df, x="Attrition", y="Age", points="outliers",
        title="Age Spread by Attrition Status"
    )
    st.plotly_chart(age_box, use_container_width=True)
    st.caption("Shows age variability among current vs. exited employees.")

    # 6 Stacked Bar - Marital Status vs Attrition Count
    marital_attr = filtered_df.pivot_table(
        index="MaritalStatus", columns="Attrition", values="EmployeeNumber", aggfunc="count"
    ).fillna(0)
    marital_fig = px.bar(
        marital_attr, title="Attrition Count by Marital Status", barmode="stack"
    )
    st.plotly_chart(marital_fig, use_container_width=True)
    st.caption("Assesses whether marital status affects turnover.")

# ---------------------- JOB & SATISFACTION TAB --------------------------------
with job_tab:
    st.subheader("Role & Satisfaction Analysis")

    # 7 Bar - Attrition rate by Job Role
    job_attr = (
        filtered_df.groupby("JobRole")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
        .sort_values(by="AttritionRate", ascending=False)
    )
    job_fig = px.bar(
        job_attr, x="AttritionRate", y="JobRole", orientation="h",
        title="Attrition Rate by Job Role", text_auto=".1f"
    )
    job_fig.update_layout(xaxis_title="Attrition Rate (%)", yaxis_title="")
    st.plotly_chart(job_fig, use_container_width=True)
    st.caption("Pinpoints high-risk roles needing retention strategies.")

    # 8 Line - Attrition rate by Job Level
    level_attr = (
        filtered_df.groupby("JobLevel")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
    )
    level_fig = px.line(level_attr, x="JobLevel", y="AttritionRate",
                        markers=True, title="Attrition Rate across Job Levels")
    st.plotly_chart(level_fig, use_container_width=True)
    st.caption("Tracks turnover trend as employees move up the hierarchy.")

    # 9 Boxplot - Job Satisfaction by Attrition
    js_box = px.box(
        filtered_df, x="Attrition", y="JobSatisfaction", points="all",
        title="Job Satisfaction Distribution by Attrition Status"
    )
    st.plotly_chart(js_box, use_container_width=True)
    st.caption("Low satisfaction scores often correlate with exits.")

    # 10 Scatter - Job Involvement vs Job Satisfaction
    ji_js_scatter = px.scatter(
        filtered_df, x="JobInvolvement", y="JobSatisfaction",
        color="Attrition", size="MonthlyIncome",
        title="Job Involvement vs Job Satisfaction"
    )
    st.plotly_chart(ji_js_scatter, use_container_width=True)
    st.caption("Visualizes interplay between involvement, satisfaction and attrinition.")
