# Documentation — How to Run & Use

**Project:** Business Automation Research — SafeX Solutions
**Module:** SafeX AI Attendance Automation Prototype (Week 2, Group 25)

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full workflow diagram and
design rationale. This file covers setup and usage.

## 1. Install

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env: set OFFICE_LATITUDE/LONGITUDE to your real office location,
# set MANAGER_DASHBOARD_PASSWORD for protected dashboard access,
# and (optionally) GEMINI_API_KEY for live AI insights
```

## 2. Seed sample data (creates employees + their QR codes)

```bash
python sample_data/seed.py
```
This populates 5 sample employees (see `sample_data/sample_employees.csv`)
and writes each one's QR code image to `static/qr/<employee_id>.png`.

## 3. Run

```bash
python app.py
```
- Employee check-in page: `http://127.0.0.1:5000/`
- Manager dashboard: `http://127.0.0.1:5000/manager/login` then `/dashboard`

To actually scan a QR with your phone's camera, the browser needs camera +
location permission, which most browsers only grant over `https://` or
`http://localhost`. Testing on the same machine via `localhost:5000` works
out of the box; testing from a phone on the same network needs either a
tunnel (e.g. `ngrok http 5000`) or a self-signed HTTPS cert.

## 4. Try a check-in without a camera (e.g. for automated testing)

Open `static/qr/EMP-001.png` to see the QR image, or get the same payload
programmatically:
```python
from services.qr_service import sign_employee_token
token = sign_employee_token("EMP-001")
```
Then `POST /checkin` with `{"token": token, "latitude": ..., "longitude": ...}`.

## 5. Run the automated smoke test

```bash
python test_flow.py
```
Exercises: registration -> check-in inside geofence -> duplicate check-in ->
check-in outside geofence -> forged token -> report -> dashboard render.

## 6. Demo notebook

```bash
jupyter notebook notebook/demo.ipynb
```
Already executed with real sample outputs — open it directly to see results
without re-running, or re-run top-to-bottom yourself.

## 7. Enabling live Gemini AI insights

Set `GEMINI_API_KEY` in `.env` (get one from Google AI Studio). Without it,
the dashboard still works — `services/ai_service.py` uses a rule-based
summary (attendance rate, health score, recommendations) instead.

## 8. API reference (for other Group 25 modules to integrate against)

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/employees` | Register/update an employee, generates their QR |
| GET | `/api/employees` | List all employees |
| GET | `/api/employees/<id>/qr` | Fetch an employee's QR image |
| POST | `/checkin` | Process a check-in (token + lat/lon) |
| GET | `/api/attendance/report?date=YYYY-MM-DD` | Records + per-day/status summary |
| GET | `/manager/login` | Manager dashboard login page |
| POST | `/manager/login` | Authenticate manager access |
| GET | `/manager/logout` | Clear manager dashboard session |
| GET | `/dashboard` | Manager dashboard (HTML, protected) |

## 9. Project structure

```
app.py                    Flask entrypoint
config.py                 Environment-driven settings
database/db.py            SQLite schema + connection helper
models/employee.py        Employee data access
models/attendance.py      Attendance data access + reporting queries
routes/attendance_routes.py  Check-in page + endpoint
routes/dashboard_routes.py   Manager dashboard
routes/api_routes.py         JSON API
services/qr_service.py       Signed QR generation/verification
services/geofence_service.py Haversine geofence check
services/attendance_service.py  Check-in orchestration
services/ai_service.py       Gemini insights + rule-based fallback
templates/                   Jinja2 HTML (Bootstrap-based)
static/css, static/js        Styling + camera scanner script
static/qr/                   Generated employee QR images
sample_data/                 Sample employees CSV + seed script
notebook/demo.ipynb          Executed end-to-end demo
docs/                        This documentation + architecture + progress report
test_flow.py                 Automated smoke test
```
