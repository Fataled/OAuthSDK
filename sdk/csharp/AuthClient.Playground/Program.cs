// See https://aka.ms/new-console-template for more information

var client = new AuthClient.AuthClient("http://127.0.0.1:8000");

// Test register
var registerResult = await client.RegisterAsync("csharptest1@test.com", "test123", "CSharp Test");
Console.WriteLine($"Register: {registerResult}");

var token = registerResult.GetProperty("access_token").GetString()!;

// Test get user
var user = await client.GetUserAsync(token);
Console.WriteLine($"Get user: {user}");

// Test logout
var logout = await client.LogoutAsync(token);
Console.WriteLine($"Logout: {logout}");