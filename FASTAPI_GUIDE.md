# FastAPI Backend - Complete Guide

## ✅ What's New

FastAPI is now the independent IoT backend for the Smart Plant Watering System. It handles telemetry, user authentication, plant management, watering history, and integration with the mobile and web apps.

## Starting FastAPI Locally

```bash
cd "e:\Download\appdev\fast-api"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Once FastAPI is running, verify:
- `http://localhost:8001`
- `http://localhost:8001/docs`
- `http://localhost:8001/redoc`

## Backend URL Configuration for Cloned Projects

If you clone the project and run the backend on your own machine, use the backend host's LAN IP in the frontend and mobile apps.

### Web app
In `Smart-Plant-Watering-System/.env.development` or `.env.local`:

```env
REACT_APP_API_URL=http://<YOUR_BACKEND_IP>:8001
```

### Mobile app
In `Smart-Plant-Watering-System-Mobile/.env`:

```env
EXPO_PUBLIC_API_URL=http://<YOUR_BACKEND_IP>:8001
```

### Notes
- Use `http://localhost:8001` only when the app and backend run on the same machine.
- For Android emulators, if `localhost` does not work, try `http://10.0.2.2:8001`.
- For physical devices, use the host machine's local IP.

## API Documentation

Use the built-in FastAPI docs:
- `http://localhost:8001/docs`
- `http://localhost:8001/redoc`

## Switching Between Backends

Update the frontend/mobile environment variables to point to the desired backend.

### FastAPI example
```env
REACT_APP_API_URL=http://192.168.1.10:8001
EXPO_PUBLIC_API_URL=http://192.168.1.10:8001
```

### Django example
```env
REACT_APP_API_URL=http://192.168.1.10:8000/api
EXPO_PUBLIC_API_URL=http://192.168.1.10:8000/api
```

## Database

- Default: SQLite: `sqlite:///./fastapi.db`
- If you want a clean slate, stop the server, delete `fastapi.db`, then restart.
- Use DB Browser for SQLite to inspect tables.

## Authentication

Protected endpoints require:

```http
Authorization: Token <your_token_here>
```

## Integration Notes

- Web app: set `REACT_APP_API_URL` to this backend host
- Mobile app: set `EXPO_PUBLIC_API_URL` to this backend host
- ESP32: send telemetry to `http://<YOUR_BACKEND_IP>:8001/api/iot/telemetry/`

## Troubleshooting

### Backend not reachable
- Confirm `uvicorn` is running on `0.0.0.0:8001`
- Make sure firewall allows port `8001`
- Use host LAN IP for other devices

### CORS issues
- Add front-end origins to `CORS_ORIGINS`
- Example:
  `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.1.10:3000`

### Mobile app fails to connect
- Set `EXPO_PUBLIC_API_URL` to the backend LAN IP
- Restart Expo after `.env` changes
- Use tunnel mode if network configuration blocks direct access

## Recommended Clone Workflow

1. Clone repository.
2. Create `fast-api/.env` from `.env.example`.
3. Set `HOST=0.0.0.0` and `PORT=8001`.
4. Add CORS origins for your frontend host.
5. Start FastAPI.
6. Set web/mobile backend URLs to the host IP.

---

FastAPI guide updated for local development and cloned project workflows.
