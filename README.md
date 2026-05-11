# Smart Plant Watering System - FastAPI Backend

FastAPI backend running alongside Django backend to provide additional analytics and features.

## Features

- **Relay Endpoints**: Proxy requests to Django backend for compatibility
- **Plant Analytics**: Advanced trend analysis and health tracking
- **Watering Schedule**: Intelligent recommendations for watering plants
- **User Summary**: Aggregated user statistics
- **Token Verification**: Token validation with Django backend
- **CORS Support**: Works with web (Vercel) and mobile apps

## Local Development

### Setup Virtual Environment

```bash
cd fastapi-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
DEBUG=True
DJANGO_API_URL=http://localhost:8000/api
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Run Development Server

```bash
uvicorn main:app --reload --port 8001
```

The server will start at `http://localhost:8001`

### Access API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## API Endpoints

### Health & Status
- `GET /` - Welcome message
- `GET /health` - Health check

### Plants (Relay to Django)
- `GET /api/plants` - List all plants
- `GET /api/plants/{plant_id}` - Get plant details
- `POST /api/plants/{plant_id}/water` - Water a plant

### FastAPI-Specific Analytics
- `GET /api/analytics/plant-trends` - Plant health trends
- `GET /api/analytics/watering-schedule` - Watering recommendations
- `GET /api/users/summary` - User statistics summary
- `POST /api/auth/verify-token` - Verify token validity

## Authentication

All API endpoints require `Authorization` header:

```
Authorization: Token your-auth-token
```

## Deployment on Render

### Option 1: Using GitHub Integration

1. Push this code to GitHub
2. Go to https://dashboard.render.com
3. Click "New +" → "Web Service"
4. Connect GitHub and select repository
5. Fill in configuration:
   - **Name**: `smart-plant-fastapi`
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

6. Add Environment Variables:
   ```
   DEBUG = false
   PORT = 8001
   CORS_ORIGINS = https://smart-plant-watering-system.vercel.app
   DATABASE_URL = postgresql://user:password@host:5432/dbname
   DJANGO_API_URL = https://smart-plant-backend-39w7.onrender.com/api
   SECRET_KEY = your-secret-key-here
   ```

   - `DATABASE_URL` should point to the same Render PostgreSQL database used by the Django backend.
   - If your original Render PostgreSQL instance expired, create a new PostgreSQL database service and paste its connection URL here.
   - `DJANGO_API_URL` enables FastAPI to proxy `/api/*` requests to the Django backend so the deployed service uses the same auth/data store.

7. Click "Deploy"

### Option 2: Using Render CLI

```bash
# Install Render CLI
npm i -g @render-com/cli

# Authenticate
render login

# Deploy
render deploy
```

## Integration with Frontend

### React Web App

Update `src/services/api.js` to include FastAPI endpoints:

```javascript
const fastapi = {
  getTrends: () => fetchWithToken('https://your-fastapi-url/api/analytics/plant-trends'),
  getSchedule: () => fetchWithToken('https://your-fastapi-url/api/analytics/watering-schedule'),
  getUsersSummary: () => fetchWithToken('https://your-fastapi-url/api/users/summary'),
};
```

### React Native Mobile App

Similarly update the mobile API service to include FastAPI endpoints.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` (development) / `false` (production) |
| `PORT` | Server port | `8001` |
| `HOST` | Server host | `0.0.0.0` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `https://app.vercel.app,http://localhost:3000` |
| `DJANGO_API_URL` | Django backend URL | `https://django-api.onrender.com/api` |
| `SECRET_KEY` | JWT secret key | Generate a random string |

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8001 (Windows)
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Kill process on port 8001 (macOS/Linux)
lsof -ti:8001 | xargs kill -9
```

### Import Errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### CORS Errors

Check that `CORS_ORIGINS` environment variable includes your frontend URL.

## Project Structure

```
fastapi-backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── Procfile               # Render deployment config
├── render.yaml            # Alternative Render config
└── README.md              # This file
```

## Support

For issues or questions, refer to:
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Render Dashboard](https://dashboard.render.com)
- Django Backend: https://github.com/wlasah/Smart-Plant-Watering-System
