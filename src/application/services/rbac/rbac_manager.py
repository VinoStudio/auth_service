import re
from dataclasses import dataclass, field
from functools import wraps
from typing import List, ClassVar, Tuple

from src.application.base.rbac.base import BaseRBACManager
from src.application.base.security.jwt_user import JWTUserInterface
from src.application.exceptions import (
    RoleAlreadyExistsException,
    AccessDeniedException,
    RoleInUseException,
    PermissionAlreadyExistsException,
    PermissionInUseException,
)
from src.domain.permission.values import PermissionName
from src.domain.role.values.role_name import RoleName
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
import src.domain as domain
import src.application.dto as dto
import structlog

logger = structlog.getLogger(__name__)


@dataclass(eq=False)
class RBACManager(BaseRBACManager):
    """
    Core service for managing RBAC (Role-Based Access Control)
    Responsible for all role and permission management operations
    """

    role_repository: BaseRoleRepository
    permission_repository: BasePermissionRepository
    system_roles: ClassVar[Tuple[str]] = ("super_admin", "system_admin")
    protected_permissions: ClassVar[Tuple[str]] = (
        "role:create",
        "role:update",
        "role:delete",
        "role:assign",
        "role:remove",
        "permission:create",
        "permission:update",
        "permission:delete",
        "system:manage_settings",
        "security:manage",
        "user:impersonate",
    )

    # -------------------- Authorization Decorators --------------------

    @staticmethod
    def require_permission(permission_name: str):
        """Decorator to check if user has required permission"""

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                # Get user from a consistent position or parameter name
                request_from = kwargs.get("request_from")

                if not request_from:
                    raise ValueError("Authorization requires request_from parameter")

                if not self._has_permission(request_from, permission_name):
                    operation = permission_name.split(":")[0]
                    raise AccessDeniedException(
                        f"You don't have permission to {operation}"
                    )

                return await func(self, *args, **kwargs)

            return wrapper

        return decorator

    # -------------------- Role Operations --------------------
    @require_permission("role:view")
    async def get_role(
        self,
        role_name: str,
        request_from: JWTUserInterface,
    ) -> domain.Role:
        """Get a role by name"""

        return await self.role_repository.get_role_by_name(role_name)

    @require_permission("role:create")
    async def create_role(
        self,
        role_dto: dto.RoleCreation,
        request_from: JWTUserInterface,
    ) -> domain.Role:
        """Create a new role with specified permissions"""

        self._validate_role_name(role_dto.name)

        await self._check_if_role_exists(role_dto.name)

        new_role = domain.Role(
            name=RoleName(role_dto.name),
            description=role_dto.description,
            security_level=role_dto.security_level,
        )

        self._check_security_level(
            user_level=request_from.get_security_level(),
            role_level=new_role.security_level,
        )

        # Add permission to role. Of there is not a permission, repo raises exception
        if role_dto.permissions:
            for permission_name in role_dto.permissions:
                permission = await self.permission_repository.get_permission_by_name(
                    permission_name=permission_name
                )
                self._validate_permission_interaction(
                    permission_name=permission_name,
                    request_from=request_from,
                )
                new_role.add_permission(permission)

        await self.role_repository.create_role(new_role)

        logger.info(
            f"Role '{new_role.name.to_raw()}' created by {request_from.get_user_identifier()}"
        )

        return new_role

    @require_permission("role:update")
    async def update_role(
        self,
        role: domain.Role,
        request_from: JWTUserInterface,
    ) -> domain.Role:
        """Update an existing given role"""

        # Security checks
        self._can_modify_system_roles(request_from, role)
        self._check_security_level(
            user_level=request_from.get_security_level(),
            role_level=role.security_level,
        )

        # Update role properties
        await self.role_repository.update_role(role=role)

        logger.info(
            f"Role '{role.name.to_raw()}' updated by {request_from.get_user_identifier()}"
        )

        return role

    @require_permission("role:delete")
    async def delete_role(
        self,
        role: domain.Role,
        request_from: JWTUserInterface,
    ) -> None:
        """Delete an existing role"""

        # Security checks
        self._can_modify_system_roles(request_from, role)
        self._check_security_level(
            user_level=request_from.get_security_level(),
            role_level=role.security_level,
        )

        # Check for users with this role
        users_count = await self._count_users_with_role(role_name=role.name.to_raw())

        if users_count > 0:
            raise RoleInUseException(
                f"Role '{role.name.to_raw()}' is still assigned to {users_count} users"
            )

        # Delete the role
        await self.role_repository.delete_role(role_id=role.id)

        logger.info(
            f"Role '{role.name.to_raw()}' deleted by {request_from.get_user_identifier()}"
        )

    # -------------------- Permission Operations --------------------

    @require_permission("permission:view")
    async def get_permission(
        self, permission_name: str, request_from: JWTUserInterface
    ) -> domain.Permission:
        """Get a permission by name"""

        self._validate_permission_interaction(
            permission_name=permission_name,
            request_from=request_from,
        )

        db_permission: domain.Permission = (
            await self.permission_repository.get_permission_by_name(
                permission_name=permission_name
            )
        )

        return db_permission

    @require_permission("permission:create")
    async def create_permission(
        self,
        permission_dto: dto.PermissionCreation,
        request_from: JWTUserInterface,
    ) -> domain.Permission:
        """Create a new permission"""
        # Check if permission exists
        await self._check_if_permission_exists(permission_dto.name)

        new_permission = domain.Permission(
            permission_name=PermissionName(permission_dto.name),
        )

        await self.permission_repository.create_permission(new_permission)

        logger.info(
            f"Permission '{new_permission.permission_name.to_raw()}' created by {request_from.get_user_identifier()}"
        )

        return new_permission

    @require_permission("permission:delete")
    async def delete_permission(
        self,
        permission: domain.Permission,
        request_from: JWTUserInterface,
    ) -> None:
        """Delete an existing permission"""
        roles_in_use = await self._count_roles_with_permission(
            permission_name=permission.permission_name.to_raw()
        )

        if roles_in_use > 0:
            raise PermissionInUseException(
                f"Permission '{permission.permission_name.to_raw()}' is still assigned to {roles_in_use} roles"
            )

        await self.permission_repository.delete_permission(
            permission_name=permission.permission_name.to_raw()
        )

        logger.info(
            f"Permission '{permission.permission_name.to_raw()}' deleted by {request_from.get_user_identifier()}"
        )

    # -------------------- User Role Operations --------------------
    @require_permission("role:assign")
    async def assign_role_to_user(
        self,
        user: domain.User,
        role: domain.Role,
        request_from: JWTUserInterface,
    ) -> domain.User:
        """Assign a role to a user"""
        # Security check
        self._check_security_level(
            user_level=request_from.get_security_level(), role_level=role.security_level
        )

        if role in user.roles:
            return user

        user.add_role(role)

        logger.info(
            f"Role '{role.name.to_raw()}' assigned to user '{user.username.to_raw()}' by {request_from.get_user_identifier()}"
        )

        return user

    @require_permission("role:remove")
    async def remove_role_from_user(
        self,
        user: domain.User,
        role: domain.Role,
        request_from: JWTUserInterface,
    ) -> domain.User:
        """Remove a role from a user"""
        # Security check
        self._check_security_level(
            user_level=request_from.get_security_level(), role_level=role.security_level
        )

        if role not in user.roles:
            return user

        user.remove_role(role)

        logger.info(
            f"Role '{role.name.to_raw()}' removed from user '{user.username.to_raw()}' by {request_from.get_user_identifier()}"
        )

        return user

    # -------------------- Validation Methods --------------------

    async def _check_if_role_exists(self, role_name: str) -> None:
        if await self.role_repository.check_role_exists(role_name):
            raise RoleAlreadyExistsException(value=role_name)

    async def _check_if_permission_exists(self, permission_name: str) -> None:
        if await self.permission_repository.check_permission_exists(permission_name):
            raise PermissionAlreadyExistsException(value=permission_name)

    async def _count_users_with_role(self, role_name: str) -> int:
        return await self.role_repository.count_users_with_role(role_name)

    async def _count_roles_with_permission(self, permission_name: str) -> int:
        return await self.permission_repository.count_roles_with_permission(
            permission_name
        )

    # -------------------- Permission Checking --------------------

    def _validate_role_name(self, role_name: str) -> None:
        """Validate that role name follows naming conventions"""
        if not re.match(r"^[a-z0-9_]+$", role_name):
            raise ValidationException(
                "Role name must be lowercase alphanumeric with underscores"
            )

        if role_name.startswith(("system_", "admin_")) and not self._is_system_user(
            request_from
        ):
            raise ValidationException(
                "Role names with 'system_' or 'admin_' prefixes are reserved"
            )

    def _validate_permission_interaction(
        self,
        permission_name: str,
        request_from: JWTUserInterface,
    ) -> None:
        """
        Validate if the requesting user can assign a specific permission to a role
        with the given security level
        """
        # System users can assign any permission
        if self._is_system_user(request_from):
            return

        # Check if this is a restricted permission
        if permission_name in self.protected_permissions:
            raise AccessDeniedException(
                f"Permission '{permission_name}' can only be interacted by system users"
            )

        # Check if requesting user has this permission
        if permission_name not in request_from.get_permissions():
            raise AccessDeniedException(
                f"You cannot interact with permission that you don't have"
            )

    def _has_permission(self, user: JWTUserInterface, permission_name: str) -> bool:
        """Check if a user has a specific permission"""
        # System role check (super_admin, system_admin)
        if self._is_system_user(user):
            return True

        # Direct permission check
        return permission_name in user.get_permissions()

    @staticmethod
    def _check_security_level(user_level: int, role_level: int) -> None:
        """Verify user has sufficient security level to manipulate role"""

        if role_level == 0:
            raise AccessDeniedException("Security level 0 role is read-only")

        if user_level > role_level:
            raise AccessDeniedException(
                "You cannot interact with roles having higher security level than yours"
            )

    def _can_modify_system_roles(
        self, request_from: JWTUserInterface, role: domain.Role
    ) -> None:
        """Check if a user can modify system roles"""
        # System users can modify system roles
        if self._is_system_user(request_from):
            return

        # Regular users cannot modify system roles
        if role.name.to_raw() in self.system_roles:
            raise AccessDeniedException("You cannot modify system roles")

    def _is_system_user(self, user: JWTUserInterface) -> bool:
        """Check if user has any system role"""
        return any(role in self.system_roles for role in user.get_roles())
