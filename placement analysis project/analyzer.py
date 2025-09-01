# analyzer.py
import pandas as pd
from dbconfig import get_connection

# --- Placement Status Mapping + Global Order ---
PLACEMENT_ORDER = [
    "Not Eligible",
    "Unable to Clear 1st Round",
    "Unable to Clear Technicals",
    "Unable to Clear HR",
    "Shortlisted",
    "Placed"
]

def map_status(code: int) -> str:
    mapping = {
        0: "Not Eligible",
        1: "Unable to Clear 1st Round",
        3: "Unable to Clear Technicals",
        4: "Unable to Clear HR",
        9: "Shortlisted",
        10: "Placed"
    }
    return mapping.get(code, "Unknown")


def load_hiring_records(dept_filter=None, batch_filter=None, company_filter=None):
    conn = get_connection()

    # Load raw tables
    student1_df = pd.read_sql("SELECT * FROM student1", conn)
    student2_df = pd.read_sql("SELECT * FROM student", conn)
    company_df = pd.read_sql("SELECT * FROM company", conn)
    performance_df = pd.read_sql("SELECT * FROM performance", conn)
    hiring_df = pd.read_sql("SELECT * FROM hiring", conn)

    # Merge using LEFT JOIN (include all students)
    merged_query = """
        SELECT s.usn, s.name, s.dept, s.batch, s.cgpa,
               p.status, c.company, h.cid, h.date, h.ctc
        FROM student s
        LEFT JOIN performance p ON s.usn = p.usn
        LEFT JOIN hiring h ON p.cid = h.cid
        LEFT JOIN company c ON h.cid = c.cid
    """
    combined_df = pd.read_sql(merged_query, conn)
    conn.close()

    # Apply status mapping + enforce category order
    combined_df["Placement_status"] = combined_df["status"].apply(map_status)
    combined_df["Placement_status"] = pd.Categorical(
        combined_df["Placement_status"],
        categories=PLACEMENT_ORDER,
        ordered=True
    )

    # --- Apply filters ---
    if dept_filter and dept_filter != "All":
        combined_df = combined_df[combined_df["dept"] == dept_filter]
    if batch_filter and batch_filter != "All" and batch_filter != "Last 3 Years":
        combined_df = combined_df[combined_df["batch"] == batch_filter]
    if company_filter and company_filter != "All":
        combined_df = combined_df[combined_df["company"] == company_filter]

    # Handle "Last 3 Years"
    if batch_filter == "Last 3 Years":
        all_batches = sorted(student1_df["batch"].dropna().unique())
        if len(all_batches) >= 3:
            last_three = all_batches[-3:]
            combined_df = combined_df[combined_df["batch"].isin(last_three)]

    # Pivot: student-company matrix
    pivot_df = combined_df.pivot_table(
        index=["usn", "name", "dept", "batch", "cgpa"],
        columns="company",
        values="Placement_status",
        aggfunc="first"
    ).reset_index()

    return (
        combined_df, pivot_df,
        student1_df, student2_df, company_df,
        performance_df, hiring_df
    )
