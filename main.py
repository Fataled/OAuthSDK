import io
import pyotp
import qrcode
from fastapi import FastAPI, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os
from sqlalchemy import select
from starlette.responses import StreamingResponse
from database import AsyncSessionLocal
from models import User
from auth import create_access_token, get_current_user, hash_password, verify_password, blacklist_token, require_admin
from pydantic import BaseModel


load_dotenv()
app = FastAPI()
oauth = OAuth()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))

oauth.register(
    'google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.get("/login/google")
async def google_login(request: Request):
    google = oauth.create_client('google')
    redirect_uri = request.url_for("auth_via_google")
    print(f"Redirect URI: {redirect_uri}")
    return await google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google")
async def auth_via_google(request: Request):
    google = oauth.create_client('google')
    token = await google.authorize_access_token(request)
    user_info = token['userinfo']

    async with AsyncSessionLocal() as db_session:
        # Check if user alr exists
        result = await db_session.execute(
            select(User).where(User.email == user_info['email'])
        )
        user = result.scalar_one_or_none() # This either returns the user OR none

        if user is None:
            user = User(
                email=user_info['email'],
                name=user_info['name'],
                picture=user_info['picture'],
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

    access_token = create_access_token(
        data={
            "sub": str(user.id), # sub - Subject
            "email": user.email
        })

    print(f"Token: {access_token}")

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def get_current_user(current_user: dict = Depends(get_current_user)):
    return current_user

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str
    totp_code: str | None = None
@app.post("/register")
async def register_user(body: RegisterRequest):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.email == body.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=body.email,
            name=body.name,
            hashed_password=hash_password(body.password)
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login")
async def login_user(body: LoginRequest):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(body.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        if user.mfa_enabled:
            if not body.totp_code:
                raise HTTPException(status_code=400, detail="MFA code required")
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(body.totp_code, valid_window=2):
                raise HTTPException(status_code=400, detail="Invalid MFA code")

        token = create_access_token(data={"sub": str(user.id), "email": user.email})


        return {"access_token": token, "token_type": "bearer"}

@app.post("/mfa/setup")
async def mfa_Setup(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        secret = pyotp.random_base32()
        user.totp_secret = secret
        await db_session.commit()

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user["email"], issuer_name="OAuthLibrary")

    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

@app.post("/mfa/verify")
async def mfa_verify(code: str, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        totp = pyotp.TOTP(user.totp_secret)
        print(f"Expected code: {totp.now()}")
        print(f"Received code: {code}")
        if not totp.verify(code, valid_window=2):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

        user.mfa_enabled = True
        await db_session.commit()

    return {"message": "MFA enabled successfully"}

@app.delete("/user")
async def delete_user(current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        await db_session.delete(user)
        await db_session.commit()

    return {"message": "User deleted successfully"}

@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    await blacklist_token(current_user["token"], current_user["exp"])
    return {"message": "Logged out successfully"}

@app.get("/admin/users")
async def admin_users(current_user: dict = Depends(require_admin)):
    async with AsyncSessionLocal() as db_session:
        all_users = await db_session.execute(select(User).where(User.id == current_user["id"]))
        users = all_users.scalars().all()
        return [{"id": str(u.id), "email": u.email, "name": u.name, "is_admin": u.is_admin} for u in users]
