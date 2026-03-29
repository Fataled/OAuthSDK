// See https://aka.ms/new-console-template for more information

var client = new AuthClient.AuthClient("http://159.203.18.252:8002");

var data = await client.LoginRefreshTokenAsync("");
Console.WriteLine($"{data}");
