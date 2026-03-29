using System.Text.Json.Serialization;

namespace AuthClient;

public class ConfirmationResponse
{
    [JsonPropertyName("message")]
    public string? Message { get; set; }
    
    
    public string? Detail { get; set; }
}