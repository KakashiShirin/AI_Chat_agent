#!/usr/bin/env python3
"""
Check database tables
"""

from app.models.database import engine
from sqlalchemy import text

def check_tables():
    """Check what tables exist in the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'data_%'
            """))
            tables = [row[0] for row in result]
            print(f"Found {len(tables)} data tables:")
            for table in tables:
                print(f"  - {table}")
            
            # Check specific session
            session_id = "7071b5f3-fe2b-4283-9357-26102112acb6"
            session_tables = [t for t in tables if session_id in t]
            print(f"\nTables for session {session_id}: {session_tables}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()
