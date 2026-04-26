#!/usr/bin/env python
"""Make wlasah an admin"""
import sqlite3

conn = sqlite3.connect('fastapi.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET is_staff = 1 WHERE username = 'wlasah'")
conn.commit()
print('✅ wlasah is now an admin!')
conn.close()
