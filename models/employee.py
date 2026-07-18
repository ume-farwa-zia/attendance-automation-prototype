"""
Employee data-access functions.
"""
from database.db import get_conn


def create_or_update_employee(employee_id, full_name, department=None, phone=None, email=None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO employees (employee_id, full_name, department, phone, email)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(employee_id) DO UPDATE SET
                 full_name=excluded.full_name, department=excluded.department,
                 phone=excluded.phone, email=excluded.email""",
            (employee_id, full_name, department, phone, email),
        )
    return get_employee(employee_id)


def get_employee(employee_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM employees WHERE employee_id = ?", (employee_id,)
        ).fetchone()
    return dict(row) if row else None


def list_employees():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM employees ORDER BY full_name").fetchall()
    return [dict(r) for r in rows]
