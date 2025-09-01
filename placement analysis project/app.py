# app.py
import streamlit as st
import pandas as pd
from analyzer import load_hiring_records
import visualization as vz

# --- Page Config ---
st.set_page_config(page_title="Placement Analysis Dashboard", layout="wide")
st.title("📊 Placement Analysis Dashboard")

# --- Load data initially ---
(
    df, pivot_df,
    student1_df, student2_df, company_df,
    performance_df, hiring_df
) = load_hiring_records()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Department options
dept_options = ["All"] + sorted(student1_df["dept"].dropna().unique().tolist())
dept_filter = st.sidebar.selectbox("Select Department", dept_options)

# Batch options (with "Last 3 Years" + "All")
batch_list = sorted(student1_df["batch"].dropna().unique().tolist())
batch_options = ["All", "Last 3 Years"] + batch_list
batch_filter = st.sidebar.selectbox("Select Batch", batch_options)

# Company options
company_options = ["All"] + sorted(company_df["company"].dropna().unique().tolist())
company_filter = st.sidebar.selectbox("Select Company", company_options)

# Apply filters again
(
    df, pivot_df,
    student1_df, student2_df, company_df,
    performance_df, hiring_df
) = load_hiring_records(dept_filter, batch_filter, company_filter)

# --- KPI Summary Cards ---
st.subheader("📌 Key Placement Metrics")

# Total students comes from student1 (master list)
total_students = student1_df["usn"].nunique()

# Placed & shortlisted come from filtered df
placed_students = df[df["Placement_status"] == "Placed"]["usn"].nunique()
shortlisted_students = df[df["Placement_status"] == "Shortlisted"]["usn"].nunique()
not_placed = total_students - placed_students
placement_rate = ( (placed_students + shortlisted_students) / total_students * 100) if total_students > 0 else 0


card_style = """
    <div style="background-color:{bg}; padding:20px; border-radius:15px;
                box-shadow:0px 4px 10px rgba(0,0,0,0.25); text-align:center;">
        <h2 style="margin:0; font-size:28px; color:#212121;">{value}</h2>
        <p style="margin:0; font-size:16px; font-weight:bold; color:#424242;">{label}</p>
    </div>
"""

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(card_style.format(bg="#bbdefb", value=total_students, label="🎓 Total Students"), unsafe_allow_html=True)
with col2:
    st.markdown(card_style.format(bg="#c8e6c9", value=placed_students, label="✅ Placed Students"), unsafe_allow_html=True)
with col3:
    st.markdown(card_style.format(bg="#ffe0b2", value=shortlisted_students, label="📝 Shortlisted"), unsafe_allow_html=True)
with col4:
    st.markdown(card_style.format(bg="#ffcdd2", value=f"{placement_rate:.2f}%", label="📉 Placement Rate"), unsafe_allow_html=True)

st.markdown("---")

# --- Graphs Section ---
st.subheader("📊 Placement Analysis Graphs")
color_set = vz.plot_overall_status(df) 
vz.plot_top_recruiters(df)
vz.plot_batch_wise(df)
vz.plot_branch_wise(df)
vz.plot_salary_trends(df)
vz.plot_conversion_rates(df)
vz.plot_cgpa_bins(df, color_set)    

st.markdown("---")

# --- Hiring Records Table ---
st.subheader("📑 Hiring Records Table")
if not pivot_df.empty:
    st.dataframe(pivot_df, use_container_width=True, height=500)
    csv_data = pivot_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="hiring_records.csv",
        mime="text/csv"
    )
else:
    st.info("⚠ No hiring records available for the selected filters.")
