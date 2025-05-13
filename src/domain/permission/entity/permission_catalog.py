from enum import Enum

from src.domain.permission.entity.permission import Permission
from src.domain.permission.values.permission_name import PermissionName


class PermissionEnum(Enum):
    """An example of predefined project permissions."""

    # System Management
    MANAGE_SYSTEM_SETTINGS = Permission(PermissionName("system:manage_settings"))
    VIEW_SYSTEM_LOGS = Permission(PermissionName("system:view_logs"))

    # User Management
    CREATE_USER = Permission(PermissionName("user:create"))
    UPDATE_USER = Permission(PermissionName("user:update"))
    DELETE_USER = Permission(PermissionName("user:delete"))
    VIEW_USER = Permission(PermissionName("user:view"))
    IMPERSONATE_USER = Permission(PermissionName("user:impersonate"))

    # Role Management
    CREATE_ROLE = Permission(PermissionName("role:create"))
    UPDATE_ROLE = Permission(PermissionName("role:update"))
    DELETE_ROLE = Permission(PermissionName("role:delete"))
    VIEW_ROLE = Permission(PermissionName("role:view"))
    ASSIGN_ROLE = Permission(PermissionName("role:assign"))
    REMOVE_ROLE = Permission(PermissionName("role:remove"))

    # Permission Management
    CREATE_PERMISSION = Permission(PermissionName("permission:create"))
    UPDATE_PERMISSION = Permission(PermissionName("permission:update"))
    DELETE_PERMISSION = Permission(PermissionName("permission:delete"))
    VIEW_PERMISSION = Permission(PermissionName("permission:view"))

    # Project Management
    CREATE_PROJECT = Permission(PermissionName("project:create"))
    UPDATE_PROJECT = Permission(PermissionName("project:update"))
    DELETE_PROJECT = Permission(PermissionName("project:delete"))
    VIEW_PROJECT = Permission(PermissionName("project:view"))

    # Content Management
    CREATE_CONTENT = Permission(PermissionName("content:create"))
    UPDATE_CONTENT = Permission(PermissionName("content:update"))
    DELETE_CONTENT = Permission(PermissionName("content:delete"))
    VIEW_CONTENT = Permission(PermissionName("content:view"))
    APPROVE_CONTENT = Permission(PermissionName("content:approve"))

    # API Access
    API_READ = Permission(PermissionName("api:read"))
    API_WRITE = Permission(PermissionName("api:write"))
    API_DELETE = Permission(PermissionName("api:delete"))

    # Audit
    VIEW_AUDIT_LOGS = Permission(PermissionName("audit:view"))
    EXPORT_AUDIT_LOGS = Permission(PermissionName("audit:export"))

    @classmethod
    def get_all_permissions(cls) -> set[Permission]:
        return {permission.value for permission in cls}
