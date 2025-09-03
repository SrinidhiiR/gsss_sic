import pandas as pd
import plotly.express as px
import streamlit as st
from analyzer import PLACEMENT_ORDER

# --- Utils ---
def bin_cgpa_value(cgpa):
    try: 
        cgpa = float(cgpa)
    except: 
        return "Unknown"
    return "<6" if cgpa < 6 else "6-7" if cgpa < 7 else "7-8" if cgpa < 8 else "8-9" if cgpa < 9 else "9-10"

def make_bar(df, x, y, color, title, text="count", barmode=None, order=None, height=500, angle=0, hover=None):
    fig = px.bar(df, x=x, y=y, color=color, text=text, height=height,
                 title=title, category_orders={color: order} if order else None)
    fig.update_traces(texttemplate="%{text}", textposition="inside", hovertemplate=hover)
    fig.update_layout(xaxis_title=x.capitalize(), yaxis_title=y.capitalize(),
                      legend_title=color.replace("_"," ").title(), xaxis_tickangle=angle, barmode=barmode)
    st.plotly_chart(fig, use_container_width=True)

# --- Overall Placement ---
def plot_overall_status(df):
    df = df[df["Placement_status"] != "Unknown"]
    total = df["usn"].nunique()
    if total == 0: 
        return st.info("⚠ No placement data available.")
    stats = df.groupby("Placement_status")["usn"].nunique().reset_index(name="count")
    stats["percent"] = stats["count"]/total*100
    make_bar(stats, "Placement_status","percent","Placement_status",
             "Overall Placement Status (%)", text="count", order=PLACEMENT_ORDER)

    # --- Text Analysis ---
    placed = stats.loc[stats["Placement_status"] == "Placed", "percent"].sum()
    shortlisted = stats.loc[stats["Placement_status"] == "Shortlisted", "percent"].sum()
    not_placed = 100 - (placed + shortlisted)

    st.markdown(f"""
    🔎 **Analysis:**  
    - Out of **{total} students**, **{placed:.1f}% were placed** and **{shortlisted:.1f}% shortlisted**.  
    - Around **{not_placed:.1f}% of students could not secure offers**.  
    """)

# --- Branch/Batch wise ---
def plot_group_wise(df, group_col, title):
    df = df[df["Placement_status"] != "Unknown"]
    if df.empty: 
        return st.info(f"⚠ No {group_col}-wise data available.")
    totals = df.groupby(group_col)["usn"].nunique().reset_index(name="total")
    stats = df.groupby([group_col,"Placement_status"])["usn"].nunique().reset_index(name="count")
    stats = stats.merge(totals, on=group_col)
    stats["percent"] = stats["count"]/stats["total"]*100
    if stats.empty: 
        return st.info(f"⚠ No {group_col}-wise data available.")
    make_bar(stats, group_col,"percent","Placement_status",
             f"{title} Placement Status (%)", text="count", order=PLACEMENT_ORDER, barmode="stack", height=600)

    # --- Text Analysis ---
    best_group = stats.groupby(group_col)["percent"].mean().idxmax()
    worst_group = stats.groupby(group_col)["percent"].mean().idxmin()
    st.markdown(f"""
    🔎 **Analysis:**  
    - **{best_group}** shows the **highest placement performance** among all {group_col}s.  
    - **{worst_group}** has the **lowest placement outcomes**. 
    """)

def plot_branch_wise(df): 
    plot_group_wise(df,"dept","Branch-wise")

def plot_batch_wise(df):  
    plot_group_wise(df,"batch","Batch-wise")

# --- Top Recruiters ---
def plot_top_recruiters(df):
    top = df[df["Placement_status"].isin(["Placed","Shortlisted"])]
    top = top.groupby("company")["usn"].nunique().reset_index(name="hires").sort_values("hires",ascending=False)
    if top.empty: 
        return st.info("⚠ No recruiter data.")
    
    make_bar(top,"company","hires","company","Top Recruiters (Placed+Shortlisted)", text="hires", height=600, angle=45)

    # --- Text Analysis ---
    top_company = top.iloc[0]["company"]
    top_hires = top.iloc[0]["hires"]
    st.markdown(f"""
    🔎 **Analysis:**  
    - **{top_company}** emerged as the leading recruiter with **{top_hires} hires**.  
    """)

# --- CGPA bins ---
def plot_cgpa_bins(df, colors):
    df["cgpa_bin"] = df["cgpa"].apply(bin_cgpa_value)
    df = df[df["cgpa_bin"]!="Unknown"]
    order = ["<6","6-7","7-8","8-9","9-10"]
    col1,col2 = st.columns(2)

    with col1:
        stats_all = df.groupby("cgpa_bin")["usn"].nunique().reset_index(name="count")
        make_bar(stats_all,"cgpa_bin","count","cgpa_bin","CGPA Distribution (All)", order=order, height=500)

    with col2:
        placed = df[df["Placement_status"].isin(["Placed","Shortlisted"])]
        if placed.empty: 
            st.info("⚠ No placed/shortlisted CGPA data.")
        else:
            stats_p = placed.groupby("cgpa_bin")["usn"].nunique().reset_index(name="count")
            make_bar(stats_p,"cgpa_bin","count","cgpa_bin","CGPA Distribution (Placed+Shortlisted)", order=order, height=500)

    # --- Text Analysis ---
    if not df.empty:
        dominant_bin = df["cgpa_bin"].mode()[0]
        st.markdown(f"""
        🔎 **Analysis:**  
        - Most students who are not placed fall in the **{dominant_bin} CGPA range**.  
        """)

# --- Salary Trends ---
def plot_salary_trends(df):
    stats = df[df["Placement_status"]=="Placed"].groupby("company")["ctc"].agg(highest="max",lowest="min",average="mean").reset_index()
    if stats.empty: 
        return st.info("⚠ No salary data.")
    fig = px.pie(stats, names="company", values="average", title="Average Salary Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

    # --- Text Analysis ---
    top_salary = stats["average"].max()
    top_company = stats.loc[stats["average"].idxmax(), "company"]
    st.markdown(f"""
    🔎 **Analysis:**  
    - **{top_company}** offers the **highest average salary** of approximately **{top_salary:.2f} LPA**.
    """)

# --- Conversion Rates ---
def plot_conversion_rates(df):
    if df.empty: 
        return st.info("⚠ No conversion rate data.")
    conv = df.groupby("company").apply(lambda x: x[x["Placement_status"]=="Placed"]["usn"].nunique()/x["usn"].nunique()*100 if x["usn"].nunique()>0 else 0).reset_index().rename(columns={0:"conversion"})
    if conv.empty: 
        return st.info("⚠ No conversion rate data.")
    conv["conversion"] = conv["conversion"].round().astype(int)
    make_bar(conv.sort_values("conversion",ascending=False),"company","conversion","company","Interview-to-Offer Conversion (%)", text="conversion", height=600, angle=45)

    # --- Text Analysis ---
    best_company = conv.loc[conv["conversion"].idxmax(), "company"]
    best_rate = conv["conversion"].max()
    st.markdown(f"""
    🔎 **Analysis:**  
    - **{best_company}** shows the **highest interview-to-offer conversion rate** at **{best_rate}%**.  
    """)
