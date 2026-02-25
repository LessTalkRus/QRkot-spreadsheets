from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

from app.core.config import settings
from app.core.constants import DRIVE_URL, SPREADSHEET_URL

SCOPES = [
    SPREADSHEET_URL,
    DRIVE_URL
]

INFO = dict(
    type=settings.type,
    project_id=settings.project_id,
    private_key_id=settings.private_key_id,
    private_key=settings.private_key,
    client_id=settings.client_id,
    client_email=settings.client_email,
    auth_uri=settings.auth_uri,
    token_uri=settings.token_uri,
    auth_provider_x509_cert_url=settings.auth_provider_x509_cert_url,
    client_x509_cert_url=settings.client_x509_cert_url,
)

CREDENTIALS = ServiceAccountCreds(scopes=SCOPES, **INFO)


async def get_service():
    async with Aiogoogle(service_account_creds=CREDENTIALS) as aiogoogle:
        yield aiogoogle