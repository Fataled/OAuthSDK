from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

def create_openid_connect_client_registration(name: str, client_id: str, client_secret: str, server_metadata_url: str, client_kwargs:dict[str, str]):
    oauth.register(
        name=name,
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url=server_metadata_url,
        client_kwargs=client_kwargs
    )