from fastapi import Depends, HTTPException, status, Request, Response, Cookie
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError
from users.models import UserModel
from core.database import get_db
from core.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "refresh",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token: str, token_type: str):
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms="HS256")
        if decoded.get("type") != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        if datetime.now(timezone.utc) > datetime.fromtimestamp(decoded["exp"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        return decoded["user_id"]
    except (InvalidSignatureError, DecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_authenticated_user(
    access_token: str = Cookie(None), 
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
    
    user_id = verify_token(access_token, "access")
    user = db.query(UserModel).filter_by(id=user_id).one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

'''
from fastapi import APIRouter, Depends, HTTPException, Response, Request

@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db),response: Response):
    user_obj = (
        db.query(UserModel)
        .filter_by(username=request.username.lower())
        .first()
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user aor password",
        )
    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user aor password",
        )

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="Lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
    return JSONResponse(
        content={
            "detail": "logged in successfully",
        }
    )

@router.post("/refresh-token")
async def user_refresh_token(
    request: Request, db: Session = Depends(get_db),refresh_token: str = Cookie(None),response: Response
):
    user_id = decode_refresh_token(refresh_token)
    access_token = generate_access_token(user_id)
    response.set_cookie("access_token", new_access_token, httponly=True, secure=True, samesite="Lax")
    return JSONResponse(content={"detail": "token refreshed"})


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")    
    return JSONResponse(content={"detail": "Logged out"})

'''