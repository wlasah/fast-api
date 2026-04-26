import sqlite3
from pathlib import Path

path = Path('fastapi.db')
print('db exists:', path.exists())
if not path.exists():
    raise SystemExit(1)
conn = sqlite3.connect('fastapi.db')
cursor = conn.cursor()
print('tables:')
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(' ', row[0])
print('columns users:')
for row in cursor.execute("PRAGMA table_info(users)"):
    print(' ', row)
print('user rows:')
for row in cursor.execute("SELECT id, username, email, is_staff, is_active FROM users"):
    print(' ', row)
conn.close()
