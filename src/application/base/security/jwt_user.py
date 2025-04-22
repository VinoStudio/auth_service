from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Self, Dict, Any

import src.domain as domain
from src.application.dto import Token


class JWTUserInterface(ABC):
    """
    This class stores the essential security information about a user including their
    identity, roles, permissions, and security level. It's used for JWT token generation
    and validation throughout the authentication flow.
    """

    @abstractmethod
    def create_from_domain_user(self, domain_user: domain.User) -> Self:
        """
        Create a SecurityUser instance from a domain User object.

        Extracts JWT data from the domain user and creates a security user with
        essential authentication information.

        Args:
            domain_user: The domain user object containing JWT data

        Returns:
            SecurityUser: A new instance with user's security information

        Note:
            If JWT data is not already set on the domain user, it will be generated.
        """
        raise NotImplementedError

    @abstractmethod
    def create_from_jwt_data(
        self, jwt_data: bytes, device_id: str | None = None
    ) -> Self:
        """
        Create a SecurityUser instance from raw JWT data.

        Parses the byte-encoded JWT data and extracts user security information.

        Args:
            jwt_data: Raw JWT data in bytes format
            device_id: Optional device identifier

        Returns:
            SecurityUser: A new instance with the decoded user security information
        """
        raise NotImplementedError

    @abstractmethod
    def create_from_payload(self, payload: Dict[str, Any]) -> Self:
        """
        Create a SecurityUser instance from a dictionary payload.

        Extracts user security information from a dictionary, typically obtained
        from a decoded JWT token.

        Args:
            payload: Dictionary containing user security information
                    Must include 'sub', 'roles', 'lvl', 'device_id', and 'permissions' keys

        Returns:
            SecurityUser: A new instance with the user security information
        """
        raise NotImplementedError

    @abstractmethod
    def create_from_token_dto(self, token_dto: Token) -> Self:
        """
        Create a SecurityUser instance from a Token DTO.

        Extracts user security information from a Token data transfer object.

        Args:
            token_dto: Token object containing user security information

        Returns:
            SecurityUser: A new instance with the user security information
        """
        raise NotImplementedError

    @abstractmethod
    def set_device_id(self, device_id: str) -> None:
        """
        Set the device identifier for this security user.

        Args:
            device_id: The device identifier to set
        """
        raise NotImplementedError

    @abstractmethod
    def get_roles(self) -> List[str]:
        """
        Get the list of roles assigned to this user.

        Returns:
            List[str]: The user's role names
        """
        raise NotImplementedError

    @abstractmethod
    def get_permissions(self) -> List[str]:
        """
        Get the list of permissions granted to this user.

        Returns:
            List[str]: The user's permission names
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_identifier(self) -> str:
        """
        Get the unique identifier for this user.

        Returns:
            str: The user's ID
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_id(self) -> str | None:
        """
        Get the device identifier associated with this user.

        Returns:
            str | None: The device ID if set, otherwise None
        """
        raise NotImplementedError

    @abstractmethod
    def get_security_level(self) -> int | None:
        """
        Get the security clearance level of this user.

        Returns:
            int | None: The security level if set, otherwise None
        """
        raise NotImplementedError
