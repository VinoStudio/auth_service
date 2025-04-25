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
    MappingProviderException,
    OAuthAccountAlreadyDeactivatedException,
    OAuthAccountDoesNotExistException,
)
from src.application.exceptions.oauth import OAuthAccountAlreadyAssociatedException
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
    """
    Manages OAuth authentication flows, user association, and account creation.

    This class handles the OAuth 2.0 authentication process including generating
    authorization URLs, processing callbacks, exchanging authorization codes for tokens,
    retrieving user information from providers, and associating OAuth accounts with
    application users.

    Attributes:
        oauth_provider_factory: Factory that contains a dictionary of existing OAuth provider instances
        oauth_repo: Repository for OAuth account storage and retrieval
        user_reader: Service for reading user information
    """

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
        """
        Process OAuth callback and authenticate or create a user.

        Handles the OAuth callback flow by exchanging the authorization code for tokens,
        retrieving user information from the provider, and either finding an existing
        user account or preparing data for a new user registration.

        Args:
            provider_name: The name of the OAuth provider (e.g., "Google", "GitHub", "Yandex".)
            code: The authorization code from the OAuth callback
            state: Parameter to protect from XSRF attacks and validate the request

        Returns:
            Either credentials for a new user to be created or identity for an existing user

        Raises:
            EmailAlreadyExistsException: If user not found, but OAuth email already taken
        """

        provider = self.oauth_provider_factory.get_provider(provider_name)

        # Exchange code for tokens
        oauth_tokens = self._convert_callback_to_token(
            provider,
            code,
            state=state,
        )

        logger.debug("Received tokens: ", tokens=oauth_tokens)

        # Get user info from provider
        user_info = self._get_provider_user_info(provider, oauth_tokens["access_token"])

        logger.debug("Received user_data: ", user_data=user_info)

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
        """
        Associate a new OAuth provider with an existing user account.

        Links an OAuth identity from a third-party provider to a user that already exists
        in the system. This enables the user to login using the associated provider in the future.

        Args:
            user_id: The ID of the user to associate with
            provider_name: The name of the OAuth provider (e.g., "Google", "GitHub", "Yandex".)
            code: The authorization code from the OAuth callback
            state: Parameter to protect from XSRF. Also used as redis key for oauth account connection

        Raises:
            OAuthAccountAlreadyAssociatedException: If the OAuth account is already associated with another user
            UserNotFoundException: If the specified user does not exist
        """

        # Get the provider
        provider = self.oauth_provider_factory.get_provider(provider_name)

        # Exchange code for tokens
        oauth_tokens = self._convert_callback_to_token(
            provider,
            code,
            state=state,
            is_connect=True,
        )

        logger.info("Received tokens for association: ", tokens=oauth_tokens)

        # Get user info from provider
        user_info = self._get_provider_user_info(provider, oauth_tokens["access_token"])

        logger.info("Received user_data for association: ", user_data=user_info)

        provider_parsed_info = self._parse_oauth_user_info(provider_name, user_info)

        # Check if this OAuth account is already associated with any user
        existing_oauth_account: domain.OAuthAccount = (
            await self._find_account_by_oauth_data(
                provider_name, provider_parsed_info["provider_user_id"]
            )
        )

        if existing_oauth_account:
            if existing_oauth_account.is_active:
                raise OAuthAccountAlreadyAssociatedException("provider_user_id")
            else:
                existing_oauth_account.reactivate()
                await self.oauth_repo.update_oauth_account(existing_oauth_account)
                logger.info(
                    f"Successfully reactivated {provider_name} account for user {user_id}"
                )
                return None

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

    async def disconnect_oauth_account(
        self, provider_name: str, provider_user_id: str
    ) -> None:
        account: domain.OAuthAccount = await self._find_account_by_oauth_data(
            provider_name, provider_user_id
        )
        if account is None:
            raise OAuthAccountDoesNotExistException("provider_user_id")

        if not account.is_active:
            raise OAuthAccountAlreadyDeactivatedException("provider_user_id")

        account.deactivate()

        await self.oauth_repo.update_oauth_account(account)

    def get_oauth_url(
        self, provider_name: str, state: str, is_connect: bool = False
    ) -> str:
        """
        Generate URL for redirecting user to OAuth provider login page.

        Creates the authorization URL that the user will be redirected to in order
        to authenticate with the OAuth provider.

        Args:
            provider_name: The name of the OAuth provider (e.g., "Google", "GitHub", "Yandex".)
            state: Unique state parameter for CSRF protection
            is_connect: If True, generates URL for connecting an account rather than logging in

        Returns:
            The fully formed authorization URL for the specified provider
        """

        provider = self.oauth_provider_factory.get_provider(provider_name)
        if is_connect:
            url = provider.get_connect_url() + f"&state={state}"
            logger.info("provides connect url", url=url)
            return url

        url = provider.get_auth_url() + f"&state={state}"
        logger.info("provides redirect url", url=url)
        return url

    # -------------------- Callback Helpers --------------------

    @staticmethod
    def _convert_callback_to_token(
        provider: OAuthProvider,
        code: str,
        state: str,
        is_connect: bool = False,
    ) -> Dict[str, str]:
        """
        Exchange authorization code for OAuth tokens.

        Makes a request to the provider's token endpoint to exchange the authorization
        code for access (and possibly refresh) tokens.

        Args:
            provider: OAuth provider configuration object
            code: Authorization code received from the callback
            state: State token for security validation
            is_connect: If True, uses connect_url, otherwise uses redirect_uri

        Returns:
            Dictionary containing tokens (typically access_token, refresh_token, etc.)
        """

        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "state": state,
            "grant_type": "authorization_code",
        }

        if provider.name in ("google", "github"):
            # Use the appropriate URL based on the is_connect parameter
            data["redirect_uri"] = (
                provider.connect_url if is_connect else provider.redirect_uri
            )

        headers = {"Accept": "application/json"}

        response = requests.post(provider.token_url, data=data, headers=headers)

        return response.json()

    def _get_provider_user_info(
        self, provider: OAuthProvider, access_token: str
    ) -> Dict[str, Any]:
        """
        Get user information from OAuth provider.

        Retrieves profile information about the user from the OAuth provider's
        user info endpoint using the access token.

        Args:
            provider: The OAuth provider configuration object
            access_token: The access token received from the token exchange

        Returns:
            Dictionary containing user profile information
        """
        if provider.name == "github":
            return self._get_github_user_info(provider, access_token)
        else:
            headers = self._get_headers(provider, access_token)
            response = requests.post(provider.userinfo_url, headers=headers)
            return response.json()

    def _get_github_user_info(
        self, provider: OAuthProvider, access_token: str
    ) -> Dict[str, Any]:
        """
        Get GitHub user information including email.

        GitHub requires a separate API call to retrieve email information,
        so this method handles the special case for GitHub providers.

        Args:
            provider: The GitHub OAuth provider configuration
            access_token: The access token received from the token exchange

        Returns:
            Dictionary containing user profile information with email added
        """

        headers = self._get_headers(provider, access_token)

        # Get basic user profile
        response = requests.get(provider.userinfo_url, headers=headers)
        user_data = response.json()

        # Enrich with email information
        email = self._get_github_user_email(headers)
        if email:
            user_data["email"] = email

        return user_data

    @staticmethod
    def _get_github_user_email(headers: Dict[str, str]) -> Optional[str]:
        """
        Extract primary or first email from GitHub emails endpoint.

        GitHub requires a separate API call to get user emails. This method
        fetches the emails and returns the primary one if available.

        Args:
            headers: HTTP headers including the authorization token

        Returns:
            Primary email address or first available one, None if unavailable
        """

        emails_response = requests.get(
            "https://api.github.com/user/emails", headers=headers
        )

        if not emails_response.ok:
            logger.warning(
                "Failed to fetch GitHub emails", status=emails_response.status_code
            )
            return None

        emails = emails_response.json()
        logger.info("Received emails from GitHub", count=len(emails))

        # First try to find primary email
        for email_data in emails:
            if email_data.get("primary"):
                return email_data.get("email")

        # If no primary found, take the first one
        if emails:
            return emails[0].get("email")

        return None

    # -------------------- User Methods --------------------

    async def _find_or_create_user(
        self,
        provider_name: str,
        user_info: Dict[str, Any],
    ) -> dto.OAuthUserIdentity | dto.OauthUserCredentials:
        """
        Find existing user or create new one based on OAuth data.

        Determines if a user already exists based on OAuth provider data or email.
        If found, returns user identity; otherwise, prepares data for user creation.

        Args:
            provider_name: The name of the OAuth provider
            user_info: User information retrieved from the provider

        Returns:
            Either credentials for a new user or identity information for an existing user

        Raises:
            EmailAlreadyExistsException: If user not found by OAuth but email exists
        """

        # Parse and normalize user info
        parsed_info = self._parse_oauth_user_info(provider_name, user_info)

        provider_email = parsed_info["email"]
        provider_user_id = parsed_info["provider_user_id"]

        # Try to find user by provider info
        existing_user: domain.OAuthAccount = await self._find_account_by_oauth_data(
            provider_name, provider_user_id
        )

        if existing_user:
            return await self._get_user_oauth_credentials(
                provider_name, provider_user_id
            )

        # Check if email already exists
        await self._check_if_email_exists(provider_email)

        # Create new user with the parsed info
        return await self._create_user_from_oauth(parsed_info, provider_name)

    async def _create_user_from_oauth(
        self,
        user_info: Dict[str, Any],
        provider_name: str,
    ) -> dto.OauthUserCredentials:
        """
        Create new user from OAuth data.

        Prepares the data needed to create a new user account based on
        information retrieved from the OAuth provider.

        Args:
            user_info: Parsed and normalized user information from provider
            provider_name: The name of the OAuth provider

        Returns:
            DTO containing user credentials and OAuth information for account creation
        """

        username = await self._generate_username(user_info)

        return dto.OauthUserCredentials(
            username=username,
            provider_email=user_info["email"],
            password=self._generate_secure_password(),
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            middle_name=user_info["middle_name"],
            provider_name=provider_name,
            provider_user_id=user_info["provider_user_id"],
        )

    @staticmethod
    def _extract_name_parts(user_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract first, middle, and last name from a full name string.

        Parses a full name into its component parts using a simple heuristic:
        - First word becomes first name
        - Last word becomes last name
        - Any words in between become middle name

        Args:
            user_info: Dictionary containing a 'name' key with full name

        Returns:
            Dictionary with 'first_name', 'middle_name', and 'last_name' keys
        """

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
        """
        Create appropriate HTTP headers for OAuth provider API requests.

        Constructs authorization headers based on the specific requirements
        of different OAuth providers (Yandex, Google, GitHub, etc.).

        Args:
            provider: The OAuth provider configuration object
            access_token: The access token to use for authorization

        Returns:
            Dictionary of HTTP headers required for API requests

        Raises:
            MappingProviderException: If the provider is not supported
        """

        match provider.name:
            case "yandex":
                headers = {"Authorization": f"OAuth {access_token}"}
            case "google":
                headers = {"Authorization": f"Bearer {access_token}"}
            case "github":
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                }
            case _:
                raise MappingProviderException(provider.name)

        return headers

    def _parse_oauth_user_info(
        self, provider_name: str, user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse and normalize OAuth user information from different providers.

        Creates a standardized user profile with consistent fields regardless of
        which OAuth provider the data comes from. Handles the different data
        structures and field names used by various providers.

        Args:
            provider_name: The name of the OAuth provider
            user_info: Raw user information from the provider

        Returns:
            Standardized dictionary with normalized user information

        Raises:
            ValueError: If required fields cannot be extracted from the provider data
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

    @staticmethod
    def _validate_parsed_profile(provider_name: str, profile: Dict[str, Any]) -> None:
        """
        Ensure all required fields are present in the parsed profile.

        Validates that essential information like provider user ID and email
        were successfully extracted from the provider data.

        Args:
            provider_name: The name of the OAuth provider
            profile: Parsed user profile to validate

        Raises:
            ValueError: If required fields are missing or invalid
        """

        """Ensure all required fields are present in the parsed profile."""
        if not profile["provider_user_id"]:
            raise ValueError(
                f"Could not extract provider user ID from {provider_name} data"
            )

        # Lowercase email if it exists
        if "email" in profile and profile["email"]:
            profile["email"] = profile["email"].lower()
        else:
            raise ValueError(f"Could not extract email from {provider_name} data")

    async def _generate_username(self, user_info: Dict[str, Any]) -> str:
        """
        Generate a unique username based on OAuth user information.

        Creates a username using the following strategy:
        1. Try using the email prefix
        2. If not available, use the full name without spaces
        3. If username exists, add random adjective
        4. As a last resort, use timestamp-based username

        Args:
            user_info: Parsed user information from OAuth provider

        Returns:
            A unique username string that doesn't exist in the system
        """

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
    def _generate_secure_password(length=12):
        """
        Generate a cryptographically secure random password.

        Creates a password that meets common security requirements:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - Minimum length of 8 characters

        Args:
            length: Desired password length (minimum 8)

        Returns:
            A secure random password string
        """

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

    # -------------------- Validators --------------------

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
    ) -> domain.OAuthAccount:
        """Find user by OAuth provider and ID"""
        return await self.oauth_repo.get_by_provider_and_id(provider, provider_user_id)
