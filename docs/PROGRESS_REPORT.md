# Progress Report — Week 2

**Project:** Business Automation Research — SafeX Solutions
**Module:** SafeX AI Attendance Automation Prototype
**Group:** 25 (Individual contribution)

## Summary

Built and tested a working Flask-based attendance automation prototype:
camera-based QR check-in, GPS geofence validation, duplicate/late detection,
SQLite storage, and a manager dashboard with AI-generated (Gemini, with a
rule-based fallback) attendance insights.

## Completed this week

- Designed per-employee signed QR tokens (not per-session), so scanning
  directly identifies the employee with no manual ID entry, and forged/
  handwritten IDs never verify.
- Built the Haversine-based geofence check against a configurable office
  location and radius.
- Built attendance orchestration logic: QR verification -> employee lookup
  -> duplicate-check-in prevention -> geofence check -> late-arrival
  detection -> record storage.
- Built the Gemini-based AI insights module (attendance rate, health score,
  recommendations), with a deterministic rule-based fallback so the
  dashboard is fully demoable without a paid API key.
- Built the employee check-in page (live camera QR scanning via
  html5-qrcode + GPS capture) and the manager dashboard, both with a
  Bootstrap-based professional blue/white theme.
- Wrote an automated smoke test and a fully executed demo notebook covering
  every path: successful check-in, late check-in, duplicate rejection,
  out-of-geofence rejection, and forged-token rejection.
- Wrote full architecture documentation (workflow diagram, component map,
  design trade-offs, known limitations).

## Challenges encountered

- Deciding between a per-session vs. per-employee QR design — chose
  per-employee since it avoids manual ID entry (a hard requirement) at the
  cost of needing duplicate/geofence checks to do the replay-protection work
  that token expiry would otherwise do.
- Making the AI insights step demoable without requiring a funded Gemini API
  key — solved with a rule-based fallback that returns the same response
  shape, so the dashboard template doesn't need to branch on which one ran.
- This module was originally attempted via an external AI assistant over
  several days without producing working code (repository had only a README
  and empty source files); rebuilt from scratch this session with everything
  tested end-to-end.

## Coordination with Group 25

The JSON API (`/api/employees`, `/checkin`, `/api/attendance/report`) is the
intended integration point for other members' modules — anyone building a
reporting layer, chatbot, or payroll hook can call into this service instead
of duplicating attendance logic.

## Next steps (if continued beyond Week 2)

- Add admin authentication for employee registration / QR issuance.
- Convert late-arrival time comparison to the office's explicit local
  timezone rather than naive UTC.
- Consider a secondary location signal (e.g. office Wi-Fi network match) to
  further harden against GPS spoofing.
