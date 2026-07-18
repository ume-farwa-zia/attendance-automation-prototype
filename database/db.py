"""
SQLite schema + connection helper.

Plain sqlite3 (no ORM) so the schema is easy to read in one file and there
are zero extra moving parts for evaluators running this locally.
"""
import sqlite3
from contextlib import contextmanager

from config import Config


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id   TEXT PRIMARY KEY,
                full_name     TEXT NOT NULL,
                department    TEXT,
                phone         TEXT,
                email         TEXT
            );

            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id     TEXT NOT NULL,
                attendance_date TEXT NOT NULL,   -- YYYY-MM-DD
                check_in_time   TEXT NOT NULL,   -- ISO timestamp
                latitude        REAL NOT NULL,
                longitude       REAL NOT NULL,
                distance_m      REAL,            -- distance from registered office at check-in
                status          TEXT NOT NULL,   -- PRESENT / LATE / REJECTED_LOCATION / REJECTED_QR / DUPLICATE
                FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
            );
            """
        )


@contextmanager
def get_conn():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
