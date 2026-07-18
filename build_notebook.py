import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(t): cells.append(nbf.v4.new_markdown_cell(t))
def code(t): cells.append(nbf.v4.new_code_cell(t))

md("""# SafeX AI Attendance Automation — Demo Notebook
**Business Automation Research — Group 25 — Week 2 Individual Module**

Demonstrates the full flow using Flask's `test_client`, so it runs standalone
without a separate server process. To run the real app with camera QR
scanning in a browser, see the main `README.md`.

**Flow demonstrated:**
1. Register a sample employee + generate their QR code
2. Check in from *inside* the office geofence -> `PRESENT`/`LATE`
3. Duplicate check-in same day -> `DUPLICATE`
4. Check in from *outside* the geofence -> `REJECTED_LOCATION`
5. Check in with a forged/invalid QR token -> `REJECTED_QR`
6. Pull the attendance report + AI-generated dashboard insights
""")

code("""import sys, os, pathlib
sys.path.insert(0, os.path.abspath('..'))
os.chdir('..')

db_path = pathlib.Path("database/attendance.db")
if db_path.exists():
    db_path.unlink()

from app import app
from services.qr_service import sign_employee_token, generate_and_save_employee_qr

client = app.test_client()
""")

md("## 1. Register a sample employee + view their generated QR code")
code("""resp = client.post("/api/employees", json={
    "employee_id": "EMP-001",
    "full_name": "Ayesha Khan",
    "department": "Engineering",
    "phone": "+923001234567",
})
resp.get_json()
""")

code("""from IPython.display import Image, display
from pathlib import Path
qr_path = Path("static/qr/EMP-001.png")
if not qr_path.exists():
    generate_and_save_employee_qr("EMP-001", Path("static/qr"))
display(Image(filename=str(qr_path)))
""")

md("""## 2. Sample Input/Output — Check-in inside the geofence
This is what happens when the employee scans their QR (decoded token below) and
their phone reports GPS coordinates ~15m from the registered office.""")
code("""token = sign_employee_token("EMP-001")
result = client.post("/checkin", json={"token": token, "latitude": 27.7053, "longitude": 68.8575})
result.get_json()
""")

md("## 3. Duplicate check-in same day — should be rejected, not double-counted")
code("""result = client.post("/checkin", json={"token": token, "latitude": 27.7053, "longitude": 68.8575})
result.get_json()
""")

md("## 4. Check-in from outside the geofence (different employee)")
code("""client.post("/api/employees", json={"employee_id": "EMP-002", "full_name": "Bilal Ahmed", "department": "Sales"})
token2 = sign_employee_token("EMP-002")
result = client.post("/checkin", json={"token": token2, "latitude": 27.8000, "longitude": 68.9000})
result.get_json()
""")

md("## 5. Check-in with a forged/invalid QR token — never trusted without a valid signature")
code("""result = client.post("/checkin", json={"token": "forged-token-attempt", "latitude": 27.7053, "longitude": 68.8575})
result.get_json()
""")

md("## 6. Attendance report (Pandas-based)")
code("""import pandas as pd
report = client.get("/api/attendance/report").get_json()
pd.DataFrame(report["records"])
""")

md("## 7. AI-generated dashboard insights\\nUses Gemini if `GEMINI_API_KEY` is set in `.env`, otherwise a rule-based fallback (shown below).")
code("""dash = client.get("/dashboard")
print("dashboard status:", dash.status_code)

from services.ai_service import generate_attendance_insights
sample_stats = {"date": "2026-07-16", "total_employees": 5, "present": 2, "late": 1, "absent": 2}
generate_attendance_insights(sample_stats)
""")

nb['cells'] = cells
with open('notebook/demo.ipynb', 'w') as f:
    nbf.write(nb, f)
print("done")
