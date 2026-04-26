# FastAPI Backend - Complete Guide

## ✅ What's New

FastAPI is now **completely independent** with:
- ✅ SQLite database (SQLAlchemy ORM)
- ✅ All endpoints implemented
- ✅ User authentication with JWT tokens
- ✅ Plants management
- ✅ Watering history tracking
- ✅ Admin functionality

**Database File**: `fastapi.db` (SQLite, ~52KB)

---

## 🚀 Starting FastAPI Locally

### Option 1: With Auto-Reload (Development)
```bash
cd "e:\Smart Plant Watering System\fastapi-backend"
"e:\Smart Plant Watering System\.venv\Scripts\python" -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Option 2: Direct Python Run
```bash
cd "e:\Smart Plant Watering System\fastapi-backend"
"e:\Smart Plant Watering System\.venv\Scripts\python" main.py
```

### Option 3: Using Batch File
```bash
cd "e:\Smart Plant Watering System\fastapi-backend"
.\run-fastapi.bat
```

FastAPI will be available at: **http://localhost:8001**

---

## 📚 API Documentation

Once FastAPI is running, visit:
- **Interactive Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

---

## 🔄 Switching Between Backends

### Web App (React)
Edit `.env.local`:
```
# Use FastAPI:
REACT_APP_API_URL=http://localhost:8001/api

# Use Django Local:
# REACT_APP_API_URL=http://localhost:8000/api

# Use Django Render:
# REACT_APP_API_URL=https://smart-plant-backend-39w7.onrender.com/api
```

Then refresh browser.

### Mobile App (React Native)
Edit `.env`:
```
# Use FastAPI:
REACT_APP_API_URL=http://192.168.1.10:8001
EXPO_PUBLIC_API_URL=http://192.168.1.10:8001

# Use Django Local:
# REACT_APP_API_URL=http://192.168.1.10:8000
# EXPO_PUBLIC_API_URL=http://192.168.1.10:8000
```

Then rebuild app.

---

## 💾 Database

### View Tables (SQLite)

**Option 1: Using DB Browser for SQLite (Free)**
1. Download: https://sqlitebrowser.org/
2. Open file: `fastapi.db`
3. Browse tables

**Option 2: Using Python Shell**
```bash
cd "e:\Smart Plant Watering System\fastapi-backend"
"e:\Smart Plant Watering System\.venv\Scripts\python" -c "
from sqlalchemy import inspect, create_engine
engine = create_engine('sqlite:///./fastapi.db')
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

### Database Tables

1. **users** - User accounts
   - id, username, email, password_hash, is_staff, is_active, created_at

2. **plants** - Plant data
   - id, name, type, location, moisture, owner_id, created_at

3. **watering_history** - Watering records
   - id, plant_id, watered_at, notes

4. **tokens** - Authentication tokens
   - id, user_id, token, created_at

---

## 🔐 Authentication

All protected endpoints require the `Authorization` header:

```
Authorization: Token <your-jwt-token>
```

### Getting a Token

**Register**:
```bash
curl -X POST "http://localhost:8001/api/users/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

**Login**:
```bash
curl -X POST "http://localhost:8001/api/users/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Response includes `token` - use this for subsequent requests.

---

## 🚀 Deploying to Render (Production)

### Step 1: Update Environment Variables

In your Render dashboard, set:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
CORS_ORIGINS=https://yourdomain.com,https://mobile.com
```

### Step 2: Update .env.production in FastAPI

Edit `fastapi-backend/.env.production`:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
DEBUG=False
```

### Step 3: Deploy

The `render.yaml` and `Procfile` are already configured for:
- `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Automatic pip install from requirements.txt

Just push to GitHub and Render will auto-deploy!

### Step 4: Keep Render Warm
Render free tier can hibernate after inactivity, which may cause the first request to return `429 Too Many Requests` while it wakes up.

A GitHub Actions workflow is included at `.github/workflows/keep-fastapi-warm.yml` to ping `https://fast-api-g456.onrender.com/health` every 15 minutes and keep the service responsive during your demo.

---

## ✅ Checklist: Local Testing

- [ ] FastAPI running on http://localhost:8001
- [ ] `/health` endpoint returns "healthy"
- [ ] Can register new user
- [ ] Can login with user
- [ ] Can create plant
- [ ] Can water plant
- [ ] Can view watering history
- [ ] Web app connected to FastAPI
- [ ] Mobile app connected to FastAPI

---

## 🐛 Troubleshooting

### Port 8001 Already in Use
```bash
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Database Errors
```bash
# Delete corrupted database and restart (it will recreate)
del fastapi.db
```

### Import Errors
```bash
# Reinstall dependencies
"e:\Smart Plant Watering System\.venv\Scripts\python" -m pip install -r requirements.txt
```

### Can't connect from mobile
- Make sure phone is on **same WiFi**
- Use IP (192.168.1.10) not localhost
- Firewall might be blocking port 8001

---

## 📊 API Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/users/register/` | No | Register user |
| POST | `/api/users/login/` | No | Login user |
| GET | `/api/users/me/` | Yes | Get current user |
| POST | `/api/users/logout/` | Yes | Logout |
| GET | `/api/plants/` | Yes | Get user's plants |
| POST | `/api/plants/` | Yes | Create plant |
| PUT | `/api/plants/{id}/` | Yes | Update plant |
| DELETE | `/api/plants/{id}/` | Yes | Delete plant |
| POST | `/api/plants/{id}/water/` | Yes | Water plant |
| GET | `/api/watering_history/` | Yes | Get watering history |
| GET | `/api/plants/stats/` | Yes | Get user stats |

---

**Version**: 1.0.0 (Independent)  
**Database**: SQLite (local) / PostgreSQL (production)
