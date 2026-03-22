import httpx

class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def register(self, email: str, password: str, name:str) -> dict:

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/register", json={
                "email": email,
                "password": password,
                "name": name
            })
            response.raise_for_status()
            return response.json()

    async def login(self, email: str, password: str, totp_code: str = None) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/login", json={
                "email": email,
                "password": password,
                "totp_code": totp_code
            })
            response.raise_for_status()
            return response.json()

    async def logout(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/logout", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return response.json()

    async def get_user(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/me", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return response.json()
