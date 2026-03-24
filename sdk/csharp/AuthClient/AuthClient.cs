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

    public async Task<JsonElement> LoginAsync(string email, string password, string? totpCode = null)
    {
        // Login and return the JWT, optionally with MFA code
        var response = await _httpClient.PostAsJsonAsync("/login", new
        {
            email,
            password,
            totp_code = totpCode
        });
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
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

    public async Task<JsonElement> DeleteUserAsync(string token)
    {
        var request = new HttpRequestMessage(HttpMethod.Delete, "/delete");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
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

    public async Task<JsonElement> LoginWithOidc(string provider)
    {
        var response = await _httpClient.GetAsync($"/oidc/login-url/{provider}");
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
    
}
