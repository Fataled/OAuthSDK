using System.Diagnostics;
using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;

namespace AuthClient;

public class AuthClient
{
    private readonly HttpClient _httpClient;

    public AuthClient(string baseUrl)
    {
        // Set up the HTTP client with the base URL
        _httpClient = new HttpClient { BaseAddress = new Uri(baseUrl) };
    }

    public async Task<JsonElement> RegisterAsync(string email, string password, string name)
    {
        // Register a new user and return the JWT
        var response = await _httpClient.PostAsJsonAsync("/register", new
        {
            email,
            password,
            name
        });
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<LoginResult> LoginAsync(string email, string password)
    {
        var response = await _httpClient.PostAsJsonAsync("/login", new { email, password });
    
        if (!response.IsSuccessStatusCode)
        {
            var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            return new LoginResult { Error = error?.detail };
        }

        return await response.Content.ReadFromJsonAsync<LoginResult>();
    }

    public async Task<LoginResult> LoginMfaAsync(string userId, string totpCode)
    {
        var response = await _httpClient.PostAsJsonAsync("/login/mfa", new { user_id = userId, totp_code = totpCode });

        if (!response.IsSuccessStatusCode)
        {
            var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            return new LoginResult { Error = error?.detail };
        }

        return await response.Content.ReadFromJsonAsync<LoginResult>();
    }

    public async Task<JsonElement> LogoutAsync(string token)
    {
        // Blacklist the token
        var request = new HttpRequestMessage(HttpMethod.Post, "/logout");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> GetUserAsync(string token)
    {
        // Get the current user from the JWT
        var request = new HttpRequestMessage(HttpMethod.Get, "/me");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }
    
    public async Task<bool?> CheckEmail(string email)
    {
        var response = await _httpClient.PostAsync($"/auth/check-email", JsonContent.Create(new { email }));
        response.EnsureSuccessStatusCode(); //TODO Change this to proper error handling
        var exists = await response.Content.ReadFromJsonAsync<CheckEmailResponse>();
        return exists.Exists;
    }

    public async Task<JsonElement> DeleteUserAsync(string token)
    {
        var request = new HttpRequestMessage(HttpMethod.Delete, "/delete");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<RefreshTokenResponse> GetRefreshTokenAsync(string token)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/auth/refresh-token");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        if (!response.IsSuccessStatusCode)
        {
            var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            return new RefreshTokenResponse() { Error = error?.detail };
        }
        return await response.Content.ReadFromJsonAsync<RefreshTokenResponse>();
    }

    public async Task<LoginResult> LoginRefreshTokenAsync(string refreshToken)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/auth/refresh");
        request.Content = JsonContent.Create(new { refresh_token = refreshToken });
        var response = await _httpClient.SendAsync(request);
        if (!response.IsSuccessStatusCode)
        {
            var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
            return new LoginResult() { Error = error?.detail };
        }
        return await response.Content.ReadFromJsonAsync<LoginResult>();
    }

    public async Task<JsonElement> GetAllUsersAsync(string token)
    {
        var request = new HttpRequestMessage(HttpMethod.Get, "/admin/users");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> AdminDeleteUserAsync(string token, string userId)
    {
        var request = new HttpRequestMessage(HttpMethod.Delete, $"/admin/delete-user/{userId}");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> ModifyMailService(string token, string mailUsername, string mailPassword,
        string mailFrom, int mailPort, string mailServer, bool mailStartttls, bool mailSslTls)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/modify-mail");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        request.Content = JsonContent.Create(new
        {
            mail_username = mailUsername,
            mail_password = mailPassword,
            mail_from = mailFrom,
            mail_port = mailPort,
            mail_server = mailServer,
            mail_startttls = mailStartttls,
            mail_ssl_tls = mailSslTls,
        });
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> DeleteMailServiceAsync(string token)
    {
        var request = new HttpRequestMessage(HttpMethod.Delete, $"/remove-mail");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }
    
    public async Task<JsonElement> RegisterOidcProviderAsync(
        string token,
        string name,
        string clientId,
        string clientSecret,
        string metadataUrl,
        string scope = "openid email profile")
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/oidc/register");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        request.Content = JsonContent.Create(new
        {
            name,
            client_id = clientId,
            client_secret = clientSecret,
            metadata_url = metadataUrl,
            scope
        });

        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        return result;
    }

    public async Task<JsonElement> RemoveOidcProvider(string token, string oidcProviderId)
    {
        var request =  new HttpRequestMessage(HttpMethod.Delete, $"/oidc/remove");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        request.Content = JsonContent.Create(new
        {
            oidc_provider = oidcProviderId,
        });
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<byte[]> SetupMfa(string token)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/mfa/setup");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsByteArrayAsync();
    }

    public async Task<JsonElement> VerifyMfa(string token, string mfaCode)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "mfa/verify");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        request.Content = JsonContent.Create(new
        {
            code = mfaCode
        });
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> RequestPasswordReset(string email)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/auth/reset-request");
        request.Content = JsonContent.Create(new
        {
            email
        });
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> ResetPassword(string email, string password, string code)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/auth/password-reset");
        request.Content = JsonContent.Create(new
        {
            email,
            code,
            password
        });
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> DisableMfa(string token, string code)
    {
        var request = new HttpRequestMessage(HttpMethod.Delete, "/mfa/disable");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        request.Content = JsonContent.Create(new
        {
            code
        });
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> LoginWithOidc(string provider)
    {
        if (string.IsNullOrWhiteSpace(provider))
            throw new ArgumentException("Provider is required.", nameof(provider));


        var allowedProviders = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "google",
            "auth0",
            "azuread"
        };

        if (!allowedProviders.Contains(provider))
            throw new InvalidOperationException($"Unsupported provider: {provider}");

        using var cts = new CancellationTokenSource(TimeSpan.FromMinutes(3));
        using var listener = new HttpListener();

        const string redirectUri = "http://localhost:8080/callback/";
        listener.Prefixes.Add(redirectUri);

        try
        {
            listener.Start();
        }
        catch (HttpListenerException ex)
        {
            throw new InvalidOperationException(
                "Could not start local callback listener. Port 8080 may already be in use.",
                ex);
        }

        // Ask backend for login URL
        using var response = await _httpClient.GetAsync($"/oidc/login-url/{provider}", cts.Token);
        response.EnsureSuccessStatusCode();

        var urlData = await response.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: cts.Token);
        if (!urlData.TryGetProperty("url", out var urlProp))
            throw new InvalidOperationException("Login URL was not returned by the server.");

        string? loginUrl = urlProp.GetString();
        if (string.IsNullOrWhiteSpace(loginUrl))
            throw new InvalidOperationException("Login URL is empty.");

        Process.Start(new ProcessStartInfo(loginUrl) { UseShellExecute = true });

        HttpListenerContext context;
        try
        {
            var getContextTask = listener.GetContextAsync();
            var completed = await Task.WhenAny(getContextTask, Task.Delay(Timeout.Infinite, cts.Token));

            if (completed != getContextTask)
                throw new TimeoutException("Login timed out.");

            context = await getContextTask;
        }
        catch (OperationCanceledException)
        {
            throw new TimeoutException("Login timed out.");
        }

        string? accessToken = context.Request.QueryString["access_token"];
        string? error = context.Request.QueryString["error"];

        string responseHtml;

        if (!string.IsNullOrEmpty(error))
        {
            responseHtml = "<html><body><h2>Login failed.</h2><p>You can close this window.</p></body></html>";
            byte[] errorBytes = System.Text.Encoding.UTF8.GetBytes(responseHtml);
            context.Response.StatusCode = 400;
            context.Response.ContentType = "text/html; charset=utf-8";
            context.Response.ContentLength64 = errorBytes.Length;
            await context.Response.OutputStream.WriteAsync(errorBytes);
            context.Response.Close();

            throw new InvalidOperationException($"OIDC login failed: {error}");
        }

        if (string.IsNullOrWhiteSpace(accessToken))
        {
            responseHtml =
                "<html><body><h2>Login failed.</h2><p>No access token was returned. You can close this window.</p></body></html>";
            byte[] failBytes = System.Text.Encoding.UTF8.GetBytes(responseHtml);
            context.Response.StatusCode = 400;
            context.Response.ContentType = "text/html; charset=utf-8";
            context.Response.ContentLength64 = failBytes.Length;
            await context.Response.OutputStream.WriteAsync(failBytes);
            context.Response.Close();

            throw new InvalidOperationException("No access token was returned in the callback.");
        }

        responseHtml =
            "<html><body><h2>Login successful.</h2><p>You can close this window and return to the app.</p></body></html>";
        byte[] successBytes = System.Text.Encoding.UTF8.GetBytes(responseHtml);
        context.Response.StatusCode = 200;
        context.Response.ContentType = "text/html; charset=utf-8";
        context.Response.ContentLength64 = successBytes.Length;
        await context.Response.OutputStream.WriteAsync(successBytes);
        context.Response.Close();

        return JsonSerializer.SerializeToElement(new
        {
            access_token = accessToken
        });
    }
}
