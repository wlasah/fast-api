# 🌱 Smart Plant Watering System - FastAPI Backend

This FastAPI service is the independent IoT backend for the Smart Plant Watering System. It receives ESP32 telemetry, manages device configuration, exposes plant and telemetry APIs, and can proxy select requests to a Django backend.

## What this service does

- Stores IoT telemetry data from ESP32 devices
- Updates plant moisture values based on telemetry
- Provides device configuration and command endpoints
- Handles user authentication and token validation
- Exposes plant list, watering history, and analytics endpoints
- Supports local development and deployment to cloud hosts

## Requirements

- Python 3.11+ (recommended)
- `pip`
- `virtualenv` or built-in `venv`

## Local Setup

1. Open a terminal in the FastAPI project:
   ```powershell
   cd e:\Download\appdev\fast-api
   ```

2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```

3. Activate the environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and edit values:
   ```powershell
   copy .env.example .env
   ```

## Environment Configuration

Example `.env` values:

```env
DEBUG=True
HOST=0.0.0.0
PORT=8001
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.1.10:8001
DATABASE_URL=sqlite:///./fastapi.db
DJANGO_API_URL=http://localhost:8000/api
SECRET_KEY=your-secret-key-here
```

**If your web app, mobile device, or ESP32 runs on another machine, use the backend host machine's LAN IP address in the frontend/mobile configuration.**

For example, `REACT_APP_API_URL` or `EXPO_PUBLIC_API_URL` should be set to:

```env
http://<YOUR_BACKEND_IP>:8001
```

### Important settings

- `CORS_ORIGINS`: Add the frontend/mobile URLs that will access this API.
- `DJANGO_API_URL`: Optional proxy destination if Django handles some routes.
- `DATABASE_URL`: Defaults to SQLite `sqlite:///./fastapi.db`.
- `SECRET_KEY`: Used for JWT token generation.

## Run the server

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Then access:

- API: `http://localhost:8001`
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Key API Endpoints

### Health
- `GET /health`

### IoT telemetry and device management
- `POST /api/iot/telemetry/` — receive sensor telemetry
- `GET /api/iot/telemetry/` — list telemetry records
- `POST /api/iot/config/` — create/update device config
- `GET /api/iot/config/{device_id}/` — get device config
- `POST /api/iot/commands/` — create device command
- `GET /api/iot/commands/{device_id}/` — poll pending commands
- `POST /api/iot/commands/{command_id}/ack/` — acknowledge command execution

### Plant endpoints
- `GET /api/plants/` — list plants for current user
- `GET /api/plants/{plant_id}/` — get plant details
- `POST /api/plants/{plant_id}/water/` — record manual watering
- `GET /api/plants/needing_water/` — plants with low moisture
- `GET /api/plants/stats/` — plant statistics for user

### User authentication
- `POST /api/users/register/` — register user
- `POST /api/users/login/` — login and receive token
- `GET /api/users/me/` — current user profile
- `POST /api/users/logout/` — logout

## Authentication

Protect API calls with the `Authorization` header:

```http
Authorization: Token <your_token_here>
```

## Integration Notes

### Mobile app
- Set `EXPO_PUBLIC_API_URL` to this FastAPI host in `Smart-Plant-Watering-System-Mobile/.env`
- Use the backend machine's LAN IP if the mobile device is on a different device or physical network
- Restart Expo after changing `.env`

### Web app
- Set `REACT_APP_API_URL` to this backend host in the web app `.env` file
- Use the backend machine's LAN IP if the web app is running from another computer
- Restart the React development server after changing `.env`

### ESP32
- Send telemetry to `/api/iot/telemetry/`
- Ensure the ESP32 backend URL matches the machine running FastAPI

## Troubleshooting

### Backend address issues
- Use the host machine LAN IP instead of `localhost` when mobile or other device needs access.
- Example: `http://192.168.1.10:8001`

### Command does not execute
- Confirm `device_id` and `plant_id` are valid in the database
- Check `GET /api/iot/commands/{device_id}/` for pending commands

### Dependency problems

```powershell
git clean -fdx
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port in use

```powershell
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

## Project Structure

```
fast-api/
├── main.py            # FastAPI application and routes
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── Procfile           # Render deployment file
├── render.yaml        # Render config file
├── README.md          # This file
└── fastapi.db         # SQLite database file (local development)
```

## Deployment

### Local development
- Use `uvicorn main:app --reload --host 0.0.0.0 --port 8001`

### Render deployment
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Add environment variables in Render for `DJANGO_API_URL`, `DATABASE_URL`, `SECRET_KEY`, and `CORS_ORIGINS`.

## Support

For more details, consult FastAPI docs:
- https://fastapi.tiangolo.com/

For full system architecture and frontend integration, see the parent repository documentation.

