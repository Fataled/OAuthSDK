using System.Text.Json.Serialization;

namespace AuthClient;

public class RefreshTokenResponse
{   
    [JsonPropertyName("refresh_token")]
    public string? RefreshToken { get; set; }
    public string? Error { get; set; }
}