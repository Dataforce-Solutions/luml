from urllib.parse import urlencode

import httpx

from dataforce_studio.infra.exceptions import AuthError
from dataforce_studio.schemas.auth import UserInfo
from dataforce_studio.settings import config


class OAuthGoogleProvider:
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    @staticmethod
    def login_url() -> str:
        params = {
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    @staticmethod
    async def exchange_code_for_token(client: httpx.AsyncClient, code: str) -> str:
        data = {
            "code": code,
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response = await client.post(OAuthGoogleProvider.GOOGLE_TOKEN_URL, data=data)

        if response.status_code != 200:
            raise AuthError("Failed to retrieve token from Google", 400)

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise AuthError("Failed to retrieve access token", 400)

        return str(access_token)

    @staticmethod
    async def get_user_info(client: httpx.AsyncClient, access_token: str) -> UserInfo:
        response = await client.get(
            OAuthGoogleProvider.GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            raise AuthError("Failed to retrieve user info from Google", 400)

        result = response.json()

        return UserInfo(
            email=result.get("email"),
            full_name=result.get("name"),
            photo_url=result.get("picture"),
        )


class OAuthMicrosoftProvider:
    MICROSOFT_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"

    @staticmethod
    def _get_token_url() -> str:
        return f"https://login.microsoftonline.com/{config.MICROSOFT_TENANT}/oauth2/v2.0/token"

    @staticmethod
    def login_url() -> str:
        params = {
            "client_id": config.MICROSOFT_CLIENT_ID,
            "redirect_uri": config.MICROSOFT_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile User.Read",
        }
        auth_url = f"https://login.microsoftonline.com/{config.MICROSOFT_TENANT}/oauth2/v2.0/authorize"
        return auth_url + "?" + urlencode(params)

    @staticmethod
    async def exchange_code_for_token(client: httpx.AsyncClient, code: str) -> str:
        data = {
            "code": code,
            "client_id": config.MICROSOFT_CLIENT_ID,
            "client_secret": config.MICROSOFT_CLIENT_SECRET,
            "redirect_uri": config.MICROSOFT_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response = await client.post(OAuthMicrosoftProvider._get_token_url(), data=data)

        if response.status_code != 200:
            raise AuthError("Failed to retrieve token from Microsoft", 400)

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise AuthError("Failed to retrieve access token", 400)

        return str(access_token)

    @staticmethod
    async def get_user_info(client: httpx.AsyncClient, access_token: str) -> UserInfo:
        response = await client.get(
            OAuthMicrosoftProvider.MICROSOFT_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            raise AuthError("Failed to retrieve user info from Microsoft", 400)

        result = response.json()

        email = result.get("mail")

        if not email:
            other_mails = result.get("otherMails", [])
            email = other_mails[0] if other_mails else result.get("userPrincipalName")

        return UserInfo(
            email=email,
            full_name=result.get("displayName"),
            photo_url=None,
        )
