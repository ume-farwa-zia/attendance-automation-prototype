"""
Manager dashboard: today's attendance stats + AI-generated insights.
"""
from datetime import datetime, timezone

from flask import Blueprint, render_template

from models.attendance import get_todays_records_df
from models.employee import list_employees
from services.ai_service import generate_attendance_insights

dashboard_bp = Blueprint("dashboard", __name__)


def _compute_today_stats():
    employees = list_employees()
    total = len(employees)
    df = get_todays_records_df()

    present = int((df["status"] == "PRESENT").sum()) if not df.empty else 0
    late = int((df["status"] == "LATE").sum()) if not df.empty else 0
    checked_in_ids = set(df.loc[df["status"].isin(["PRESENT", "LATE"]), "employee_id"]) if not df.empty else set()
    absent = total - len(checked_in_ids)

    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_employees": total,
        "present": present,
        "late": late,
        "absent": absent,
    }, df


@dashboard_bp.route("/dashboard")
def dashboard():
    stats, df = _compute_today_stats()
    insights = generate_attendance_insights(stats)
    records = df.to_dict(orient="records") if not df.empty else []
    return render_template("dashboard.html", stats=stats, insights=insights, records=records)
