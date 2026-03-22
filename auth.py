from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import Select

from database import AsyncSessionLocal
from models import User
from redis_client import redis_client

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Create a copy of the data to not mess with the original
# Set an expiry time
# Add the expiry to the copy of the data
# Encode using jwt and return
def create_access_token(data: dict) -> str:
    """
    Turn the data into a jwt token
    :param data: dict of data from service you are requesting access to
    :return: A JWT encoded access token in the form of a string
    """
    # Copy data 1st turns out you SHOULD NOT mutate the data given
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:

        if await is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        payload = decode_access_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
        return {"id": user_id, "email": email, "token": token, "exp": payload.get("exp")}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def blacklist_token(token: str, exp:int) -> None:
    ttl = exp - int(datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        await redis_client.setex(f"blacklist:{token}", ttl, "true")

async def is_token_blacklisted(token: str)-> bool:
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None

async def require_admin(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(Select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        if not user or not user.is_admin:
            raise HTTPException(status_code=400, detail="Admin required")
        return current_user