"""
FastAPI Backend for Smart Plant Watering System
Independent backend with SQLite/PostgreSQL database
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt
import httpx
import json

load_dotenv()

# ============== CONFIGURATION ==============
DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = int(os.getenv("PORT", 8001))
HOST = os.getenv("HOST", "0.0.0.0")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fastapi.db")
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print(f"[FastAPI] DEBUG={DEBUG}, PORT={PORT}")
print(f"[FastAPI] Database: {DATABASE_URL}")
print(f"[FastAPI] CORS Origins: {CORS_ORIGINS}")

# ============== DATABASE MODELS ==============

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plants = relationship("Plant", back_populates="owner", cascade="all, delete-orphan")
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    location = Column(String)
    moisture = Column(Float, default=50.0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="plants")
    watering_history = relationship("WateringHistory", back_populates="plant", cascade="all, delete-orphan")


class WateringHistory(Base):
    __tablename__ = "watering_history"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    watered_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    plant = relationship("Plant", back_populates="watering_history")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tokens")


# Create tables
Base.metadata.create_all(bind=engine)

# ============== PYDANTIC SCHEMAS ==============

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_staff: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PlantCreate(BaseModel):
    name: str
    type: str
    location: str
    moisture: Optional[float] = 50.0


class PlantUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    moisture: Optional[float] = None


class PlantResponse(BaseModel):
    id: int
    name: str
    type: str
    location: str
    moisture: float
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WateringHistoryResponse(BaseModel):
    id: int
    plant_id: int
    watered_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class WaterPlantRequest(BaseModel):
    notes: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


# ============== DEPENDENCIES ==============

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: int, db: Session = None) -> str:
    """Create JWT token and store in database"""
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(days=30)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Store token in database if db is provided
    if db:
        db_token = Token(user_id=user_id, token=token)
        db.add(db_token)
        db.commit()

    return token


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        # Handle "Token <token>" format
        token_str = authorization
        if token_str.startswith("Token "):
            token_str = token_str[6:]

        # Try to decode JWT
        try:
            payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token format")

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user

        except JWTError as e:
            # If JWT fails, try to find token in database
            db_token = db.query(Token).filter(Token.token == token_str).first()
            if not db_token:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            user = db.query(User).filter(User.id == db_token.user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Optional[User]:
    if not authorization:
        return None

    try:
        token_str = authorization
        if token_str.startswith("Token "):
            token_str = token_str[6:]

        try:
            payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token format")

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
        except JWTError:
            db_token = db.query(Token).filter(Token.token == token_str).first()
            if not db_token:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            user = db.query(User).filter(User.id == db_token.user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def build_django_proxy_url(path: str, query: str) -> str:
    if not DJANGO_API_URL:
        raise HTTPException(status_code=503, detail="DJANGO_API_URL is not configured")

    base_url = DJANGO_API_URL.rstrip("/")
    if path.startswith("/api/"):
        path = path[5:]
    elif path == "/api":
        path = ""

    target = f"{base_url}/{path.lstrip('/')}"
    if query:
        target = f"{target}?{query}"

    return target


async def proxy_to_django(request: Request) -> Response:
    target_url = build_django_proxy_url(request.url.path, request.url.query)
    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length", "transfer-encoding", "connection"}}
    body = await request.body()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        django_response = await client.request(
            request.method,
            target_url,
            headers=headers,
            content=body,
            timeout=30.0,
        )

    excluded_headers = {"content-length", "transfer-encoding", "connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "upgrade"}
    response_headers = {k: v for k, v in django_response.headers.items() if k.lower() not in excluded_headers}

    return Response(
        content=django_response.content,
        status_code=django_response.status_code,
        headers=response_headers,
        media_type=django_response.headers.get("content-type"),
    )


# ============== FASTAPI APP ==============

app = FastAPI(
    title="Smart Plant Watering System - FastAPI",
    description="Independent FastAPI backend for Smart Plant Watering System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if DJANGO_API_URL:
    @app.api_route("/api", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def django_api_proxy(path: str = "", request: Request):
        return await proxy_to_django(request)

# ============== HEALTH CHECK ==============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FastAPI Backend (Independent)",
        "timestamp": datetime.utcnow().isoformat(),
        "debug": DEBUG,
        "database": "SQLite" if "sqlite" in DATABASE_URL else "PostgreSQL"
    }


# ============== AUTHENTICATION ENDPOINTS ==============

@app.post("/api/users/register/", response_model=TokenResponse, tags=["Authentication"])
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    if user_data.password != user_data.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, db)

    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }


@app.post("/api/users/login/", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return token"""
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_access_token(user.id, db)

    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }


@app.get("/api/users/me/", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current logged-in user info"""
    return UserResponse.from_orm(current_user)


@app.post("/api/users/logout/", tags=["Authentication"])
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user"""
    return {"success": True, "message": "Logged out successfully"}


@app.put("/api/users/update_profile/", response_model=UserResponse, tags=["Authentication"])
async def update_profile(profile_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile"""
    if "email" in profile_data:
        current_user.email = profile_data["email"]
    if "username" in profile_data:
        current_user.username = profile_data["username"]

    db.commit()
    db.refresh(current_user)
    return UserResponse.from_orm(current_user)


@app.post("/api/users/change_password/", tags=["Authentication"])
async def change_password(password_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change user password"""
    if not verify_password(password_data.get("old_password"), current_user.password_hash):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    current_user.password_hash = get_password_hash(password_data.get("new_password"))
    db.commit()
    return {"success": True, "message": "Password changed successfully"}


@app.post("/api/users/request_password_reset/", tags=["Authentication"])
async def request_password_reset(reset_data: dict, db: Session = Depends(get_db)):
    """Request password reset"""
    user = db.query(User).filter(User.email == reset_data.get("email")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "message": "Password reset link sent to email"}


# ============== USERS ENDPOINTS ==============

@app.get("/api/users/", response_model=List[UserResponse], tags=["Users"])
async def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    return [UserResponse.from_orm(u) for u in db.query(User).all()]


@app.get("/api/users/{user_id}/", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get specific user (admin only)"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)


@app.delete("/api/users/{user_id}/", tags=["Users"])
async def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a user (admin only)"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"success": True, "message": "User deleted"}


@app.post("/api/users/register_admin/", response_model=TokenResponse, tags=["Users"])
async def register_admin(user_data: UserRegister, current_user: Optional[User] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    """Register an admin user"""
    if current_user and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    if user_data.password != user_data.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_staff=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, db)

    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }


@app.post("/api/users/{user_id}/reset_password/", tags=["Users"])
async def reset_user_password(user_id: int, password_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Reset user password (admin only)"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(password_data.get("new_password"))
    db.commit()
    return {"success": True, "message": "Password reset successfully"}


# ============== PLANTS ENDPOINTS ==============

@app.get("/api/plants/", response_model=List[PlantResponse], tags=["Plants"])
async def get_plants(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all plants for current user; admin sees all plants"""
    query = db.query(Plant)
    if not current_user.is_staff:
        query = query.filter(Plant.owner_id == current_user.id)

    plants = query.all()
    return [PlantResponse.from_orm(p) for p in plants]


@app.get("/api/plants/needing_water/", response_model=List[PlantResponse], tags=["Plants"])
async def get_plants_needing_water(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get plants that need watering (moisture < 40%)"""
    plants = db.query(Plant).filter(
        Plant.owner_id == current_user.id,
        Plant.moisture < 40
    ).all()
    return [PlantResponse.from_orm(p) for p in plants]


@app.get("/api/plants/stats/", tags=["Plants"])
async def get_plant_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get plant statistics for current user"""
    plants = db.query(Plant).filter(Plant.owner_id == current_user.id).all()

    total = len(plants)
    healthy = len([p for p in plants if p.moisture >= 40])
    needing_water = len([p for p in plants if p.moisture < 40])
    avg_moisture = sum(p.moisture for p in plants) / total if total > 0 else 0
    critical = [p.name for p in plants if p.moisture < 20]

    return {
        "total_plants": total,
        "healthy_plants": healthy,
        "plants_needing_water": needing_water,
        "average_moisture": avg_moisture,
        "critical_plants": critical
    }


@app.get("/api/plants/admin_stats/", tags=["Plants"])
async def get_admin_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get system-wide statistics (admin only)"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    all_plants = db.query(Plant).all()
    all_users = db.query(User).all()

    total = len(all_plants)
    healthy = len([p for p in all_plants if p.moisture >= 40])
    needing_water = len([p for p in all_plants if p.moisture < 40])
    avg_moisture = sum(p.moisture for p in all_plants) / total if total > 0 else 0

    return {
        "total_plants": total,
        "total_users": len(all_users),
        "healthy_plants": healthy,
        "plants_needing_water": needing_water,
        "average_moisture": avg_moisture
    }


@app.get("/api/plants/{plant_id}/", response_model=PlantResponse, tags=["Plants"])
async def get_plant(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get specific plant"""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant.owner_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Access denied")

    return PlantResponse.from_orm(plant)


@app.post("/api/plants/", response_model=PlantResponse, tags=["Plants"])
async def create_plant(plant_data: PlantCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new plant"""
    plant = Plant(
        name=plant_data.name,
        type=plant_data.type,
        location=plant_data.location,
        moisture=plant_data.moisture,
        owner_id=current_user.id
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return PlantResponse.from_orm(plant)


@app.put("/api/plants/{plant_id}/", response_model=PlantResponse, tags=["Plants"])
async def update_plant(plant_id: int, plant_data: PlantUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a plant"""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant.owner_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Access denied")

    if plant_data.name:
        plant.name = plant_data.name
    if plant_data.type:
        plant.type = plant_data.type
    if plant_data.location:
        plant.location = plant_data.location
    if plant_data.moisture is not None:
        plant.moisture = plant_data.moisture

    db.commit()
    db.refresh(plant)
    return PlantResponse.from_orm(plant)


@app.delete("/api/plants/{plant_id}/", tags=["Plants"])
async def delete_plant(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a plant"""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant.owner_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(plant)
    db.commit()
    return {"success": True, "message": "Plant deleted"}


@app.post("/api/plants/{plant_id}/water/", response_model=WateringHistoryResponse, tags=["Plants"])
async def water_plant(plant_id: int, water_data: WaterPlantRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Water a plant and record history"""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant.owner_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update moisture level
    plant.moisture = min(100.0, plant.moisture + 30)

    # Record history
    history = WateringHistory(
        plant_id=plant_id,
        notes=water_data.notes
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    return WateringHistoryResponse.from_orm(history)


# ============== WATERING HISTORY ENDPOINTS ==============

@app.get("/api/plants/{plant_id}/watering_history/", response_model=List[WateringHistoryResponse], tags=["History"])
async def get_plant_watering_history(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get watering history for a specific plant"""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant.owner_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Access denied")

    history = db.query(WateringHistory).filter(WateringHistory.plant_id == plant_id).all()
    return [WateringHistoryResponse.from_orm(h) for h in history]


@app.get("/api/watering_history/", response_model=List[WateringHistoryResponse], tags=["History"])
async def get_watering_history(page: int = 1, page_size: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all watering history for current user (paginated)"""
    skip = (page - 1) * page_size

    history = db.query(WateringHistory).join(Plant).filter(
        Plant.owner_id == current_user.id
    ).offset(skip).limit(page_size).all()

    return [WateringHistoryResponse.from_orm(h) for h in history]


@app.get("/api/watering_history/stats/", tags=["History"])
async def get_watering_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get watering statistics"""
    user_plants = db.query(Plant).filter(Plant.owner_id == current_user.id).all()

    total_waterings = 0
    for plant in user_plants:
        total_waterings += len(plant.watering_history)

    return {
        "total_waterings": total_waterings,
        "plants_owned": len(user_plants)
    }


@app.get("/api/watering_history/admin/", response_model=List[WateringHistoryResponse], tags=["History"])
async def get_all_watering_history_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all watering history for admin users"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin access required")

    history = db.query(WateringHistory).all()
    return [WateringHistoryResponse.from_orm(h) for h in history]


@app.get("/api/watering-history/", response_model=List[WateringHistoryResponse], tags=["History"])
async def get_all_watering_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all watering history for current user"""
    history = db.query(WateringHistory).join(Plant).filter(
        Plant.owner_id == current_user.id
    ).all()

    return [WateringHistoryResponse.from_orm(h) for h in history]


@app.get("/api/watering-history/by_plant/", response_model=List[WateringHistoryResponse], tags=["History"])
async def get_plant_history_by_id(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get watering history for a specific plant"""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant.owner_id != current_user.id and not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Access denied")

    history = db.query(WateringHistory).filter(WateringHistory.plant_id == plant_id).all()
    return [WateringHistoryResponse.from_orm(h) for h in history]


# ============== SETUP/ADMIN REGISTRATION ==============

@app.get("/setup", response_class=HTMLResponse, tags=["Setup"])
async def setup_page(db: Session = Depends(get_db)):
    """Simple admin registration page"""
    # Check if any admins exist
    admin_exists = db.query(User).filter(User.is_staff == True).first()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Plant Watering - Admin Setup</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                width: 100%;
                max-width: 400px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-top: 0;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #555;
                font-weight: bold;
            }
            input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
                font-size: 14px;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
            }
            button {
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #5568d3;
            }
            .message {
                margin-top: 20px;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌱 Admin Setup</h1>
            """ + (f"<div class='message info'>⚠️ Admin already exists. Use login to access admin features.</div>" if admin_exists else f"<div class='message info'>📝 Create the first admin account for your system.</div>") + """
            
            <form id="adminForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <div class="form-group">
                    <label for="password_confirm">Confirm Password</label>
                    <input type="password" id="password_confirm" name="password_confirm" required>
                </div>
                
                <button type="submit">Create Admin Account</button>
            </form>
            
            <div id="message"></div>
        </div>
        
        <script>
            document.getElementById('adminForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const password_confirm = document.getElementById('password_confirm').value;
                const messageDiv = document.getElementById('message');
                
                if (password !== password_confirm) {
                    messageDiv.innerHTML = '<div class="message error">❌ Passwords do not match</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/api/setup/register-admin/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            username,
                            email,
                            password,
                            password_confirm
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        messageDiv.innerHTML = '<div class="message success">✅ Admin account created successfully!<br>Redirecting to login...</div>';
                        localStorage.setItem('auth_token', data.token);
                        localStorage.setItem('currentUser', JSON.stringify({
                            username: data.user.username,
                            email: data.user.email,
                            id: data.user.id,
                            is_staff: data.user.is_staff,
                            role: 'admin'
                        }));
                        setTimeout(() => {
                            window.location.href = 'http://localhost:3000/dashboard';
                        }, 2000);
                    } else {
                        messageDiv.innerHTML = '<div class="message error">❌ ' + (data.detail || 'Failed to create admin account') + '</div>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="message error">❌ Error: ' + error.message + '</div>';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/api/setup/register-admin/", response_model=TokenResponse, tags=["Setup"])
async def setup_register_admin(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register admin - accessible during setup (if no admins exist) or anytime"""
    if user_data.password != user_data.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create admin user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_staff=True,  # Always create as admin via this endpoint
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, db)

    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }


# ============== ROOT ==============

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Plant Watering System - FastAPI Backend",
        "docs": "/docs",
        "health": "/health",
        "setup": "/setup"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
