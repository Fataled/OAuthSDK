# Auth Platform

A authentication backend built with FastAPI. Supports Google OAuth2, email/password login, MFA with TOTP, JWT-based auth, and token blacklisting via Redis. Includes client SDKs for Python and C#.

---

## Features

- Google OAuth2 login
- Email/password registration and login
- MFA with TOTP (Google Authenticator / Authy)
- JWT issuance and verification
- Token blacklisting via Redis (logout)
- Admin-only endpoints
- Client SDKs for Python and C#

---

## Tech Stack

- **Python FastAPI** — API server
- **PostgreSQL** — user storage
- **SQLAlchemy + asyncpg** — async ORM
- **Alembic** — database migrations
- **Redis** — token blacklisting
- **python-jose** — JWT encoding/decoding
- **passlib + bcrypt** — password hashing
- **pyotp** — TOTP generation and verification
- **Authlib** — Google OAuth2

---

## Prerequisites

- Python 3.11+
- PostgreSQL running locally on port 5432
- Redis running locally on port 6379 (or via Docker)
- A Google OAuth2 app with a client ID and secret

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo>
cd OAuthLibrary
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/mydb
SECRET_KEY=your_secret_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Set up the database

```bash
alembic upgrade head
```

### 4. Start Redis (if using Docker)

```bash
docker run -d --name redis -p 6379:6379 redis
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/auth/google` | Google OAuth2 login | No |
| POST | `/register` | Register with email and password | No |
| POST | `/login` | Login with email, password, and optional TOTP code | No |
| POST | `/logout` | Blacklist the current JWT | Yes |

### User

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/user` | Get current user from JWT | Yes |
| DELETE | `/user` | Delete current user | Yes |

### MFA

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/mfa/setup` | Generate a TOTP secret and return a QR code | Yes |
| POST | `/mfa/verify` | Verify a TOTP code and enable MFA | Yes |

### Admin

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/users` | List all users | Yes (admin only) |

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your_jwt>
```

To get a token, register or login and copy the `access_token` from the response.

---

## MFA Setup

1. Call `POST /mfa/setup` with your JWT — save the QR code image returned
2. Scan the QR code with Google Authenticator or Authy
3. Call `POST /mfa/verify?code=123456` with the 6-digit code from your app
4. MFA is now enabled — future logins require a `totp_code` field

---

## Client SDKs

### Python SDK

```bash
pip install sdk/python
```

```python
import asyncio
from auth_client import AuthClient

client = AuthClient("http://127.0.0.1:8000")

async def main():
    result = await client.register("user@example.com", "password123", "My Name")
    token = result["access_token"]

    user = await client.get_user(token)
    print(user)

    await client.logout(token)

asyncio.run(main())
```

### C# SDK

Add a reference to `sdk/csharp/AuthClient/AuthClient.csproj` in your project.

```csharp
var client = new AuthClient.AuthClient("http://127.0.0.1:8000");

var result = await client.RegisterAsync("user@example.com", "password123", "My Name");
var token = result.GetProperty("access_token").GetString()!;

var user = await client.GetUserAsync(token);
Console.WriteLine(user);

await client.LogoutAsync(token);
```

---

## Project Structure

```
OAuthLibrary/
  main.py           # FastAPI app and route definitions
  auth.py           # JWT, password hashing, MFA, dependencies
  database.py       # SQLAlchemy async engine and session
  models.py         # User model
  redis_client.py   # Redis connection
  alembic/          # Database migrations
  sdk/
    python/         # Python client SDK
    csharp/         # C# client SDK
```

---

## Making a User an Admin

Connect to your database and run:

```sql
UPDATE public.users SET is_admin = true WHERE email = 'youremail@example.com';
```
