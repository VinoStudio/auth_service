import structlog
import requests
import random
import string
import src.domain as domain
import src.application.dto as dto

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Dict, Any

from src.infrastructure.base.repository import BaseUserReader
from src.settings.config import OAuthProvider

logger = structlog.getLogger(__name__)


@dataclass
class OAuthProviderFactory:
    providers: Dict[str, OAuthProvider]

    def get_provider(self, provider_name: str) -> OAuthProvider:
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider_name}")
        return self.providers[provider_name]


@dataclass
class OAuthManager:
    oauth_provider_factory: OAuthProviderFactory
    user_reader: BaseUserReader

    # -------------------- Oauth Operations --------------------

    async def handle_oauth_callback(
        self, provider_name: str, code: str
    ) -> dto.OauthUserCredentials:
        """Process OAuth callback, create user if needed, and return tokens"""
        provider = self.oauth_provider_factory.get_provider(provider_name)

        # Exchange code for tokens
        oauth_tokens = self._convert_callback_to_token(provider, code)

        logger.info("Received tokens: ", tokens=oauth_tokens)

        # Get user info from provider
        user_info = self._get_provider_user_info(provider, oauth_tokens["access_token"])

        logger.info("Received user_data: ", user_data=user_info)

        # Find or create user in our system
        user = await self._find_or_create_user(user_info)

        return user

    def get_oauth_login_url(self, provider_name: str, state: str) -> str:
        """Generate URL for redirecting user to OAuth provider login page"""
        provider = self.oauth_provider_factory.get_provider(provider_name)
        url = provider.get_auth_url()  # + "&" + state
        logger.info("provides redirect url", url=url)
        return url

    # -------------------- Callback Helpers --------------------

    @staticmethod
    def _convert_callback_to_token(
        provider: OAuthProvider, code: str
    ) -> Dict[str, str]:
        """Exchange authorization code for OAuth tokens"""
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "redirect_uri": provider.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(provider.token_url, data=data)

        return response.json()

    @staticmethod
    def _get_provider_user_info(
        provider: OAuthProvider, access_token: str
    ) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(provider.userinfo_url, headers=headers)

        return response.json()

    # -------------------- User Methods --------------------

    async def _find_or_create_user(
        self,
        user_info: Dict[str, Any],
    ) -> domain.User | dto.OauthUserCredentials:
        """Find existing user or create new one based on OAuth data"""
        # Extract email
        email = user_info.get("email")
        if not email:
            raise ValueError("Email not provided by OAuth provider")

        # Try to find user by email
        if user := await self._check_if_user_exist_by_email(email):
            # user = await self._update_user_if_needed(user, user_info)
            return user

        # Create new user
        return await self._create_user_from_oauth(user_info, email)

    async def _create_user_from_oauth(
        self, user_info: Dict[str, Any], email: str
    ) -> dto.OauthUserCredentials:
        """Create new user from OAuth data"""
        username = await self._generate_username(user_info)
        name_data = self._extract_name_parts(user_info)

        return dto.OauthUserCredentials(
            username=username,
            email=email,
            password=self.generate_secure_password(),
            first_name=name_data["first_name"],
            last_name=name_data["last_name"],
            middle_name=name_data["middle_name"],
        )

    @staticmethod
    def _extract_name_parts(user_info: Dict[str, Any]) -> Dict[str, str]:
        """Extract name parts from user info"""
        first_name = ""
        middle_name = ""
        last_name = ""

        if user_info.get("name"):
            name_parts = user_info.get("name").split()
            if len(name_parts) >= 1:
                first_name = name_parts[0]
            if len(name_parts) == 2:
                last_name = name_parts[1]
            elif len(name_parts) >= 3:
                middle_name = name_parts[1]
                last_name = " ".join(name_parts[2:])

        return {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
        }

    # -------------------- Helpers Methods --------------------

    async def _generate_username(self, user_info: Dict[str, Any]) -> str:
        """Generate beautiful unique username from OAuth user info"""

        username = "user"

        if user_info.get("email"):
            username = user_info["email"].split("@")[0]

        elif user_info.get("name"):
            username = user_info["name"].lower().replace(" ", "")

        # Check if base username exists
        if not await self._check_if_username_exists(username):
            return username

        adjectives = ["happy", "clever", "bright", "swift", "calm", "kind"]
        nouns = ["dolphin", "falcon", "panda", "tiger", "wolf", "eagle"]

        username = f"{username}_{random.choice(adjectives)}_{random.choice(nouns)}"

        if not await self._check_if_username_exists(username):
            return username

        # Papa Roach: Last Resort :)
        return f"user_{datetime.now(UTC).timestamp()}"

    @staticmethod
    def generate_secure_password(length=12):
        # Make sure length is at least 8
        length = max(length, 8)

        # Create base password with minimum requirements
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
        ]

        # Add remaining characters
        remaining_length = length - len(password)
        chars = string.ascii_letters + string.digits
        password.extend(random.choice(chars) for _ in range(remaining_length))

        # Shuffle the password
        random.shuffle(password)

        return "".join(password)

    async def _check_if_username_exists(self, username: str) -> bool:
        return await self.user_reader.check_username_exists(username)

    async def _check_if_user_exist_by_email(self, email: str) -> domain.User | None:
        if await self.user_reader.check_email_exists(email):
            return await self.user_reader.get_user_by_email(email)
