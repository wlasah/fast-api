#!/usr/bin/env python
"""
Quick script to set wlasah as admin
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import SessionLocal, User, get_password_hash
from passlib.context import CryptContext  # if needed

db = SessionLocal()

try:
    # Find user
    user = db.query(User).filter(User.username == 'wlasah').first()
    if not user:
        print('❌ User wlasah not found!')
    else:
        print(f'Found user: {user.username}, was staff: {user.is_staff}')
        
        # Update
        user.is_staff = True
        # Ensure correct password
        user.password_hash = get_password_hash('password')
        db.commit()
        print('✅ Updated wlasah: is_staff=True, password=\\'password\\'')

    # Show all users
    print('\n📋 All users:')
    for u in db.query(User).all():
        role = '👑 Admin' if u.is_staff else '👤 User'
        print(f'  {role} | {u.username} (staff: {u.is_staff})')

except Exception as e:
    print(f'❌ Error: {e}')
finally:
    db.close()

