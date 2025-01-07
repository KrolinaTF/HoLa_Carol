from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/v1")

class User(BaseModel):
    username: str

@router.post("/token")
async def generate_token(user: User):
    try:
        expiration = datetime.now(timezone.utc) + timedelta(hours=24)
        token = jwt.encode(
            {
                "sub": user.username,
                "exp": expiration.timestamp(),
                "iat": datetime.now(timezone.utc).timestamp()
            },
            os.getenv("SECRET_KEY", "your-secret-key-here"),
            algorithm="HS256"
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))