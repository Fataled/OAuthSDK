# AuthClient

A lightweight authentication client library for working with a FastAPI-based auth API.

This project includes SDK support for:

* C# / .NET
* Python

Both clients provide clean wrappers around common authentication workflows such as:

* user registration
* login
* logout
* get current user
* delete current user
* admin user management
* OpenID Connect (OIDC)
* multi-factor authentication (MFA)
* password reset
* mail service configuration

Built by Brume Ako.

---

## Features

* Simple, clean API
* Async-first design
* Token-based authentication
* C# and Python client support
* OIDC provider support
* MFA setup and verification
* Password reset flows
* Admin endpoints
* Easy integration with backend services and apps

---

## Installation

### C# / .NET

```bash
dotnet add package AuthClient
```

### Python

```bash
pip install httpx
```

---

## Requirements

* .NET 6.0 or later for the C# SDK
* Python 3.9+ recommended for the Python client
* A backend API with endpoints such as:

  * POST /register
  * POST /login
  * POST /logout
  * GET /me
  * DELETE /delete
  * GET /admin/users
  * DELETE /admin/delete-user/{user_id}
  * POST /oidc/register
  * DELETE /oidc/remove
  * GET /oidc/login-url/{provider}
  * POST /mfa/setup
  * POST /mfa/verify
  * DELETE /mfa/disable
  * POST /auth/reset-request
  * POST /auth/password-reset
  * POST /modify-mail
  * DELETE /remove-mail

---

## C# SDK

### Create the client

```csharp
using AuthClient;

var client = new AuthClient.AuthClient("https://your-api-url.com");
```

### Register

```csharp
var result = await client.RegisterAsync(
    "user@example.com",
    "StrongPassword123",
    "John Doe"
);
```

### Login

```csharp
var result = await client.LoginAsync(
    "user@example.com",
    "StrongPassword123"
);
```

### Login with MFA

```csharp
var result = await client.LoginAsync(
    "user@example.com",
    "StrongPassword123",
    "123456"
);
```

### Logout

```csharp
await client.LogoutAsync("your-jwt-token");
```

### Get current user

```csharp
var user = await client.GetUserAsync("your-jwt-token");
```

### Delete current user

```csharp
await client.DeleteUserAsync("your-jwt-token");
```

### Get all users (admin)

```csharp
var users = await client.GetAllUsersAsync("admin-token");
```

### Delete user (admin)

```csharp
await client.AdminDeleteUserAsync("admin-token", "user-id");
```

### Register OIDC provider (admin)

```csharp
await client.RegisterOidcProviderAsync(
    "admin-token",
    "google",
    "client-id",
    "client-secret",
    "https://accounts.google.com/.well-known/openid-configuration"
);
```

### Remove OIDC provider (admin)

```csharp
await client.RemoveOidcProvider("admin-token", "google");
```

### Get OIDC login URL

```csharp
var url = await client.LoginWithOidc("google");
```

Open the returned URL in a browser to authenticate.

### Setup MFA

```csharp
byte[] qrCode = await client.SetupMfa("your-jwt-token");
File.WriteAllBytes("qrcode.png", qrCode);
```

### Verify MFA

```csharp
await client.VerifyMfa("your-jwt-token", "123456");
```

### Disable MFA

```csharp
await client.DisableMfa("your-jwt-token", "123456");
```

### Request password reset

```csharp
await client.RequestPasswordReset("user@example.com");
```

### Reset password

```csharp
await client.ResetPassword(
    "user@example.com",
    "NewPassword123",
    "reset-code"
);
```

### Configure mail service (admin)

```csharp
await client.ModifyMailService(
    "admin-token",
    "email@gmail.com",
    "password",
    "email@gmail.com",
    587,
    "smtp.gmail.com",
    true,
    false
);
```

### Remove mail service (admin)

```csharp
await client.DeleteMailServiceAsync("admin-token");
```

---

## Python Client

### Setup

```python
from auth_client import AuthClient

client = AuthClient("https://your-api-url.com")
```

### Register

```python
await client.register(
    "user@example.com",
    "StrongPassword123",
    "John Doe"
)
```

### Login

```python
await client.login(
    "user@example.com",
    "StrongPassword123"
)
```

### Login with MFA

```python
await client.login(
    "user@example.com",
    "StrongPassword123",
    "123456"
)
```

### Get current user

```python
await client.get_user(token)
```

### Logout

```python
await client.logout(token)
```

### Delete user

```python
await client.delete_user(token)
```

### Admin: Get all users

```python
await client.get_all_users(admin_token)
```

### Admin: Delete user

```python
await client.admin_delete_user(admin_token, "user-id")
```

### Example usage

```python
import asyncio
from auth_client import AuthClient

async def main():
    client = AuthClient("https://your-api-url.com")

    user = await client.register(
        "user@example.com",
        "StrongPassword123",
        "John Doe"
    )

    login = await client.login(
        "user@example.com",
        "StrongPassword123"
    )

    print(login)

asyncio.run(main())
```

👉 Full Python implementation available in `/python/auth_client.py`

---

## Error Handling

Both clients rely on HTTP status validation.

### C#

```csharp
try
{
    await client.LoginAsync("user@example.com", "password");
}
catch (HttpRequestException ex)
{
    Console.WriteLine(ex.Message);
}
```

### Python

```python
try:
    result = await client.login("user@example.com", "password")
except httpx.HTTPStatusError as ex:
    print(str(ex))
```

---

## Notes

* C# methods return `JsonElement` unless otherwise noted
* The Python client returns parsed JSON as `dict`
* Tokens must be passed manually to protected endpoints
* OIDC providers are registered at runtime unless backend persistence is added
* MFA setup returns a QR code image as PNG bytes in the C# SDK
* Admin endpoints require a valid admin token

---

## Project Structure

```text
AuthClient/
├── AuthClient/   # C# SDK published to NuGet
├── TestApp/      # Example C# app
└── python/       # Optional Python client implementation
```

---

## License

MIT License

---

## Author

Brume Ako
