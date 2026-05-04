"""
Controller Layer — Authentication Routes
Handles /api/auth endpoints
"""

from flask import Blueprint, request, jsonify
from app.database import get_connection
from app.services.auth_service import hash_password, verify_password, create_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """FR-ST01: Register new personnel"""
    data = request.get_json()
    required = ['first_name', 'last_name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM personnel WHERE email = ?", (data['email'],)
        ).fetchone()
        if existing:
            return jsonify({"error": "Email already registered"}), 409

        conn.execute(
            '''INSERT INTO personnel (first_name, last_name, email, hashed_password, role, department)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (data['first_name'], data['last_name'], data['email'],
             hash_password(data['password']),
             data.get('role', 'employee'),
             data.get('department'))
        )
        conn.commit()
        person = conn.execute(
            "SELECT id, first_name, last_name, email, role, department, is_active, created_at FROM personnel WHERE email = ?", (data['email'],)
        ).fetchone()
        return jsonify(dict(person)), 201
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    """FR-ST09: Login with email and password"""
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM personnel WHERE email = ? AND is_active = 1", (data['email'],)
        ).fetchone()
        if not user or not verify_password(data['password'], user['hashed_password']):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_token({
            "id": user['id'],
            "email": user['email'],
            "role": user['role']
        })
        return jsonify({
            "access_token": token,
            "token_type": "bearer",
            "role": user['role'],
            "name": f"{user['first_name']} {user['last_name']}"
        }), 200
    finally:
        conn.close()
