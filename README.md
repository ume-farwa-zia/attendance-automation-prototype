# SafeX AI Attendance Automation Prototype

QR + GPS geofence attendance system with a Flask backend, SQLite storage,
and an AI-powered (Gemini) manager dashboard — built as an individual Week 2
module for SafeX Solutions' Business Automation Research project (Group 25).

Full docs: [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md)
Architecture & workflow: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
Progress report: [`docs/PROGRESS_REPORT.md`](docs/PROGRESS_REPORT.md)
Demo notebook: [`notebook/demo.ipynb`](notebook/demo.ipynb)

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env
# set MANAGER_DASHBOARD_PASSWORD in .env for dashboard access
python sample_data/seed.py      # creates sample employees + their QR codes
python app.py                   # http://127.0.0.1:5000
```

- Employee check-in: `/` (camera QR scan + GPS)
- Manager dashboard: `/manager/login` then `/dashboard`

Or explore without a server:
```bash
python test_flow.py                    # automated smoke test
jupyter notebook notebook/demo.ipynb   # executed walkthrough with sample I/O
```

## Features

- **QR check-in** — each employee has a signed, forgery-proof QR code
  (`services/qr_service.py`), scanned live via the device camera
  (`html5-qrcode`), no manual ID entry.
- **GPS geofence** — Haversine-distance check against a configurable office
  location and radius (`services/geofence_service.py`).
- **Duplicate + late detection** — one check-in per employee per day; late
  arrivals flagged against a configurable office start time + grace period.
- **AI attendance insights** — Gemini-generated summary, health score, and
  recommendations on the dashboard, with a rule-based fallback if no API key
  is configured.
- **Manager dashboard** — protected manager-only access for today's
  present/late/absent counts + full record table, Bootstrap-based
  professional UI.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full workflow
diagram and design rationale.
