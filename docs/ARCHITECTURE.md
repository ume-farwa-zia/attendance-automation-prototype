# Architecture & Workflow

**SafeX AI Attendance Automation Prototype** — Business Automation Research, Group 25

## Workflow

```
Employee opens Attendance Portal (/  or  /checkin)
        │
        ▼
Browser requests Camera permission (html5-qrcode)
        │
        ▼
Browser requests Location permission
        │
        ▼
Employee scans their personal QR code
        │
        ▼
QR is decoded client-side -> signed token string
        │
        ▼
Browser captures current GPS coordinates
        │
        ▼
POST /checkin  { token, latitude, longitude }
        │
        ▼
Flask backend:
  1. Verify token signature -> extract employee_id
     (invalid/forged token -> REJECTED_QR)
  2. Confirm employee exists
     (unknown id -> UNKNOWN_EMPLOYEE)
  3. Check for an existing check-in today
     (already checked in -> DUPLICATE)
  4. Haversine distance vs. registered office location
     (outside GEOFENCE_RADIUS_METERS -> REJECTED_LOCATION)
  5. Compare check-in time vs. OFFICE_START_TIME + grace period
     -> PRESENT or LATE
  6. Store attendance record (SQLite)
        │
        ▼
Manager Login (/manager/login) -> Manager Dashboard (/dashboard)
  - Pulls today's records via Pandas
  - Computes present / late / absent counts
  - Sends stats to Gemini (or rule-based fallback) for a plain-language
    summary + health score + recommendations
```

## Component map

| Layer | File(s) | Responsibility |
|---|---|---|
| Entry point | `app.py` | Flask app factory, blueprint registration, DB init |
| Config | `config.py` | All environment-driven settings in one place |
| Database | `database/db.py` | SQLite schema (`employees`, `attendance`) + connection helper |
| Models | `models/employee.py`, `models/attendance.py` | Data-access functions |
| Services | `services/qr_service.py` | Signed per-employee QR generation/verification |
| Services | `services/geofence_service.py` | Haversine distance + geofence check |
| Services | `services/attendance_service.py` | Orchestrates the full check-in decision flow |
| Services | `services/ai_service.py` | Gemini-based insights, with rule-based fallback |
| Routes | `routes/attendance_routes.py` | Employee check-in page + `/checkin` endpoint |
| Routes | `routes/dashboard_routes.py` | Manager login + protected dashboard |
| Routes | `routes/api_routes.py` | JSON API: employee registration, QR issuance, reporting |
| Frontend | `templates/`, `static/` | Bootstrap UI, camera scanner JS |

## Why a per-employee QR (not a per-session QR)

Two designs were considered:

1. **Per-session QR** — one QR displayed at the entrance, regenerated daily/
   hourly. Simple, but anyone can photograph and share it during its validity
   window, and it doesn't identify *which* employee is checking in without
   also asking them to type an ID (which the brief explicitly said to avoid).
2. **Per-employee QR** (chosen) — each employee has their own signed QR
   (shown on their phone or printed once). It directly identifies the
   employee with no manual entry, and a forged/handwritten ID can never
   produce a valid signature.

The trade-off: a per-employee QR is longer-lived (it can't be rotated daily
without reissuing everyone a new code), so replay protection instead comes
from **geofence + one-check-in-per-day duplicate detection**, not from token
expiry. Someone with a stolen photo of the QR still can't check in unless
they are physically at the office, and can only do it once per day.

## Why Haversine for geofencing

Haversine gives great-circle distance between two lat/lon points without
needing external mapping APIs or paid services — accurate enough for an
office-sized geofence (tens to hundreds of meters) and zero external
dependencies.

## Why Gemini has a rule-based fallback

`GEMINI_API_KEY` requires a Google account and (for sustained use) billing.
So evaluators without a key can still see the dashboard fully working: if the
key is missing, or the Gemini call fails for any reason, `ai_service.py`
falls back to a deterministic rule-based summary — same response shape,
so the dashboard template doesn't need to know which path produced it.

## Known limitations

- Late-arrival detection compares check-in time to `OFFICE_START_TIME` using
  naive UTC time — a production version should store/convert to the office's
  local timezone explicitly.
- No admin authentication yet on `/api/employees` or QR issuance — would be
  needed before real deployment.
- GPS spoofing on rooted/jailbroken devices isn't detected; a production
  version might add a secondary signal (e.g. office Wi-Fi network match).
- Single-office geofence only; multi-branch orgs would need a per-branch
  geofence keyed by employee or a branch selector at check-in.
