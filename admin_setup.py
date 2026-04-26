#!/usr/bin/env python
"""
Admin Setup Script for FastAPI Backend
Use this to create admin users and sample data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import SessionLocal, User, Plant, WateringHistory, get_password_hash
from datetime import datetime

db = SessionLocal()

def create_admin_user(username: str = "admin", email: str = "admin@example.com", password: str = "admin123"):
    """Create an admin user"""
    # Check if admin already exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"❌ Admin user '{username}' already exists!")
        return None

    admin = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_staff=True,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"✅ Admin user created: {username} / {password}")
    return admin


def create_test_user(username: str = "testuser", email: str = "test@example.com", password: str = "test123"):
    """Create a regular test user"""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"⚠️  User '{username}' already exists!")
        return existing

    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_staff=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ Test user created: {username} / {password}")
    return user


def create_sample_plants(user_id: int):
    """Create sample plants for a user"""
    sample_plants = [
        {"name": "Monstera", "type": "Indoor Plant", "location": "Living Room", "moisture": 45.0},
        {"name": "Snake Plant", "type": "Succulent", "location": "Bedroom", "moisture": 30.0},
        {"name": "Pothos", "type": "Vine Plant", "location": "Office", "moisture": 55.0},
        {"name": "Peace Lily", "type": "Flowering", "location": "Bathroom", "moisture": 65.0},
        {"name": "Cactus", "type": "Succulent", "location": "Desk", "moisture": 20.0},
    ]

    for plant_data in sample_plants:
        existing = db.query(Plant).filter(
            Plant.name == plant_data["name"],
            Plant.owner_id == user_id
        ).first()

        if existing:
            print(f"  ⚠️  Plant '{plant_data['name']}' already exists")
            continue

        plant = Plant(
            name=plant_data["name"],
            type=plant_data["type"],
            location=plant_data["location"],
            moisture=plant_data["moisture"],
            owner_id=user_id
        )
        db.add(plant)
        print(f"  ✅ Created plant: {plant_data['name']}")

    db.commit()


def create_sample_history(plant_id: int, count: int = 3):
    """Create sample watering history for a plant"""
    from datetime import timedelta

    for i in range(count):
        history = WateringHistory(
            plant_id=plant_id,
            watered_at=datetime.utcnow() - timedelta(days=i),
            notes=f"Regular watering #{i+1}"
        )
        db.add(history)

    db.commit()
    print(f"  ✅ Added {count} watering history records")


def show_all_users():
    """Display all users in database"""
    users = db.query(User).all()
    print(f"\n📋 Total Users: {len(users)}")
    for user in users:
        role = "👑 Admin" if user.is_staff else "👤 User"
        print(f"  {role} | {user.id}: {user.username} ({user.email}) - Active: {user.is_active}")


def show_all_plants(user_id: int = None):
    """Display all plants"""
    if user_id:
        plants = db.query(Plant).filter(Plant.owner_id == user_id).all()
        print(f"\n🌱 Plants for user {user_id}: {len(plants)}")
    else:
        plants = db.query(Plant).all()
        print(f"\n🌱 Total Plants: {len(plants)}")

    for plant in plants:
        print(f"  [{plant.id}] {plant.name} ({plant.type}) - {plant.location} - 💧 {plant.moisture}%")


def show_database_stats():
    """Show database statistics"""
    total_users = db.query(User).count()
    total_plants = db.query(Plant).count()
    total_waterings = db.query(WateringHistory).count()
    admins = db.query(User).filter(User.is_staff == True).count()

    print("\n📊 Database Statistics:")
    print(f"  👤 Total Users: {total_users} (👑 Admins: {admins})")
    print(f"  🌱 Total Plants: {total_plants}")
    print(f"  💧 Total Waterings: {total_waterings}")


def main():
    print("\n" + "="*50)
    print("FastAPI Admin Setup Tool")
    print("="*50)

    while True:
        print("\nOptions:")
        print("  1. Create Admin User")
        print("  2. Create Test User")
        print("  3. Add Sample Plants")
        print("  4. Add Watering History")
        print("  5. View All Users")
        print("  6. View All Plants")
        print("  7. Database Stats")
        print("  8. Exit")

        choice = input("\nEnter choice (1-8): ").strip()

        if choice == "1":
            username = input("Admin username (default: admin): ") or "admin"
            email = input("Admin email (default: admin@example.com): ") or "admin@example.com"
            password = input("Admin password (default: admin123): ") or "admin123"
            create_admin_user(username, email, password)

        elif choice == "2":
            username = input("Username: ").strip()
            if not username:
                print("❌ Username required!")
                continue
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            create_test_user(username, email, password)

        elif choice == "3":
            user_id = input("User ID: ").strip()
            try:
                user_id = int(user_id)
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    print(f"❌ User {user_id} not found!")
                    continue
                print(f"Creating sample plants for {user.username}...")
                create_sample_plants(user_id)
            except ValueError:
                print("❌ Invalid user ID!")

        elif choice == "4":
            plant_id = input("Plant ID: ").strip()
            try:
                plant_id = int(plant_id)
                plant = db.query(Plant).filter(Plant.id == plant_id).first()
                if not plant:
                    print(f"❌ Plant {plant_id} not found!")
                    continue
                create_sample_history(plant_id)
            except ValueError:
                print("❌ Invalid plant ID!")

        elif choice == "5":
            show_all_users()

        elif choice == "6":
            show_all_plants()

        elif choice == "7":
            show_database_stats()

        elif choice == "8":
            print("\n✅ Goodbye!")
            break

        else:
            print("❌ Invalid choice!")

    db.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        db.close()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.close()
