"""
Controller Layer — Check-in/out Routes
Handles /api/checkin endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.database import get_connection
from app.services.shift_service import is_within_workplace

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/checkin', methods=['POST'])
def check_in():
    """FR-UC07: Register personnel check-in with GPS validation"""
    data = request.get_json()
    if not data.get('personnel_id'):
        return jsonify({"error": "personnel_id is required"}), 400

    conn = get_connection()
    try:
        person = conn.execute("SELECT * FROM personnel WHERE id = ? AND is_active = 1", (data['personnel_id'],)).fetchone()
        if not person:
            return jsonify({"error": "Personnel not found"}), 404

        # GPS validation (Service Layer business logic)
        gps_valid = True
        distance = None
        if data.get('latitude') and data.get('longitude'):
            gps_valid, distance = is_within_workplace(data['latitude'], data['longitude'])
            if not gps_valid:
                return jsonify({
                    "error": f"Too far from workplace. Distance: {distance}m (max: 500m)",
                    "distance_meters": distance
                }), 400

        # Check already checked in
        existing = conn.execute(
            "SELECT id FROM checkins WHERE personnel_id = ? AND status = 'checked_in'",
            (data['personnel_id'],)
        ).fetchone()
        if existing:
            return jsonify({"error": "Already checked in"}), 409

        conn.execute(
            "INSERT INTO checkins (personnel_id, shift_id, latitude, longitude, status) VALUES (?, ?, ?, ?, 'checked_in')",
            (data['personnel_id'], data.get('shift_id'), data.get('latitude'), data.get('longitude'))
        )
        conn.commit()
        record = conn.execute("SELECT * FROM checkins WHERE rowid = last_insert_rowid()").fetchone()
        return jsonify(dict(record)), 201
    finally:
        conn.close()

@checkin_bp.route('/checkout', methods=['PUT'])
def check_out():
    """FR-UC07: Register personnel check-out"""
    data = request.get_json()
    if not data.get('checkin_id'):
        return jsonify({"error": "checkin_id is required"}), 400

    conn = get_connection()
    try:
        record = conn.execute("SELECT * FROM checkins WHERE id = ?", (data['checkin_id'],)).fetchone()
        if not record:
            return jsonify({"error": "Check-in record not found"}), 404
        if record['status'] == 'checked_out':
            return jsonify({"error": "Already checked out"}), 400

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE checkins SET checkout_time = ?, status = 'checked_out' WHERE id = ?",
            (now, data['checkin_id'])
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM checkins WHERE id = ?", (data['checkin_id'],)).fetchone()
        return jsonify(dict(updated)), 200
    finally:
        conn.close()

@checkin_bp.route('/history/<int:pid>', methods=['GET'])
def get_history(pid):
    """Get check-in/out history for a personnel"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM checkins WHERE personnel_id = ? ORDER BY checkin_time DESC", (pid,)
        ).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()
