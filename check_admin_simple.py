#!/usr/bin/env python
"""Check admin status"""
import sqlite3

conn = sqlite3.connect('fastapi.db')
cursor = conn.cursor()
cursor.execute("SELECT id, username, is_staff FROM users WHERE username = 'wlasah'")
result = cursor.fetchone()

if result:
    user_id, username, is_staff = result
    status = "✅ ADMIN" if is_staff else "❌ NOT ADMIN"
    print(f"User: {username} (ID: {user_id}) - {status}")
else:
    print("❌ User 'wlasah' not found in database")

conn.close()
