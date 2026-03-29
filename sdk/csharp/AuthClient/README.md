# AuthClient

A lightweight .NET authentication SDK for working with an auth API.

AuthClient provides simple async methods for modern authentication workflows:

* user registration
* login (with optional MFA/TOTP)
* logout
* get current user
* delete user
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
* OIDC provider support
* MFA (TOTP + QR setup)
* Password reset flows
* Mail service configuration (admin)
* Easy integration with any .NET app

---

## Installation

```bash
dotnet add package AuthClient
```

---

## Requirements

* .NET 6.0 or later
* A backend API with endpoints:

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

## Getting Started

### Create the client

```csharp
using AuthClient;

var client = new AuthClient.AuthClient("https://your-api-url.com");
```

---

## Usage

### Register

```csharp
var result = await client.RegisterAsync(
    "user@example.com",
    "StrongPassword123",
    "John Doe"
);
```

---

### Login

```csharp
var result = await client.LoginAsync(
    "user@example.com",
    "StrongPassword123"
);
```

### Login with MFA

```csharp
var result = await client.LoginMfaAsync(
    "user_id",
    "123456"
);
```

### Login with refresh token

```csharp
var result = await client.LoginRefreshTokenAsync(
    "refresh-token"
);
```

### get refresh token

```csharp
var result = await client.GetRefreshTokenAsync(
  "your-jwt-token"  
);
```

---

### Logout

```csharp
await client.LogoutAsync("your-jwt-token");
```

---

### Get current user

```csharp
var user = await client.GetUserAsync("your-jwt-token");
```

---

### Delete current user

```csharp
await client.DeleteUserAsync("your-jwt-token");
```

### Check Email Exists in db
```csharp
await client.CheckEmail("email")
```

---

### Get all users (admin)

```csharp
var users = await client.GetAllUsersAsync("admin-token");
```

---

### Delete user (admin)

```csharp
await client.AdminDeleteUserAsync("admin-token", "user-id");
```

---

## OpenID Connect (OIDC)

### Register provider (admin)

```csharp
await client.RegisterOidcProviderAsync(
    "admin-key",
    "google",
    "client-id",
    "client-secret",
    "https://accounts.google.com/.well-known/openid-configuration"
);
```

---

### Remove provider (admin)

```csharp
await client.RemoveOidcProvider("admin-key", "google");
```

---

### Get login URL

```csharp
var url = await client.LoginWithOidc("google");
```

Open the returned URL in a browser to authenticate.

---

## Multi-Factor Authentication (MFA)

### Setup MFA (QR Code)

```csharp
byte[] qrCode = await client.SetupMfa("your-jwt-token");
File.WriteAllBytes("qrcode.png", qrCode);
```

---

### Verify MFA

```csharp
await client.VerifyMfa("your-jwt-token", "123456");
```

---

### Disable MFA

```csharp
await client.DisableMfa("your-jwt-token", "123456");
```

---

## Password Reset

### Request reset

```csharp
await client.RequestPasswordReset("user@example.com");
```

---

### Reset password

```csharp
await client.ResetPassword(
    "user@example.com",
    "NewPassword123",
    "reset-code"
);
```

---

## Mail Service (Admin)

### Configure mail

```csharp
await client.ModifyMailService(
    "admin-key",
    "sender",
    "sendgrid-api-key"
);
```

---

### Remove mail service

```csharp
await client.DeleteMailServiceAsync("admin-token");
```

---

## Error Handling

All requests use `EnsureSuccessStatusCode()`.

Wrap calls in try/catch:

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

---

## Notes

* Responses are returned as `JsonElement`
* Tokens must be passed manually
* OIDC providers are registered at runtime
* MFA setup returns a QR code image (PNG)
* Designed to be minimal and flexible

---

## Project Structure

```
AuthClient/
├── AuthClient/   # SDK (published to NuGet)
└── TestApp/      # Example app (not published)
```

---

## License

MIT License

---

## Author

Brume Ako
