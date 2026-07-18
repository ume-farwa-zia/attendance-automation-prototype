"""
Attendance data-access functions: recording check-ins, duplicate detection,
and pulling records for reporting/dashboard use.
"""
from datetime import datetime, timezone

import pandas as pd

from database.db import get_conn


def already_checked_in_today(employee_id, attendance_date):
    with get_conn() as conn:
        row = conn.execute(
            """SELECT 1 FROM attendance
               WHERE employee_id = ? AND attendance_date = ? AND status IN ('PRESENT', 'LATE')
               LIMIT 1""",
            (employee_id, attendance_date),
        ).fetchone()
    return row is not None


def record_attendance(employee_id, attendance_date, check_in_time, latitude, longitude, distance_m, status):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO attendance
               (employee_id, attendance_date, check_in_time, latitude, longitude, distance_m, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (employee_id, attendance_date, check_in_time, latitude, longitude, distance_m, status),
        )


def get_all_records_df():
    with get_conn() as conn:
        df = pd.read_sql_query(
            """SELECT a.*, e.full_name, e.department
               FROM attendance a JOIN employees e ON a.employee_id = e.employee_id
               ORDER BY a.check_in_time DESC""",
            conn,
        )
    return df


def get_todays_records_df():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    df = get_all_records_df()
    if df.empty:
        return df
    return df[df["attendance_date"] == today]
