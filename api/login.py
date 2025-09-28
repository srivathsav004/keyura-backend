from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from database import supabase
import bcrypt

router = APIRouter(prefix="/api", tags=["auth"])


class LoginRequest(BaseModel):
    wallet_address: str = Field(..., min_length=10)
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    userid: int
    wallet_address: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    wallet_address = payload.wallet_address.strip().lower()
    # Fetch user by wallet address
    result = (
        supabase
        .table("users")
        .select("userid, wallet_address, password_hash")
        .eq("wallet_address", wallet_address)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = result.data[0]
    stored_hash = user.get("password_hash")
    if not stored_hash or not bcrypt.checkpw(payload.password.encode("utf-8"), stored_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return LoginResponse(userid=user["userid"], wallet_address=user["wallet_address"])
