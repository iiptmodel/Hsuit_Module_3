import sys, os
from sqlalchemy import inspect

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine

inspector = inspect(engine)
tables = ['reports', 'chat_sessions', 'chat_messages']
for table in tables:
    cols = inspector.get_columns(table)
    print(f'{table} columns:')
    for c in cols:
        print('-', c['name'], c.get('type'))
    print()
