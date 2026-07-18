"""
End-to-end smoke test using Flask's test_client (no live server needed).
Run: python test_flow.py
"""
import pathlib

db_path = pathlib.Path("database/attendance.db")
if db_path.exists():
    db_path.unlink()

from app import app  # noqa: E402
from services.qr_service import sign_employee_token  # noqa: E402

client = app.test_client()

print("== register employee ==")
r = client.post("/api/employees", json={
    "employee_id": "EMP-001", "full_name": "Ayesha Khan",
    "department": "Engineering", "phone": "+923001234567",
})
print(r.get_json())

token = sign_employee_token("EMP-001")

print("\n== check-in INSIDE geofence (expect PRESENT or LATE) ==")
r = client.post("/checkin", json={"token": token, "latitude": 27.7053, "longitude": 68.8575})
print(r.get_json())

print("\n== duplicate check-in same day (expect DUPLICATE) ==")
r = client.post("/checkin", json={"token": token, "latitude": 27.7053, "longitude": 68.8575})
print(r.get_json())

print("\n== check-in OUTSIDE geofence, different employee (expect REJECTED_LOCATION) ==")
client.post("/api/employees", json={"employee_id": "EMP-002", "full_name": "Bilal Ahmed"})
token2 = sign_employee_token("EMP-002")
r = client.post("/checkin", json={"token": token2, "latitude": 27.8000, "longitude": 68.9000})
print(r.get_json())

print("\n== check-in with BAD/forged token (expect REJECTED_QR) ==")
r = client.post("/checkin", json={"token": "not-a-real-token", "latitude": 27.7053, "longitude": 68.8575})
print(r.get_json())

print("\n== attendance report ==")
r = client.get("/api/attendance/report")
import json
print(json.dumps(r.get_json(), indent=2, default=str))

print("\n== dashboard page renders ==")
r = client.get("/dashboard")
print("status:", r.status_code, "| contains 'AI Attendance Insights':", b"AI Attendance Insights" in r.data)
