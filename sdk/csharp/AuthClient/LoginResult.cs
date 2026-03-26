using System.Text.Json.Serialization;

namespace AuthClient;

public class LoginResult
{
    [JsonPropertyName("access_token")]
    public string? AccessToken { get; set; }
    
    [JsonPropertyName("mfa_required")]
    public bool MfaRequired { get; set; }
    
    [JsonPropertyName("user_id")]
    public string? UserId { get; set; }
    public string? Error { get; set; }
    
    public bool IsSuccess => AccessToken is not null;
    public bool HasError => Error is not null;
}