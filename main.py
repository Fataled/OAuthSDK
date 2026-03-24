import io
from datetime import datetime, timezone
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
import pyotp
import qrcode
from fastapi import FastAPI, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from dotenv import load_dotenv
import os
from sqlalchemy import select
from starlette.responses import StreamingResponse
from database import AsyncSessionLocal
from models import User
from auth import create_access_token, get_current_user, hash_password, verify_password, blacklist_token, require_admin, create_password_reset_code
from pydantic import BaseModel
from oauth_client import oauth, create_openid_connect_client_registration

load_dotenv()
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))


client_id=os.getenv("GOOGLE_CLIENT_ID")
client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
client_kwargs={'scope': 'openid email profile'}

create_openid_connect_client_registration('google',
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=server_metadata_url,
    client_kwargs=client_kwargs)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

fm = FastMail(conf)

@app.get("/login/{provider}")
async def oidc_login(provider: str, request: Request):
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
    redirect_uri = request.url_for("auth_via_oidc", provider=provider)
    print(f"Redirect URI: {redirect_uri}")
    return await client.authorize_redirect(request, redirect_uri)

@app.get("/auth/{provider}", name="auth_via_oidc")
async def auth_via_oidc(provider: str, request: Request):
    client = oauth.create_client(provider)

    if client is None:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")

    token = await client.authorize_access_token(request)
    user_info = token["userinfo"]

    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=user_info["email"],
                name=user_info.get("name"),
                picture=user_info.get("picture"),
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "provider": provider
    }

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

class totpCode(BaseModel):
    code: str
@app.post("/mfa/verify")
async def mfa_verify(code: totpCode, current_user: dict = Depends(get_current_user)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        totp = pyotp.TOTP(user.totp_secret)
        print(f"Expected code: {totp.now()}")
        print(f"Received code: {code}")
        if not totp.verify(code.code, valid_window=2):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

        user.mfa_enabled = True
        await db_session.commit()

    return {"message": "MFA enabled successfully"}

@app.delete("/delete")
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

@app.delete("/admin/delete-user/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        await db_session.delete(user)
        await db_session.commit()

    return {"message": "User deleted successfully"}

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetModel(BaseModel):
    email: str
    code: str
    password: str

@app.post("/auth/reset-request")
async def reset_request_user(body: PasswordResetRequest):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        code, exp = create_password_reset_code()
        user.reset_password_token = code
        user.reset_password_expiry = exp
        await db_session.commit()
        await db_session.refresh(user)

        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[body.email],
            body=f"""
            <h2>Password Reset Request</h2>
            <p>You requested a password reset. Use the code below to reset your password.</p>
            <h1 style="letter-spacing: 4px;">{code}</h1>
            <p>This code expires in 15 minutes. If you didn't request this, ignore this email.</p>
            """,
            subtype="html"
        )

        await fm.send_message(message)

    return {"message": "Password reset request sent successfully"}



@app.post("/auth/password-reset")
async def change_password(reset_data: PasswordResetModel):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.email == reset_data.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")
        if not user.reset_password_expiry or datetime.now(timezone.utc) > user.reset_password_expiry.replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=400, detail="Password reset request expired")
        if user.reset_password_token != reset_data.code:
            raise HTTPException(status_code=400, detail="Invalid reset code")

        user.hashed_password = hash_password(reset_data.password)
        user.reset_password_token = None
        user.reset_password_expiry = None
        await db_session.commit()
        await db_session.refresh(user)

    return {"message": "Password was successfully changed"}


class OIDCProviderRequest(BaseModel):
    name: str
    client_id: str
    client_secret: str
    metadata_url: str
    scope: str = "openid email profile"
@app.post("/oidc/register")
async def register_oidc_provider(body: OIDCProviderRequest, current_user: dict = Depends(require_admin)):
    oauth.register(
        body.name,
        client_id=body.client_id,
        client_secret=body.client_secret,
        server_metadata_url=body.metadata_url,
        client_kwargs={"scope": body.scope}
    )
    return {"message": f"{body.name} registered successfully"}

class MailService(BaseModel):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_starttls: bool
    mail_ssl_tls: bool
@app.post("/modify-mail")
async def modify_mail_service(body: MailService, current_user: dict = Depends(require_admin)):
    global fm
    conf = ConnectionConfig(
        MAIL_USERNAME=body.mail_username,
        MAIL_PASSWORD=body.mail_password,
        MAIL_FROM=body.mail_from,
        MAIL_PORT=body.mail_port,
        MAIL_SERVER=body.mail_server,
        MAIL_STARTTLS=body.mail_starttls,
        MAIL_SSL_TLS=body.mail_ssl_tls,
    )
    fm = FastMail(conf)

@app.delete("/remove-mail")
async def remove_mail_servivce( current_user: dict = Depends(require_admin)):
    global fm
    fm = FastMail()

@app.get("/oidc/login-url/{provider}")
async def get_oidc_login_url(provider: str, request: Request):
    client = oauth.create_client(provider)

    if client is None:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")

    redirect_uri = request.url_for("auth_via_oidc", provider=provider)

    uri, state = await client.create_authorization_url(str(redirect_uri))

    return {
        "provider": provider,
        "authorization_url": uri,
        "state": state
    }

class oidcProvider:
    oidc_provider: str
@app.delete("/oidc/remove")
async def remove_oidc_login(provider: oidcProvider, current_user: dict = Depends(require_admin)):
    oauth.destroy_client(provider)
    return {"message": f"OIDC login removed successfully"}

@app.delete("/mfa/disable")
async def mfa_disable(code: totpCode ,current_user: dict = Depends(require_admin)):
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist")

        totp = pyotp.TOTP(user.totp_secret)
        print(f"Expected code: {totp.now()}")
        print(f"Received code: {code}")
        if not totp.verify(code.code, valid_window=2):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

        user.mfa_enabled = False
        await db_session.commit()

    return {"message": "MFA enabled successfully"}