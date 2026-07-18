"""
Loads sample_data/sample_employees.csv into the database and generates each
employee's QR code into static/qr/. Run once before demoing:

    python sample_data/seed.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import init_db
from models.employee import create_or_update_employee
from services.qr_service import generate_and_save_employee_qr

CSV_PATH = Path(__file__).resolve().parent / "sample_employees.csv"
QR_DIR = Path(__file__).resolve().parent.parent / "static" / "qr"


def main():
    init_db()
    QR_DIR.mkdir(parents=True, exist_ok=True)

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            create_or_update_employee(
                employee_id=row["employee_id"],
                full_name=row["full_name"],
                department=row.get("department"),
                phone=row.get("phone"),
                email=row.get("email"),
            )
            path = generate_and_save_employee_qr(row["employee_id"], QR_DIR)
            print(f"Seeded {row['employee_id']} ({row['full_name']}) -> QR at {path}")


if __name__ == "__main__":
    main()
