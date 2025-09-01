import pandas as pd
from dbconfig import get_connection

PLACEMENT_ORDER = [
    "Not Eligible",
    "Unable to Clear 1st Round",
    "Unable to Clear Technicals",
    "Unable to Clear HR",
    "Shortlisted",
    "Placed",
    "Unable to Clear GD"
]

def map_status(code: int) -> str:
    mapping = {
        0: "Not Eligible",
        1: "Unable to Clear 1st Round",
        3: "Unable to Clear Technicals",
        4: "Unable to Clear HR",
        9: "Shortlisted",
        10: "Placed",
        2: "Unable to Clear GD"
    }
    return mapping.get(code, "Unknown")

def load_all_data():
    conn = get_connection()

    student_df = pd.read_sql("SELECT * FROM student", conn)
    company_df = pd.read_sql("SELECT * FROM company", conn)
    performance_df = pd.read_sql("SELECT * FROM performance", conn)
    hiring_df = pd.read_sql("SELECT * FROM hiring", conn)

    # Build combined_df with joins
    query = """
        SELECT s.usn, s.name, s.dept, s.batch, s.cgpa,
               p.status, c.company, h.ctc
        FROM student s
        LEFT JOIN performance p ON s.usn = p.usn
        LEFT JOIN hiring h ON p.cid = h.cid
        LEFT JOIN company c ON h.cid = c.cid
    """
    combined_df = pd.read_sql(query, conn)
    conn.close()

    combined_df["Placement_status"] = combined_df["status"].apply(map_status)
    combined_df["Placement_status"] = pd.Categorical(
        combined_df["Placement_status"],
        categories=PLACEMENT_ORDER,
        ordered=True
    )

    return student_df, company_df, performance_df, hiring_df, combined_df

def apply_filters(df, batch_filter="All", dept_filter="All", company_filter="All"):
    filtered = df.copy()

    # Batch filter
    if batch_filter == "Last 3 Years":
        all_batches = sorted(filtered["batch"].dropna().unique())
        if len(all_batches) >= 3:
            filtered = filtered[filtered["batch"].isin(all_batches[-3:])]
    elif batch_filter != "All":
        filtered = filtered[filtered["batch"] == batch_filter]

    # Department filter
    if dept_filter != "All":
        filtered = filtered[filtered["dept"] == dept_filter]

    # Company filter
    if company_filter != "All":
        filtered = filtered[filtered["company"] == company_filter]

    return filtered
