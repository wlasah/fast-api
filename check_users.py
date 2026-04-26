import sqlite3

conn = sqlite3.connect('fastapi.db')
cursor = conn.cursor()

# Get all users
cursor.execute('SELECT id, username, email, is_staff FROM users')
users = cursor.fetchall()

print('All users in database:')
if users:
    for user_id, username, email, is_staff in users:
        status = 'ADMIN' if is_staff else 'USER'
        print(f'  ID: {user_id}, Username: {username}, Email: {email} - {status}')
else:
    print('  No users found')

conn.close()
