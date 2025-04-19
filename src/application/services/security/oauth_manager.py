import structlog
import requests
import random
import string
import src.domain as domain
import src.application.dto as dto

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Dict, Any, Optional

from src.application.exceptions import (
    EmailAlreadyExistsException,
    UserNotFoundException,
    MappingProviderException,
)
from src.infrastructure.base.repository import BaseUserReader
from src.infrastructure.repositories.oauth.oauth_repo import OAuthAccountRepository
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
    oauth_repo: OAuthAccountRepository
    user_reader: BaseUserReader

    # -------------------- Oauth Operations --------------------

    async def handle_oauth_callback(
        self,
        provider_name: str,
        code: str,
        state: str,
    ) -> dto.OauthUserCredentials | dto.OAuthUserIdentity:
        """Process OAuth callback, create user if needed, and return tokens"""
        provider = self.oauth_provider_factory.get_provider(provider_name)

        # Exchange code for tokens
        oauth_tokens = self._convert_callback_to_token(
            provider,
            code,
            state=state,
        )

        logger.info("Received tokens: ", tokens=oauth_tokens)

        # Get user info from provider
        user_info = self._get_provider_user_info(provider, oauth_tokens["access_token"])

        logger.info("Received user_data: ", user_data=user_info)

        # Find or create user in our system
        result = await self._find_or_create_user(provider_name, user_info)

        return result

    async def associate_oauth_with_existing_user(
        self,
        user_id: str,
        provider_name: str,
        code: str,
        state: str,
    ) -> None:
        """Associate a new OAuth provider with an existing user account

        Args:
            user_id: The ID of the user to associate with
            provider_name: The name of the OAuth provider
            code: The authorization code from the OAuth callback

        Raises:
            ValueError: If the OAuth account is already associated with another user
            UserNotFoundException: If the user does not exist
        """
        # Get the provider
        provider = self.oauth_provider_factory.get_provider(provider_name)

        # Exchange code for tokens
        oauth_tokens = self._convert_connect_callback_to_token(
            provider,
            code,
            state=state,
        )

        logger.info("Received tokens for association: ", tokens=oauth_tokens)

        # Get user info from provider
        user_info = self._get_provider_user_info(provider, oauth_tokens["access_token"])

        logger.info("Received user_data for association: ", user_data=user_info)

        provider_parsed_info = self._parse_oauth_user_info(provider_name, user_info)

        # Check if this OAuth account is already associated with any user
        existing_user = await self._find_account_by_oauth_data(
            provider_name, provider_parsed_info["provider_user_id"]
        )

        if existing_user:
            raise ValueError(f"OAuth account is already associated with user {user_id}")

        associated_account = domain.OAuthAccount(
            user_id=user_id,
            provider=provider_name,
            provider_user_id=provider_parsed_info["provider_user_id"],
            provider_email=provider_parsed_info["email"].lower(),
        )
        # Create the OAuth account association
        await self.oauth_repo.create_oauth_account(associated_account)

        logger.info(
            f"Successfully associated {provider_name} account with user {user_id}"
        )

    def get_oauth_login_url(self, provider_name: str, state: str) -> str:
        """Generate URL for redirecting user to OAuth provider login page"""
        provider = self.oauth_provider_factory.get_provider(provider_name)
        url = provider.get_auth_url() + f"&state={state}"
        logger.info("provides redirect url", url=url)
        return url

    def get_oauth_connect_url(self, provider_name: str, state: str) -> str:
        """Generate URL for redirecting user to OAuth provider login page"""
        provider = self.oauth_provider_factory.get_provider(provider_name)
        url = provider.get_connect_url() + f"&state={state}"
        logger.info("provides connect url", url=url)
        return url

    # -------------------- Callback Helpers --------------------

    @staticmethod
    def _convert_callback_to_token(
        provider: OAuthProvider,
        code: str,
        state: str,
    ) -> Dict[str, str]:
        """Exchange authorization code for OAuth tokens"""
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "state": state,
            "grant_type": "authorization_code",
        }

        if provider.name == "google":
            data["redirect_uri"] = provider.redirect_uri

        response = requests.post(provider.token_url, data=data)

        return response.json()

    @staticmethod
    def _convert_connect_callback_to_token(
        provider: OAuthProvider,
        code: str,
        state: str,
    ) -> Dict[str, str]:
        """Exchange authorization code for OAuth tokens"""
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "state": state,
            "grant_type": "authorization_code",
        }

        if provider.name == "google":
            data["redirect_uri"] = provider.connect_url

        response = requests.post(provider.token_url, data=data)

        return response.json()

    def _get_provider_user_info(
        self, provider: OAuthProvider, access_token: str
    ) -> Dict[str, Any]:
        """Get user information from OAuth provider"""

        headers = self._get_headers(provider, access_token)

        response = requests.post(provider.userinfo_url, headers=headers)

        return response.json()

    # -------------------- User Methods --------------------

    async def _find_or_create_user(
        self,
        provider_name: str,
        user_info: Dict[str, Any],
    ) -> dto.OAuthUserIdentity | dto.OauthUserCredentials:
        """Find existing user or create new one based on OAuth data"""
        # Parse and normalize user info
        parsed_info = self._parse_oauth_user_info(provider_name, user_info)

        provider_email = parsed_info["email"]
        provider_user_id = parsed_info["provider_user_id"]

        await self._check_if_email_exists(provider_email)

        # Try to find user by provider info
        existing_user = await self._find_account_by_oauth_data(
            provider_name, provider_user_id
        )

        if existing_user:
            return await self._get_user_oauth_credentials(
                provider_name, provider_user_id
            )

        # Create new user with the parsed info
        return await self._create_user_from_oauth(parsed_info, provider_name)

    async def _create_user_from_oauth(
        self,
        user_info: Dict[str, Any],
        provider_name: str,
    ) -> dto.OauthUserCredentials:
        """Create new user from OAuth data"""
        username = await self._generate_username(user_info)

        return dto.OauthUserCredentials(
            username=username,
            provider_email=user_info["email"].lower(),
            password=self.generate_secure_password(),
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            middle_name=user_info["middle_name"],
            provider_name=provider_name,
            provider_user_id=user_info["provider_user_id"],
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

    @staticmethod
    def _get_headers(provider: OAuthProvider, access_token: str) -> Dict[str, str]:
        match provider.name:
            case "yandex":
                headers = {"Authorization": f"OAuth {access_token}"}
            case "google":
                headers = {"Authorization": f"Bearer {access_token}"}
            case "github":
                headers = {"Authorization": f"Bearer {access_token}"}
            case _:
                raise MappingProviderException(provider.name)

        return headers

    def _parse_oauth_user_info(
        self, provider_name: str, user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse and normalize OAuth user information from different providers.

        Returns a standardized user profile with consistent fields across providers.
        """
        # Initialize with default empty structure
        parsed_profile = {
            "provider_user_id": None,
            "email": None,
            "name": None,
            "first_name": None,
            "middle_name": None,
            "last_name": None,
            "additional_data": {},
        }

        # Select provider-specific parser
        match provider_name:
            case "google":
                self._parse_google_user_info(user_info, parsed_profile)
            case "yandex":
                self._parse_yandex_user_info(user_info, parsed_profile)
            case "github":
                self._parse_github_user_info(user_info, parsed_profile)
            case _:
                self._parse_generic_user_info(provider_name, user_info, parsed_profile)

        # Ensure required fields are present
        self._validate_parsed_profile(provider_name, parsed_profile)
        return parsed_profile

    def _parse_google_user_info(
        self, user_info: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Extract user information from Google OAuth response."""
        result["provider_user_id"] = user_info.get("sub")
        result["email"] = user_info.get("email")
        result["name"] = user_info.get("name")
        result["first_name"] = user_info.get("given_name")
        result["last_name"] = user_info.get("family_name")

        # Fill in missing name parts if we have the full name
        if result["name"] and (not result["first_name"] or not result["last_name"]):
            self._fill_missing_name_parts(result)

    def _parse_yandex_user_info(
        self, user_info: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Extract user information from Yandex OAuth response."""

        result["provider_user_id"] = user_info.get("id")
        result["email"] = user_info.get("default_email")

        # Fallback to first email in the list if default isn't available
        if not result["email"] and user_info.get("emails"):
            result["email"] = user_info["emails"][0]

        result["name"] = user_info.get("real_name")
        result["first_name"] = user_info.get("first_name")
        result["last_name"] = user_info.get("last_name")

        # Store additional useful information
        result["additional_data"].update(
            {
                "login": user_info.get("login"),
                "display_name": user_info.get("display_name"),
            }
        )

    def _parse_github_user_info(
        self, user_info: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Extract user information from GitHub OAuth response."""
        result["provider_user_id"] = str(user_info.get("id"))
        result["email"] = user_info.get("email")
        result["name"] = user_info.get("name")
        result["additional_data"]["login"] = user_info.get("login")

        # GitHub typically only provides full name, so parse it
        if result["name"]:
            self._fill_missing_name_parts(result)

    def _parse_generic_user_info(
        self, provider_name: str, user_info: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Generic parser for unknown providers using common field patterns."""
        logger.warning(f"Unknown provider: {provider_name}, attempting generic parsing")

        # Try common field names for essential information
        result["provider_user_id"] = str(
            user_info.get("id") or user_info.get("sub") or ""
        )
        result["email"] = user_info.get("email")
        result["name"] = user_info.get("name")

        # Try common name field patterns
        result["first_name"] = user_info.get("first_name") or user_info.get(
            "given_name"
        )
        result["last_name"] = user_info.get("last_name") or user_info.get("family_name")

        # If we have a name but not its parts, try to extract them
        if result["name"] and (not result["first_name"] or not result["last_name"]):
            self._fill_missing_name_parts(result)

    def _fill_missing_name_parts(self, profile: Dict[str, Any]) -> None:
        """Extract name parts from full name when parts are missing."""
        name_parts = self._extract_name_parts({"name": profile["name"]})

        if not profile["first_name"]:
            profile["first_name"] = name_parts["first_name"]

        if not profile["middle_name"]:
            profile["middle_name"] = name_parts["middle_name"]

        if not profile["last_name"]:
            profile["last_name"] = name_parts["last_name"]

    def _validate_parsed_profile(
        self, provider_name: str, profile: Dict[str, Any]
    ) -> None:
        """Ensure all required fields are present in the parsed profile."""
        if not profile["provider_user_id"]:
            raise ValueError(
                f"Could not extract provider user ID from {provider_name} data"
            )

        if not profile["email"]:
            raise ValueError(f"Could not extract email from {provider_name} data")

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

    async def _get_user_oauth_credentials(
        self, provider: str, provider_user_id: str
    ) -> dto.OAuthUserIdentity:
        return await self.user_reader.get_user_credentials_by_oauth_provider(
            provider, provider_user_id
        )

    async def _check_if_username_exists(self, username: str) -> bool:
        return await self.user_reader.check_username_exists(username)

    async def _check_if_email_exists(self, email: str) -> None:
        if await self.user_reader.check_email_exists(email):
            raise EmailAlreadyExistsException(email)

    async def _find_account_by_oauth_data(
        self, provider: str, provider_user_id: str
    ) -> bool:
        """Find user by OAuth provider and ID"""
        return await self.oauth_repo.check_if_oauth_account_exists(
            provider, provider_user_id
        )
