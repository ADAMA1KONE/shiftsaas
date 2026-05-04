"""
Data Layer — SQLite database management
Implements the persistence tier of the 3-tier architecture
"""

import sqlite3
import os

DB_PATH = os.environ.get('DATABASE_PATH', 'shiftsaas.db')

def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Personnel table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee',
            department TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Shifts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    ''')

    # Check-in/out table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            shift_id INTEGER,
            checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checkout_time TIMESTAMP,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'checked_in',
            FOREIGN KEY (personnel_id) REFERENCES personnel(id),
            FOREIGN KEY (shift_id) REFERENCES shifts(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")
