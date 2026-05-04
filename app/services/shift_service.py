"""
Service Layer — Shift Business Logic
Handles conflict detection, GPS validation, and shift management rules
"""

import math

WORKPLACE_LAT = 41.0082  # Istanbul coordinates (example)
WORKPLACE_LON = 28.9784
MAX_DISTANCE_METERS = 500

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two GPS coordinates."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def is_within_workplace(lat: float, lon: float) -> tuple:
    """
    Check if GPS coordinates are within workplace radius.
    Returns (is_valid, distance_meters)
    """
    distance = haversine_distance(lat, lon, WORKPLACE_LAT, WORKPLACE_LON)
    return distance <= MAX_DISTANCE_METERS, round(distance, 1)

def check_shift_conflict(conn, personnel_id: int, start_time: str, end_time: str, exclude_id: int = None) -> bool:
    """
    Check if a new shift overlaps with existing shifts for a personnel.
    Returns True if there is a conflict.
    """
    query = '''
        SELECT id FROM shifts
        WHERE personnel_id = ?
        AND status = 'active'
        AND start_time < ?
        AND end_time > ?
    '''
    params = [personnel_id, end_time, start_time]
    
    if exclude_id:
        query += ' AND id != ?'
        params.append(exclude_id)
    
    cursor = conn.execute(query, params)
    return cursor.fetchone() is not None

def calculate_hours_worked(checkin_time: str, checkout_time: str) -> float:
    """Calculate total hours worked between check-in and check-out."""
    from datetime import datetime
    fmt = "%Y-%m-%d %H:%M:%S"
    try:
        t1 = datetime.strptime(checkin_time[:19], fmt)
        t2 = datetime.strptime(checkout_time[:19], fmt)
        delta = t2 - t1
        return round(delta.total_seconds() / 3600, 2)
    except Exception:
        return 0.0
