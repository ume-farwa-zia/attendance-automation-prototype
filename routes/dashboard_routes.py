"""
Manager dashboard: today's attendance stats + AI-generated insights.
"""
from datetime import datetime, timezone

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from models.attendance import get_todays_records_df
from models.employee import list_employees
from services.ai_service import generate_attendance_insights

dashboard_bp = Blueprint("dashboard", __name__)


def _manager_dashboard_allowed():
    expected_password = current_app.config.get("MANAGER_DASHBOARD_PASSWORD", "")
    return bool(expected_password) and session.get("manager_dashboard_access") is True


def _require_manager_dashboard_access():
    if _manager_dashboard_allowed():
        return None
    return redirect(url_for("dashboard.manager_login"))


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


@dashboard_bp.route("/manager/login", methods=["GET", "POST"])
def manager_login():
    expected_password = current_app.config.get("MANAGER_DASHBOARD_PASSWORD", "")
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == expected_password:
            session["manager_dashboard_access"] = True
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid manager password.", "danger")

    return render_template("manager_login.html")


@dashboard_bp.route("/manager/logout")
def manager_logout():
    session.pop("manager_dashboard_access", None)
    return redirect(url_for("attendance.checkin_page"))


@dashboard_bp.route("/dashboard")
def dashboard():
    access_result = _require_manager_dashboard_access()
    if access_result is not None:
        return access_result

    stats, df = _compute_today_stats()
    insights = generate_attendance_insights(stats)
    records = df.to_dict(orient="records") if not df.empty else []
    return render_template("dashboard.html", stats=stats, insights=insights, records=records)
