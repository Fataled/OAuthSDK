import asyncio
from auth_client import AuthClient

client = AuthClient("http://127.0.0.1:8000")

async def main():

    result = await client.register(
        email="sdkTest1@gmail.com",
        password="test123",
        name="SDK Test"
    )

    print("Registered: ", result)
    token = result["access_token"]

    user = await client.get_user(token=token)
    print("Get User: ", user)

    logout = await client.logout(token=token)
    print("Logout: ", logout)

asyncio.run(main())