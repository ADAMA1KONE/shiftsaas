"""
Controller Layer — Personnel Routes
Handles /api/personnel endpoints (CRUD)
"""

from flask import Blueprint, request, jsonify
from app.database import get_connection
from app.services.auth_service import hash_password

personnel_bp = Blueprint('personnel', __name__)

@personnel_bp.route('/', methods=['GET'])
def get_all():
    """FR-ST01: Get all active personnel"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, first_name, last_name, email, role, department, is_active, created_at FROM personnel WHERE is_active = 1"
        ).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()

@personnel_bp.route('/<int:pid>', methods=['GET'])
def get_one(pid):
    """Get single personnel by ID"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, first_name, last_name, email, role, department, is_active, created_at FROM personnel WHERE id = ?", (pid,)
        ).fetchone()
        if not row:
            return jsonify({"error": "Personnel not found"}), 404
        return jsonify(dict(row)), 200
    finally:
        conn.close()

@personnel_bp.route('/', methods=['POST'])
def create():
    """FR-ST01: Create new personnel"""
    data = request.get_json()
    required = ['first_name', 'last_name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM personnel WHERE email = ?", (data['email'],)).fetchone()
        if existing:
            return jsonify({"error": "Email already exists"}), 409

        conn.execute(
            '''INSERT INTO personnel (first_name, last_name, email, hashed_password, role, department)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (data['first_name'], data['last_name'], data['email'],
             hash_password(data['password']),
             data.get('role', 'employee'),
             data.get('department'))
        )
        conn.commit()
        person = conn.execute("SELECT id, first_name, last_name, email, role, department FROM personnel WHERE email = ?", (data['email'],)).fetchone()
        return jsonify(dict(person)), 201
    finally:
        conn.close()

@personnel_bp.route('/<int:pid>', methods=['PUT'])
def update(pid):
    """FR-ST02: Update personnel"""
    data = request.get_json()
    conn = get_connection()
    try:
        person = conn.execute("SELECT * FROM personnel WHERE id = ?", (pid,)).fetchone()
        if not person:
            return jsonify({"error": "Personnel not found"}), 404

        fields = {k: v for k, v in data.items() if k in ['first_name', 'last_name', 'role', 'department', 'is_active']}
        if not fields:
            return jsonify({"error": "No valid fields to update"}), 400

        set_clause = ', '.join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [pid]
        conn.execute(f"UPDATE personnel SET {set_clause} WHERE id = ?", values)
        conn.commit()
        updated = conn.execute("SELECT id, first_name, last_name, email, role, department, is_active FROM personnel WHERE id = ?", (pid,)).fetchone()
        return jsonify(dict(updated)), 200
    finally:
        conn.close()

@personnel_bp.route('/<int:pid>', methods=['DELETE'])
def delete(pid):
    """FR-ST02: Deactivate personnel (soft delete)"""
    conn = get_connection()
    try:
        person = conn.execute("SELECT * FROM personnel WHERE id = ?", (pid,)).fetchone()
        if not person:
            return jsonify({"error": "Personnel not found"}), 404

        conn.execute("UPDATE personnel SET is_active = 0 WHERE id = ?", (pid,))
        conn.commit()
        return jsonify({"message": "Personnel deactivated successfully"}), 200
    finally:
        conn.close()
