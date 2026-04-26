import sqlite3

# Connect directly to the database
conn = sqlite3.connect('./fastapi.db')
cursor = conn.cursor()

# Check the wlasah user
cursor.execute("SELECT id, username, is_staff FROM users WHERE username = 'wlasah'")
result = cursor.fetchone()

if result:
    user_id, username, is_staff = result
    print(f"User ID: {user_id}")
    print(f"Username: {username}")
    print(f"is_staff: {is_staff} (1 = True/Admin, 0 = False/User)")
    
    if is_staff == 0:
        print("\n⚠️  User is NOT an admin! Updating now...")
        cursor.execute("UPDATE users SET is_staff = 1 WHERE username = 'wlasah'")
        conn.commit()
        print("✅ Updated to admin!")
    else:
        print("\n✅ User IS already an admin!")
else:
    print("❌ User 'wlasah' not found in database")

conn.close()
