"""
Controller Layer — Shift Routes
Handles /api/shifts endpoints
"""

from flask import Blueprint, request, jsonify
from app.database import get_connection
from app.services.shift_service import check_shift_conflict

shift_bp = Blueprint('shifts', __name__)

@shift_bp.route('/', methods=['GET'])
def get_shifts():
    """FR-ST04, FR-UC05: Get all shifts, optionally filtered by personnel"""
    personnel_id = request.args.get('personnel_id')
    conn = get_connection()
    try:
        if personnel_id:
            rows = conn.execute(
                "SELECT * FROM shifts WHERE personnel_id = ? ORDER BY start_time DESC", (personnel_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM shifts ORDER BY start_time DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()

@shift_bp.route('/<int:sid>', methods=['GET'])
def get_shift(sid):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM shifts WHERE id = ?", (sid,)).fetchone()
        if not row:
            return jsonify({"error": "Shift not found"}), 404
        return jsonify(dict(row)), 200
    finally:
        conn.close()

@shift_bp.route('/', methods=['POST'])
def create_shift():
    """FR-ST04: Create a new shift (with conflict detection)"""
    data = request.get_json()
    required = ['personnel_id', 'start_time', 'end_time']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    if data['end_time'] <= data['start_time']:
        return jsonify({"error": "End time must be after start time"}), 400

    conn = get_connection()
    try:
        person = conn.execute("SELECT id FROM personnel WHERE id = ?", (data['personnel_id'],)).fetchone()
        if not person:
            return jsonify({"error": "Personnel not found"}), 404

        # Business logic: conflict check (Service Layer)
        if check_shift_conflict(conn, data['personnel_id'], data['start_time'], data['end_time']):
            return jsonify({"error": "Shift conflict detected for this personnel", "conflict": True}), 409

        conn.execute(
            "INSERT INTO shifts (personnel_id, start_time, end_time, notes) VALUES (?, ?, ?, ?)",
            (data['personnel_id'], data['start_time'], data['end_time'], data.get('notes'))
        )
        conn.commit()
        shift = conn.execute("SELECT * FROM shifts WHERE rowid = last_insert_rowid()").fetchone()
        return jsonify(dict(shift)), 201
    finally:
        conn.close()

@shift_bp.route('/<int:sid>', methods=['PUT'])
def update_shift(sid):
    """Update shift details"""
    data = request.get_json()
    conn = get_connection()
    try:
        shift = conn.execute("SELECT * FROM shifts WHERE id = ?", (sid,)).fetchone()
        if not shift:
            return jsonify({"error": "Shift not found"}), 404

        fields = {k: v for k, v in data.items() if k in ['start_time', 'end_time', 'status', 'notes']}
        if not fields:
            return jsonify({"error": "No valid fields to update"}), 400

        set_clause = ', '.join(f"{k} = ?" for k in fields)
        conn.execute(f"UPDATE shifts SET {set_clause} WHERE id = ?", list(fields.values()) + [sid])
        conn.commit()
        updated = conn.execute("SELECT * FROM shifts WHERE id = ?", (sid,)).fetchone()
        return jsonify(dict(updated)), 200
    finally:
        conn.close()

@shift_bp.route('/<int:sid>', methods=['DELETE'])
def cancel_shift(sid):
    """Cancel a shift"""
    conn = get_connection()
    try:
        shift = conn.execute("SELECT * FROM shifts WHERE id = ?", (sid,)).fetchone()
        if not shift:
            return jsonify({"error": "Shift not found"}), 404

        conn.execute("UPDATE shifts SET status = 'cancelled' WHERE id = ?", (sid,))
        conn.commit()
        return jsonify({"message": "Shift cancelled successfully"}), 200
    finally:
        conn.close()
