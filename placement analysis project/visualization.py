import pandas as pd
import plotly.express as px
import streamlit as st
from analyzer import PLACEMENT_ORDER

# --- Bin helpers ---
def bin_cgpa_value(cgpa):
    try:
        cgpa = float(cgpa)
    except (ValueError, TypeError):
        return "Unknown"
    if cgpa < 6: return "<6"
    elif cgpa < 7: return "6-7"
    elif cgpa < 8: return "7-8"
    elif cgpa < 9: return "8-9"
    else: return "9-10"
    
# --- Overall Placement Status ---
def plot_overall_status(df):
    # guard
    if df.empty:
        st.info("⚠ No placement status data available for selected filters.")
        return None

    df_n = df.copy()
    df_n = df_n[df_n["Placement_status"] != "Unknown"]

    total_students = df_n["usn"].nunique()
    if total_students == 0:
        st.info("⚠ No students available for selected filters.")
        return None

    # count unique students per status
    stats = (
        df_n.groupby("Placement_status")["usn"]
        .nunique()
        .reset_index(name="count")
        .sort_values("Placement_status")
    )
    stats["percent"] = stats["count"] / total_students * 100

    fig = px.bar(
        stats,
        x="Placement_status",
        y="percent",
        color="Placement_status",
        text="count",                   # show raw counts on bars
        height=500,
        title="Overall Placement Status Distribution (Percent)",
        category_orders={"Placement_status": PLACEMENT_ORDER},
    )

    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(yaxis_title="Percentage of Students (%)", xaxis_title="Placement Status")
    fig.update_traces(hovertemplate="Students: %{text}<br>Percent: %{y:.1f}%")

    st.plotly_chart(fig, use_container_width=True)
    return fig.layout.colorway

# --- Branch-wise ---
def plot_branch_wise(df):
    if df.empty:
        st.info("⚠ No branch-wise data available for selected filters.")
        return

    df_n = df.copy()
    df_n = df_n[df_n["Placement_status"] != "Unknown"]

    # compute unique students per branch (denominator)
    dept_totals = df_n.groupby("dept")["usn"].nunique().reset_index(name="dept_total")

    # counts per branch + status (unique students)
    stats = (
        df_n.groupby(["dept", "Placement_status"])["usn"]
        .nunique()
        .reset_index(name="count")
    )

    # merge the branch totals and compute percent (per-branch)
    stats = stats.merge(dept_totals, on="dept", how="left")
    stats["percent"] = (stats["count"] / stats["dept_total"]) * 100

    if stats.empty:
        st.info("⚠ No branch-wise data available for selected filters.")
        return

    # stacked percentage per branch (so each column sums to ~100%)
    fig = px.bar(
        stats,
        x="dept",
        y="percent",
        color="Placement_status",
        text="count",
        height=600,
        title="Branch-wise Placement Status (Percent of branch)",
        category_orders={"Placement_status": PLACEMENT_ORDER},
    )

    fig.update_traces(texttemplate="%{text}", textposition="inside")
    fig.update_layout(
        xaxis_title="Branch",
        yaxis_title="Percentage of Students (%)",
        legend_title="Placement Status",
        barmode="stack"
    )
    # hover shows both count and percent
    fig.update_traces(hovertemplate="Branch: %{x}<br>Students: %{text}<br>Percent: %{y:.1f}%")


    st.plotly_chart(fig, use_container_width=True)


# --- Batch-wise ---
def plot_batch_wise(df):
    if df.empty:
        st.info("⚠ No batch-wise data available for selected filters.")
        return

    df_n = df.copy()
    df_n = df_n[df_n["Placement_status"] != "Unknown"]

    # compute unique students per batch (denominator)
    batch_totals = df_n.groupby("batch")["usn"].nunique().reset_index(name="batch_total")

    # counts per batch + status (unique students)
    stats = (
        df_n.groupby(["batch", "Placement_status"])["usn"]
        .nunique()
        .reset_index(name="count")
    )

    # merge totals and compute percent (per-batch)
    stats = stats.merge(batch_totals, on="batch", how="left")
    stats["percent"] = (stats["count"] / stats["batch_total"]) * 100

    if stats.empty:
        st.info("⚠ No batch-wise data available for selected filters.")
        return

    # stacked percentage per batch
    fig = px.bar(
        stats,
        x="batch",
        y="percent",
        color="Placement_status",
        text="count",
        height=600,
        title="Batch-wise Placement Status (Percent of batch)",
        category_orders={"Placement_status": PLACEMENT_ORDER},
    )

    fig.update_traces(texttemplate="%{text}", textposition="inside")
    fig.update_layout(
        xaxis_title="Batch",
        yaxis_title="Percentage of Students (%)",
        legend_title="Placement Status",
        barmode="stack"
    )
    fig.update_traces(hovertemplate="Batch: %{x}<br>Students: %{text}<br>Percent: %{y:.1f}%")
    st.plotly_chart(fig, use_container_width=True)


# --- Top Recruiters ---
def plot_top_recruiters(df):
    # filter placed + shortlisted students
    filtered = df[df["Placement_status"].isin(["Placed", "Shortlisted"])]

    # count unique students per company
    top_recruiters = (
        filtered.groupby("company")["usn"]
        .nunique()
        .reset_index(name="hires")
        .sort_values("hires", ascending=False)
    )

    if top_recruiters.empty:
        st.info("⚠ No recruiter data available for selected filters.")
        return

    fig = px.bar(
        top_recruiters,
        x="company", y="hires", color="company",
        title="Top Recruiters (Placed + Shortlisted)",
        text="hires", height=600,
    )
    fig.update_layout(xaxis_tickangle=45, yaxis_title="Number of Students")
    st.plotly_chart(fig, use_container_width=True)


# --- CGPA-wise ---
def plot_cgpa_bins(df, color_set):
    df_all = df.copy()
    df_all["cgpa_bin"] = df_all["cgpa"].apply(bin_cgpa_value)

    # remove "Unknown" from analysis
    df_all = df_all[df_all["cgpa_bin"] != "Unknown"]

    # count unique students (avoid double-counting)
    stats_all = df_all.groupby("cgpa_bin")["usn"].nunique().reset_index(name="count")

    progressed_df = df_all[df_all["Placement_status"].isin(["Placed", "Shortlisted"])]
    stats_progressed = progressed_df.groupby("cgpa_bin")["usn"].nunique().reset_index(name="count")

    cgpa_order = ["<6", "6-7", "7-8", "8-9", "9-10"]

    col1, col2 = st.columns(2)
    with col1:
        fig_all = px.bar(
            stats_all, x="cgpa_bin", y="count", text="count", color="cgpa_bin",
            category_orders={"cgpa_bin": cgpa_order},
            color_discrete_sequence=color_set if color_set else None,
            title="CGPA Distribution (All Students)", height=500
        )
        fig_all.update_layout(xaxis_title="CGPA", yaxis_title="Number of Students")
        st.plotly_chart(fig_all, use_container_width=True)

    with col2:
        if stats_progressed.empty:
            st.info("⚠ No placed/shortlisted CGPA data for selected filters.")
        else:
            fig_progressed = px.bar(
                stats_progressed, x="cgpa_bin", y="count", text="count", color="cgpa_bin",
                category_orders={"cgpa_bin": cgpa_order},
                color_discrete_sequence=color_set if color_set else None,
                title="CGPA Distribution (Placed + Shortlisted)", height=500
            )
            fig_progressed.update_layout(xaxis_title="CGPA", yaxis_title="Number of Students")
            st.plotly_chart(fig_progressed, use_container_width=True)

# --- Salary Trends ---
def plot_salary_trends(df):
    stats = (
        df[df["Placement_status"] == "Placed"]
        .groupby("company")["ctc"]
        .agg(highest="max", lowest="min", average="mean")
        .reset_index()
    )
    if stats.empty:
        st.info("⚠ No salary data available for selected filters.")
        return

    fig = px.pie(
        stats, names="company", values="average",
        title="Average Salary Distribution by Company",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# --- Conversion Rates ---
def plot_conversion_rates(df):
    if df.empty:
        st.info("⚠ No conversion rate data available for selected filters.")
        return

    conversion = (
        df.groupby("company")
        .apply(lambda x: (x[x["Placement_status"] == "Placed"]["usn"].nunique()
                          / x["usn"].nunique() * 100) if x["usn"].nunique() > 0 else 0)
        .reset_index()
        .rename(columns={0: "conversion_rate"})
    )
    conversion = conversion.dropna(subset=["company"])

    if conversion.empty:
        st.info("⚠ No conversion rate data available for selected filters.")
        return

    conversion["conversion_rate"] = conversion["conversion_rate"].round(0).astype(int)

    fig = px.bar(
        conversion.sort_values("conversion_rate", ascending=False),
        x="company", y="conversion_rate", color="company",
        title="Interview-to-Offer Conversion Rate (%)",
        text="conversion_rate", height=600,
    )
    fig.update_layout(xaxis_tickangle=45, yaxis_title="Conversion Rate (%)")
    st.plotly_chart(fig, use_container_width=True)
