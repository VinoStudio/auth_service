import re
from dataclasses import dataclass
from functools import wraps
from typing import ClassVar, Tuple

from src.application.base.rbac.base import BaseRBACManager
from src.application.base.security.jwt_user import JWTUserInterface
from src.application.exceptions import (
    RoleAlreadyExistsException,
    AccessDeniedException,
    RoleInUseException,
    PermissionAlreadyExistsException,
    PermissionInUseException,
    ValidationException,
)
from src.domain.permission.values import PermissionName
from src.domain.role.values.role_name import RoleName
from src.infrastructure.base.repository import BaseUserWriter
from src.infrastructure.base.repository.permission_repo import BasePermissionRepository
from src.infrastructure.base.repository.role_repo import BaseRoleRepository
import src.domain as domain
import src.application.dto as dto
import structlog

from src.infrastructure.repositories.role.role_invalidation_repo import (
    RoleInvalidationRepository,
)

logger = structlog.getLogger(__name__)


@dataclass(eq=False)
class RBACManager(BaseRBACManager):
    """
    Core service for managing RBAC (Role-Based Access Control)
    Responsible for all role and permission management operations
    """

    role_repository: BaseRoleRepository
    user_writer: BaseUserWriter
    permission_repository: BasePermissionRepository
    role_invalidation: RoleInvalidationRepository
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
                    raise AccessDeniedException(
                        f"You don't have permission to {permission_name}"
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
        """
        Retrieve a role by its name.

        Args:
            role_name: The name of the role to retrieve
            request_from: The authenticated user making the request

        Returns:
            domain.Role: The requested role object

        Raises:
            AccessDeniedException: If user do not have required permission for view roles
            RoleDoesNotExistException(InfrastructureException): If the role does not exist
        """

        return await self.role_repository.get_role_by_name(role_name)

    @require_permission("role:create")
    async def create_role(
        self,
        role_dto: dto.RoleCreation,
        request_from: JWTUserInterface,
    ) -> domain.Role:
        """
        Create a new role with specified permissions.

        Args:
            role_dto: Data transfer object containing role creation information
                - name: Unique name for the role
                - description: Optional description of the role's purpose
                - security_level: Numeric security level for the role. Less = more secure
                - permissions: List of permission names to assign to this role
            request_from: The authenticated user making the request

        Returns:
            domain.Role: The newly created role

        Raises:
            ValidationException: If the role name format is invalid
            RoleAlreadyExistsException: If a role with the given name already exists
            WrongRoleNameFormatException(DomainException): If the business role name format is invalid
            AccessDeniedException: If the user lacks required permission or sufficient security level
            or interact with protected permissions without system status
            PermissionDoesNotExistException(InfrastructureException): If any of the specified permissions don't exist
        """

        self._validate_role_name(request_from=request_from, role_name=role_dto.name)

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
        """
        Update an existing role's properties.

        Args:
            role: The domain.Role object with updated properties
            request_from: The authenticated user making the request

        Returns:
            domain.Role: The updated role

        Raises:
            AccessDeniedException: If the user lacks required permission or sufficient security level
            or interact with protected permissions without system status
        """

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
        """
        Delete an existing role if it's not assigned to any users.

        Args:
            role: The domain.Role object of the role to delete
            request_from: The authenticated user making the request

        Raises:
            AccessDeniedException: If the user lacks required permission or sufficient security level
            or interact with protected permissions without system status
            RoleInUseException: If the role is still assigned to users
        """

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
        """
        Retrieve a permission by its name.

        Args:
            permission_name: The name of the permission to retrieve
            request_from: The authenticated user making the request

        Returns:
            domain.Permission: The requested permission object

        Raises:
            AccessDeniedException: If the user tries to interact with a protected system permission
            or lacks required permission to view permissions
            PermissionDoesNotExistException(InfrastructureException): If the permission does not exist
        """

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
        """
        Create a new permission in the system.

        Args:
            permission_dto: Data transfer object containing permission creation information
                - name: Unique permission identifier in format 'resource:action'
            request_from: The authenticated user making the request

        Returns:
            domain.Permission: The newly created permission

        Raises:
            AccessDeniedException: If the user lacks required permission to create a permissions
            PermissionAlreadyExistsException: If the permission already exists
            WrongPermissionNameFormatException: If the permission name format is invalid
        """
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
        """
        Delete an existing permission if it's not assigned to any roles.

        Args:
            permission: The domain.Permission object of the permission to delete
            request_from: The authenticated user making the request

        Raises:
            AccessDeniedException: If the user lacks required permission to create a permissions
            PermissionInUseException: If the permission is assigned to any roles
        """
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
        """
        Assign a specific role to a user.

        Args:
            user: The domain.User object of the user to receive the role
            role: The domain.Role object of the role to assign
            request_from: The authenticated user making the request

        Returns:
            domain.User: The updated user object

        Raises:
            AccessDeniedException: If the user lacks required permission or sufficient security level
        """
        # Security check
        self._check_security_level(
            user_level=request_from.get_security_level(), role_level=role.security_level
        )

        if role in user.roles:
            return user

        user.add_role(role)

        await self.user_writer.update_user(user=user)

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
        """
        Remove a specific role from a user

        Args:
            user: The domain.User object of the user to receive the role
            role: The domain.Role object of the role to assign
            request_from: The authenticated user making the request

        Returns:
            domain.User: The updated user object

        Raises:
            AccessDeniedException: If the user lacks required permission or sufficient security level
        """
        # Security check
        self._check_security_level(
            user_level=request_from.get_security_level(), role_level=role.security_level
        )

        if role not in user.roles:
            return user

        user.remove_role(role)

        await self.user_writer.update_user(user=user)

        logger.info(
            f"Role '{role.name.to_raw()}' removed from user '{user.username.to_raw()}' by {request_from.get_user_identifier()}"
        )

        return user

    # -------------------- Invalidation Methods --------------------

    async def invalidate_role(self, role_name: str) -> None:
        await self.role_invalidation.invalidate_role(role_name)

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
    #
    def _validate_role_name(
        self, request_from: JWTUserInterface, role_name: str
    ) -> None:
        """Validate that role name follows naming conventions"""
        if len(role_name) > 24 or len(role_name) < 3:
            raise ValidationException("Role name must be between 3 and 30 characters")

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
