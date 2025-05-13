from enum import Enum

from src.domain.permission.entity.permission_catalog import PermissionEnum
from src.domain.role.entity.role import Role
from src.domain.role.values.role_name import RoleName


class SystemRoles(Enum):
    """Just and example of Pre-defined system roles with their permissions."""

    SUPER_ADMIN = Role(
        name=RoleName("super_admin"),
        description="Complete system access with all permissions",
        security_level=0,
        _permissions=PermissionEnum.get_all_permissions(),  # All permissions,
    )

    SYSTEM_ADMIN = Role(
        name=RoleName("system_admin"),
        description="Manages system settings and organizations",
        security_level=1,
        _permissions={
            PermissionEnum.MANAGE_SYSTEM_SETTINGS.value,
            PermissionEnum.VIEW_SYSTEM_LOGS.value,
            PermissionEnum.CREATE_USER.value,
            PermissionEnum.UPDATE_USER.value,
            PermissionEnum.DELETE_USER.value,
            PermissionEnum.VIEW_USER.value,
            PermissionEnum.VIEW_ROLE.value,
            PermissionEnum.ASSIGN_ROLE.value,
            PermissionEnum.REMOVE_ROLE.value,
            PermissionEnum.VIEW_AUDIT_LOGS.value,
            PermissionEnum.EXPORT_AUDIT_LOGS.value,
        },
    )

    PROJECT_MANAGER = Role(
        name=RoleName("project_manager"),
        description="Manages projects and project members",
        security_level=2,
        _permissions={
            PermissionEnum.UPDATE_PROJECT.value,
            PermissionEnum.VIEW_PROJECT.value,
            PermissionEnum.VIEW_USER.value,
            PermissionEnum.CREATE_ROLE.value,
            PermissionEnum.VIEW_ROLE.value,
            PermissionEnum.UPDATE_ROLE.value,
            PermissionEnum.ASSIGN_ROLE.value,
            PermissionEnum.VIEW_PERMISSION.value,
            PermissionEnum.UPDATE_PERMISSION.value,
            PermissionEnum.DELETE_PERMISSION.value,
            PermissionEnum.CREATE_CONTENT.value,
            PermissionEnum.UPDATE_CONTENT.value,
            PermissionEnum.DELETE_CONTENT.value,
            PermissionEnum.VIEW_CONTENT.value,
            PermissionEnum.APPROVE_CONTENT.value,
        },
    )

    SECURITY_AUDITOR = Role(
        name=RoleName("security_auditor"),
        description="View-only access for security auditing",
        security_level=3,
        _permissions={
            PermissionEnum.VIEW_SYSTEM_LOGS.value,
            PermissionEnum.VIEW_USER.value,
            PermissionEnum.VIEW_ROLE.value,
            PermissionEnum.VIEW_AUDIT_LOGS.value,
            PermissionEnum.EXPORT_AUDIT_LOGS.value,
        },
    )

    TEAM_LEAD = Role(
        name=RoleName("team_lead"),
        description="Manages team members and their content",
        security_level=4,
        _permissions={
            PermissionEnum.VIEW_PROJECT.value,
            PermissionEnum.VIEW_USER.value,
            PermissionEnum.CREATE_CONTENT.value,
            PermissionEnum.UPDATE_CONTENT.value,
            PermissionEnum.VIEW_CONTENT.value,
            PermissionEnum.APPROVE_CONTENT.value,
        },
    )

    CONTENT_ADMIN = Role(
        name=RoleName("content_admin"),
        description="Full control over content",
        security_level=5,
        _permissions={
            PermissionEnum.CREATE_CONTENT.value,
            PermissionEnum.UPDATE_CONTENT.value,
            PermissionEnum.DELETE_CONTENT.value,
            PermissionEnum.VIEW_CONTENT.value,
            PermissionEnum.APPROVE_CONTENT.value,
        },
    )

    CONTENT_CREATOR = Role(
        name=RoleName("content_creator"),
        description="Creates and edits content",
        security_level=6,
        _permissions={
            PermissionEnum.CREATE_CONTENT.value,
            PermissionEnum.UPDATE_CONTENT.value,
            PermissionEnum.VIEW_CONTENT.value,
        },
    )

    CONTENT_REVIEWER = Role(
        name=RoleName("content_reviewer"),
        description="Reviews and approves content",
        security_level=7,
        _permissions={
            PermissionEnum.VIEW_CONTENT.value,
            PermissionEnum.APPROVE_CONTENT.value,
        },
    )

    STANDARD_USER = Role(
        name=RoleName("user"),
        description="Normal application access",
        security_level=8,
        _permissions={
            PermissionEnum.VIEW_CONTENT.value,
        },
    )

    @classmethod
    def get_all_roles(cls) -> list[Role]:
        return [role.value for role in cls]
