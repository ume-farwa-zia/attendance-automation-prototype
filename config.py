"""
Central configuration, loaded from environment variables (see .env.example).
Keeping all tunables in one place makes the geofence radius, office location,
and QR validity window easy to adjust per-deployment without touching code.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key-change-me")

    # SQLite database file
    DATABASE_PATH = BASE_DIR / "database" / "attendance.db"

    # Office geofence: registered location + allowed radius
    OFFICE_LATITUDE = float(os.getenv("OFFICE_LATITUDE", "27.7052"))
    OFFICE_LONGITUDE = float(os.getenv("OFFICE_LONGITUDE", "68.8574"))
    GEOFENCE_RADIUS_METERS = float(os.getenv("GEOFENCE_RADIUS_METERS", "150"))

    # Per-employee QR tokens are signed and expire after this many days
    # (long-lived since each employee reuses their own QR daily, unlike a
    # session QR — see docs/ARCHITECTURE.md for the reasoning).
    QR_TOKEN_VALIDITY_DAYS = int(os.getenv("QR_TOKEN_VALIDITY_DAYS", "365"))

    # Office start time used for late-arrival detection, 24h "HH:MM"
    OFFICE_START_TIME = os.getenv("OFFICE_START_TIME", "09:00")
    LATE_GRACE_MINUTES = int(os.getenv("LATE_GRACE_MINUTES", "15"))

    # Google Gemini API key for AI attendance insights.
    # If unset, ai_service falls back to rule-based summaries (see services/ai_service.py)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
