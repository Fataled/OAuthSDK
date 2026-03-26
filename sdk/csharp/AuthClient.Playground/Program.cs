// See https://aka.ms/new-console-template for more information

var client = new AuthClient.AuthClient("http://159.203.18.252:8002");

var login = await client.LoginAsync("Test1@test.com", "1");
Console.WriteLine(login);
