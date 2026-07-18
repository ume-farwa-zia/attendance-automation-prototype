"""
Attendance check-in orchestration: ties together QR verification, geofence
validation, duplicate-check-in prevention, and late-arrival detection.
"""
from datetime import datetime, time, timezone

from config import Config
from models.attendance import already_checked_in_today, record_attendance
from models.employee import get_employee
from services.geofence_service import is_within_geofence
from services.qr_service import verify_employee_token


def _is_late(now: datetime) -> bool:
    start_h, start_m = map(int, Config.OFFICE_START_TIME.split(":"))
    total_minutes = start_h * 60 + start_m + Config.LATE_GRACE_MINUTES
    cutoff = time(hour=(total_minutes // 60) % 24, minute=total_minutes % 60)
    return now.time() > cutoff


def process_checkin(token: str, latitude: float, longitude: float) -> dict:
    """
    Returns a result dict:
      { employee_id, status, distance_m, checkin_time, message }
    status is one of:
      PRESENT / LATE / REJECTED_QR / REJECTED_LOCATION / DUPLICATE / UNKNOWN_EMPLOYEE
    """
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    employee_id = verify_employee_token(token)
    if employee_id is None:
        return {
            "employee_id": None,
            "status": "REJECTED_QR",
            "distance_m": None,
            "checkin_time": now.isoformat(),
            "message": "QR code could not be verified. Please use your official employee QR.",
        }

    employee = get_employee(employee_id)
    if employee is None:
        return {
            "employee_id": employee_id,
            "status": "UNKNOWN_EMPLOYEE",
            "distance_m": None,
            "checkin_time": now.isoformat(),
            "message": "This employee ID is not registered in the system.",
        }

    if already_checked_in_today(employee_id, today):
        return {
            "employee_id": employee_id,
            "status": "DUPLICATE",
            "distance_m": None,
            "checkin_time": now.isoformat(),
            "message": f"{employee['full_name']} has already checked in today.",
        }

    inside, distance = is_within_geofence(
        latitude, longitude, Config.OFFICE_LATITUDE, Config.OFFICE_LONGITUDE,
        Config.GEOFENCE_RADIUS_METERS,
    )

    if not inside:
        record_attendance(employee_id, today, now.isoformat(), latitude, longitude, round(distance, 1), "REJECTED_LOCATION")
        return {
            "employee_id": employee_id,
            "status": "REJECTED_LOCATION",
            "distance_m": round(distance, 1),
            "checkin_time": now.isoformat(),
            "message": f"You are {round(distance)}m from the office — outside the allowed {Config.GEOFENCE_RADIUS_METERS}m radius.",
        }

    status = "LATE" if _is_late(now) else "PRESENT"
    record_attendance(employee_id, today, now.isoformat(), latitude, longitude, round(distance, 1), status)
    return {
        "employee_id": employee_id,
        "status": status,
        "distance_m": round(distance, 1),
        "checkin_time": now.isoformat(),
        "message": f"Welcome {employee['full_name']}! Attendance marked as {status}.",
    }
