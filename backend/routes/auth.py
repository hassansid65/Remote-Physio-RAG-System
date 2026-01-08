from fastapi import APIRouter, HTTPException
from backend.models.user import UserCreate, UserResponse
from pymongo import MongoClient
from backend.config import Config
import uuid
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]
users_collection = db["users"]

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user with email"""
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        return UserResponse(
            user_id=existing_user["user_id"],
            email=existing_user["email"],
            created_at=existing_user["created_at"]
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    user_data = {
        "user_id": user_id,
        "email": user.email,
        "created_at": datetime.now()
    }
    
    users_collection.insert_one(user_data)
    
    return UserResponse(
        user_id=user_id,
        email=user.email,
        created_at=user_data["created_at"]
    )

@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    user = users_collection.find_one({"user_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        created_at=user["created_at"]
    )