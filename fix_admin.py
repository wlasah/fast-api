#!/usr/bin/env python
"""
Check all users and ensure the admin is properly marked
"""
import sqlite3

conn = sqlite3.connect('fastapi.db')
cursor = conn.cursor()

print("=" * 50)
print("USERS IN DATABASE")
print("=" * 50)

# Get all users
cursor.execute('SELECT id, username, email, is_staff FROM users ORDER BY id')
users = cursor.fetchall()

if not users:
    print("❌ No users found in database!")
else:
    for user_id, username, email, is_staff in users:
        status = '✅ ADMIN (is_staff=1)' if is_staff == 1 else '❌ USER (is_staff=0)'
        print(f"ID {user_id}: {username:20} | Email: {email:30} | {status}")

print("\n" + "=" * 50)
print("FIXING: Setting first non-admin user to admin...")
print("=" * 50)

# Find first user that is not admin
cursor.execute('SELECT id, username FROM users WHERE is_staff = 0 LIMIT 1')
user_to_fix = cursor.fetchone()

if user_to_fix:
    user_id, username = user_to_fix
    cursor.execute('UPDATE users SET is_staff = 1 WHERE id = ?', (user_id,))
    conn.commit()
    print(f"✅ Updated {username} (ID {user_id}) to ADMIN")
else:
    print("✅ All users are already admins!")

print("\n" + "=" * 50)
print("FINAL STATUS")
print("=" * 50)

cursor.execute('SELECT id, username, email, is_staff FROM users ORDER BY id')
users = cursor.fetchall()

for user_id, username, email, is_staff in users:
    status = '✅ ADMIN' if is_staff == 1 else '❌ USER'
    print(f"ID {user_id}: {username:20} | {status}")

conn.close()
print("\nDone!")
