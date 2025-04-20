import json
from datetime import datetime
from flask import g
from libsys.db import get_db

def log_action(user_id, action, entity_type, entity_id, details=None):
    """Record system operations to log table"""
    db = get_db()
    c = db.cursor()
    
    # Convert details to JSON if provided
    details_json = json.dumps(details) if details else None
    
    # Insert log record
    c.execute(
        "INSERT INTO SYSTEM_LOGS (user_id, action, entity_type, entity_id, details, timestamp) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, action, entity_type, entity_id, details_json, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    db.commit()
    
    return True