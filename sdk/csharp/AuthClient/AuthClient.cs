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
        request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<JsonElement> GetUserAsync(string token)
    {
        // Get the current user from the JWT
        var request = new HttpRequestMessage(HttpMethod.Get, "/me");
        request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }
}
