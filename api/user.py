from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from database import supabase
import bcrypt

router = APIRouter(prefix="/api", tags=["users"])


class CreateUserRequest(BaseModel):
    wallet_address: str = Field(..., min_length=10)
    password: str = Field(..., min_length=8)


class CreateUserResponse(BaseModel):
    userid: int
    wallet_address: str


@router.post("/users", response_model=CreateUserResponse)
def create_user(payload: CreateUserRequest):
    # Normalize wallet address
    wallet_address = payload.wallet_address.strip().lower()

    # Check if user already exists
    existing = supabase.table("users").select("userid").eq("wallet_address", wallet_address).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="User already exists for this wallet address")

    # Hash password securely
    hashed = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt())
    password_hash = hashed.decode("utf-8")

    # Insert into DB and return the inserted row
    result = supabase.table("users").insert(
        {"wallet_address": wallet_address, "password_hash": password_hash},
        returning="representation",
    ).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")

    row = result.data[0]
    return CreateUserResponse(userid=row["userid"], wallet_address=row["wallet_address"])
