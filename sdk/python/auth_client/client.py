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

    async def delete_user(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/delete", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return response.json()

    async def get_all_users(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/admin/users", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return response.json()

    async def admin_delete_user(self, token: str, user_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/admin/delete-user/{user_id}", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            return response.json()