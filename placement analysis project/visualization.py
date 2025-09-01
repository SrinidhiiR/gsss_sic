# visualization.py
import pandas as pd
import plotly.express as px
import streamlit as st
from analyzer import PLACEMENT_ORDER

# --- Bin helpers ---
def bin_cgpa(cgpa):
    try:
        cgpa = float(cgpa)
    except (ValueError, TypeError):
        return None
    if cgpa < 6: return "<6"
    elif cgpa < 7: return "6-7"
    elif cgpa < 8: return "7-8"
    elif cgpa < 9: return "8-9"
    else: return "9-10"
    
# --- Overall Placement Status ---
def plot_overall_status(df):
    stats = df[df["Placement_status"] != "Unknown"] \
                .groupby("Placement_status").size().reset_index(name="count")

    fig = px.bar(
        stats, x="Placement_status", y="count", color="Placement_status",
        text="count", height=500,
        title="Overall Placement Status Distribution",
        category_orders={"Placement_status": PLACEMENT_ORDER}
    )
    st.plotly_chart(fig, use_container_width=True)

    return fig.layout.colorway  # return color scheme

# --- Branch-wise ---
def plot_branch_wise(df):
    stats = (
        df[df["Placement_status"] != "Unknown"]
        .groupby(["dept", "Placement_status"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        stats,
        x="dept", y="count", color="Placement_status",
        barmode="group", text="count", height=600,
        title="Branch-wise Placement Status Comparison",
        hover_data=["dept", "Placement_status", "count"],
        category_orders={"Placement_status": PLACEMENT_ORDER}
    )
    fig.update_layout(xaxis_title="Branch", yaxis_title="Number of Students", legend_title="Placement Status")
    st.plotly_chart(fig, use_container_width=True)

# --- Batch-wise ---
def plot_batch_wise(df):
    stats = (
        df[df["Placement_status"] != "Unknown"]
        .groupby(["batch", "Placement_status"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        stats,
        x="batch", y="count", color="Placement_status",
        barmode="group", text="count", height=600,
        title="Batch-wise Placement Status Comparison",
        hover_data=["batch", "Placement_status", "count"],
        category_orders={"Placement_status": PLACEMENT_ORDER}
    )
    fig.update_layout(xaxis_title="Batch", yaxis_title="Number of Students", legend_title="Placement Status")
    st.plotly_chart(fig, use_container_width=True)

# --- Top Recruiters ---
def plot_top_recruiters(df):
    top_recruiters = (
        df[df["Placement_status"] == "Placed"]["company"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    top_recruiters.columns = ["company", "hires"]

    fig = px.bar(
        top_recruiters.sort_values("hires", ascending=False),
        x="company", y="hires", color="company",
        title="Top Recruiters",
        text="hires", height=600,
    )
    fig.update_layout(xaxis_tickangle=0)
    st.plotly_chart(fig, use_container_width=True)

# --- CGPA-wise ---
def plot_cgpa_bins(df, color_set):
    df_all = df.copy()
    df_all["cgpa"] = df_all["cgpa"].apply(bin_cgpa)
    df_all = df_all.dropna(subset=["cgpa"])

    progressed_df = df_all[df_all["Placement_status"].isin(["Placed", "Shortlisted"])]

    stats_all = df_all.groupby("cgpa").size().reset_index(name="count")
    stats_progressed = progressed_df.groupby("cgpa").size().reset_index(name="count")

    col1, col2 = st.columns(2)
    with col1:
        fig_all = px.bar(
            stats_all, x="cgpa", y="count", text="count", color="cgpa",
            category_orders={"cgpa": ["<6", "6-7", "7-8", "8-9", "9-10"]},
            color_discrete_sequence=color_set,
            title="CGPA Distribution (All Students)", height=500
        )
        st.plotly_chart(fig_all, use_container_width=True)

    with col2:
        fig_progressed = px.bar(
            stats_progressed, x="cgpa", y="count", text="count", color="cgpa",
            category_orders={"cgpa": ["<6", "6-7", "7-8", "8-9", "9-10"]},
            color_discrete_sequence=color_set,
            title="CGPA Distribution (Placed + Shortlisted)", height=500
        )
        st.plotly_chart(fig_progressed, use_container_width=True)

# --- Salary Trends ---
def plot_salary_trends(df):
    stats = (
        df[df["Placement_status"] == "Placed"]
        .groupby("company")["ctc"]
        .agg(highest="max", lowest="min", average="mean")
        .reset_index()
    )

    fig = px.pie(
        stats, names="company", values="average",
        title="Average Salary Distribution by Company",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# --- Conversion Rates ---
def plot_conversion_rates(df):
    conversion = (
        df.groupby("company")
        .apply(lambda x: (x[x["Placement_status"] == "Placed"]["usn"].nunique()
                          / x["usn"].nunique() * 100) if x["usn"].nunique() > 0 else 0)
        .reset_index()
        .rename(columns={0: "conversion_rate"})
    )
    conversion = conversion.dropna(subset=["company"])
    conversion["conversion_rate"] = conversion["conversion_rate"].round(0).astype(int)

    fig = px.bar(
        conversion.sort_values("conversion_rate", ascending=False),
        x="company", y="conversion_rate", color="company",
        title="Interview-to-Offer Conversion Rate (%)",
        text="conversion_rate", height=600,
    )
    fig.update_layout(xaxis_tickangle=45, yaxis_title="Conversion Rate (%)")
    st.plotly_chart(fig, use_container_width=True)
