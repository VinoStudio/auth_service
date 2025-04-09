from abc import ABC, abstractmethod
from typing import List

import src.domain as domain
import src.application.dto as dto

from src.application.base.security import JWTUserInterface


class BaseRBACManager(ABC):
    """
    Abstract base class defining the interface for Role-Based Access Control management
    """

    @abstractmethod
    async def get_role(
        self, role_name: str, request_from: JWTUserInterface
    ) -> domain.Role:
        """Get a role by name"""
        raise NotImplementedError

    @abstractmethod
    async def create_role(
        self, role_dto: dto.RoleCreation, request_from: JWTUserInterface
    ) -> domain.Role:
        """Create a new role with specified permissions"""
        raise NotImplementedError

    @abstractmethod
    async def update_role(
        self, role: domain.Role, request_from: JWTUserInterface
    ) -> domain.Role:
        """Update an existing given role"""
        pass

    @abstractmethod
    async def delete_role(
        self, role: domain.Role, request_from: JWTUserInterface
    ) -> None:
        """Delete an existing role"""
        pass

    @abstractmethod
    async def get_permission(
        self, permission_name: str, request_from: JWTUserInterface
    ) -> domain.Permission:
        """Get a permission by name"""
        pass

    @abstractmethod
    async def create_permission(
        self, permission_dto: dto.PermissionCreation, request_from: JWTUserInterface
    ) -> domain.Permission:
        """Create a new permission"""
        pass

    @abstractmethod
    async def delete_permission(
        self, permission: domain.Permission, request_from: JWTUserInterface
    ) -> None:
        """Delete an existing permission"""
        pass

    @abstractmethod
    def assign_role_to_user(
        self, user: domain.User, role: domain.Role, request_from: JWTUserInterface
    ) -> domain.User:
        """Assign a role to a user"""
        pass

    @abstractmethod
    def remove_role_from_user(
        self, user: domain.User, role: domain.Role, request_from: JWTUserInterface
    ) -> domain.User:
        """Remove a role from a user"""
        pass

    @abstractmethod
    def _has_permission(self, user: JWTUserInterface, permission_name: str) -> bool:
        """Check if a user has a specific permission"""
        pass

    @staticmethod
    @abstractmethod
    def _check_security_level(user_level: int, role_level: int) -> None:
        """Verify user has sufficient security level to manipulate role"""
        pass
