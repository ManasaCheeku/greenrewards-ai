import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import crud
from database import SessionLocal

SECRET_KEY = os.environ.get("JWT_SECRET", "change_this_secret_for_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Enforce secure secret in non-development scenarios. To bypass (only in local/dev/testing), set
# environment variable `ALLOW_INSECURE=1`.
if SECRET_KEY == "change_this_secret_for_prod" and os.environ.get("ALLOW_INSECURE", "0") != "1":
    raise RuntimeError("JWT_SECRET is not set. Set the JWT_SECRET env var to a secure value before starting the service.")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def require_role(role: str):
    async def role_checker(user = Depends(get_current_user)):
        if getattr(user, 'role', 'employee') != role and user.role != 'admin':
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
