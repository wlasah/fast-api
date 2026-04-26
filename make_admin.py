#!/usr/bin/env python
"""
Script to make an existing user an admin in FastAPI
Usage: python make_admin.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models
from main import User, Base

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fastapi.db")
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def make_admin(username: str):
    """Make a user an admin"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return False
        
        if user.is_staff:
            print(f"⚠️  User '{username}' is already an admin!")
            return True
        
        user.is_staff = True
        db.commit()
        print(f"✅ User '{username}' is now an admin!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   is_staff: {user.is_staff}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    username = input("Enter username to make admin (default: wlasah): ").strip() or "wlasah"
    make_admin(username)
