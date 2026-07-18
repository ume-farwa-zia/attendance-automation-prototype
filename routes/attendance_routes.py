"""
Employee-facing routes: the check-in page (camera QR scan + GPS capture)
and the endpoint that actually processes a check-in.
"""
from flask import Blueprint, jsonify, render_template, request

from services.attendance_service import process_checkin

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/")
@attendance_bp.route("/checkin")
def checkin_page():
    """Renders the employee-facing page with the camera QR scanner."""
    return render_template("index.html")


@attendance_bp.route("/checkin", methods=["POST"])
def checkin():
    data = request.get_json(force=True) or {}
    token = data.get("token")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if token is None or latitude is None or longitude is None:
        return jsonify({"status": "ERROR", "message": "token, latitude and longitude are required"}), 400

    result = process_checkin(token, float(latitude), float(longitude))
    return jsonify(result)


@attendance_bp.route("/success")
def success_page():
    return render_template("success.html")


@attendance_bp.route("/rejected")
def rejected_page():
    return render_template("rejected.html")
