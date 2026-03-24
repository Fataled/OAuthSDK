// See https://aka.ms/new-console-template for more information

var client = new AuthClient.AuthClient("http://159.203.18.252:8002");

// Test register
var registerResult = await client.RegisterAsync("csharptest@test.com", "test123", "CSharp Test");
Console.WriteLine($"Register: {registerResult}");

var token = registerResult.GetProperty("access_token").GetString()!;

// Test get user
var user = await client.GetUserAsync(token);
Console.WriteLine($"Get user: {user}");

var mfaSetup = await client.SetupMfa(token);
Console.WriteLine($"Setup MFA: {mfaSetup}");

// Test logout
var logout = await client.LogoutAsync(token);
Console.WriteLine($"Logout: {logout}");