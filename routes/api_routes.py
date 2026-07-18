"""
JSON API for employee management, QR issuance, and attendance reporting —
the integration surface other Group 25 modules can call into.
"""
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from config import Config
from models.attendance import get_all_records_df
from models.employee import create_or_update_employee, get_employee, list_employees
from services.qr_service import generate_and_save_employee_qr

api_bp = Blueprint("api", __name__, url_prefix="/api")

QR_DIR = Path(__file__).resolve().parent.parent / "static" / "qr"


@api_bp.route("/employees", methods=["POST"])
def register_employee():
    data = request.get_json(force=True) or {}
    required = ["employee_id", "full_name"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    employee = create_or_update_employee(
        employee_id=data["employee_id"],
        full_name=data["full_name"],
        department=data.get("department"),
        phone=data.get("phone"),
        email=data.get("email"),
    )
    qr_path = generate_and_save_employee_qr(data["employee_id"], QR_DIR)
    return jsonify({"employee": employee, "qr_path": f"/static/qr/{data['employee_id']}.png"})


@api_bp.route("/employees", methods=["GET"])
def employees_list():
    return jsonify(list_employees())


@api_bp.route("/employees/<employee_id>/qr", methods=["GET"])
def employee_qr(employee_id):
    if get_employee(employee_id) is None:
        return jsonify({"error": "Employee not found"}), 404
    qr_path = QR_DIR / f"{employee_id}.png"
    if not qr_path.exists():
        generate_and_save_employee_qr(employee_id, QR_DIR)
    return send_file(qr_path, mimetype="image/png")


@api_bp.route("/attendance/report", methods=["GET"])
def attendance_report():
    date = request.args.get("date")
    df = get_all_records_df()
    if df.empty:
        return jsonify({"records": [], "summary": {}})

    if date:
        df = df[df["attendance_date"] == date]

    summary = df.groupby(["attendance_date", "status"]).size().unstack(fill_value=0).to_dict(orient="index")
    return jsonify({"records": df.to_dict(orient="records"), "summary": summary})
