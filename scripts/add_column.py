import sys, os
from sqlalchemy import text

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE reports ADD COLUMN chat_session_id INTEGER REFERENCES chat_sessions(id)'))
    conn.commit()
    print("Added chat_session_id column to reports table")
