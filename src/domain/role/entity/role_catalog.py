from enum import Enum
from src.domain.permission.entity.permission_catalog import PermissionEnum as PE
from src.domain.role.entity.role import Role
from src.domain.role.values.role_name import RoleName


class SystemRoles(Enum):
    """
    Just and example of Pre-defined system roles with their permissions
    """

    SUPER_ADMIN = Role(
        name=RoleName("super_admin"),
        description="Complete system access with all permissions",
        security_level=0,
        _permissions=PE.get_all_permissions(),  # All permissions,
    )

    SYSTEM_ADMIN = Role(
        name=RoleName("system_admin"),
        description="Manages system settings and organizations",
        security_level=1,
        _permissions={
            PE.MANAGE_SYSTEM_SETTINGS.value,
            PE.VIEW_SYSTEM_LOGS.value,
            PE.CREATE_USER.value,
            PE.UPDATE_USER.value,
            PE.DELETE_USER.value,
            PE.VIEW_USER.value,
            PE.VIEW_ROLE.value,
            PE.ASSIGN_ROLE.value,
            PE.REMOVE_ROLE.value,
            PE.VIEW_AUDIT_LOGS.value,
            PE.EXPORT_AUDIT_LOGS.value,
        },
    )

    PROJECT_MANAGER = Role(
        name=RoleName("project_manager"),
        description="Manages projects and project members",
        security_level=2,
        _permissions={
            PE.UPDATE_PROJECT.value,
            PE.VIEW_PROJECT.value,
            PE.VIEW_USER.value,
            PE.CREATE_ROLE.value,
            PE.VIEW_ROLE.value,
            PE.UPDATE_ROLE.value,
            PE.ASSIGN_ROLE.value,
            PE.CREATE_CONTENT.value,
            PE.UPDATE_CONTENT.value,
            PE.DELETE_CONTENT.value,
            PE.VIEW_CONTENT.value,
            PE.APPROVE_CONTENT.value,
        },
    )

    SECURITY_AUDITOR = Role(
        name=RoleName("security_auditor"),
        description="View-only access for security auditing",
        security_level=3,
        _permissions={
            PE.VIEW_SYSTEM_LOGS.value,
            PE.VIEW_USER.value,
            PE.VIEW_ROLE.value,
            PE.VIEW_AUDIT_LOGS.value,
            PE.EXPORT_AUDIT_LOGS.value,
        },
    )

    TEAM_LEAD = Role(
        name=RoleName("team_lead"),
        description="Manages team members and their content",
        security_level=4,
        _permissions={
            PE.VIEW_PROJECT.value,
            PE.VIEW_USER.value,
            PE.CREATE_CONTENT.value,
            PE.UPDATE_CONTENT.value,
            PE.VIEW_CONTENT.value,
            PE.APPROVE_CONTENT.value,
        },
    )

    CONTENT_ADMIN = Role(
        name=RoleName("content_admin"),
        description="Full control over content",
        security_level=5,
        _permissions={
            PE.CREATE_CONTENT.value,
            PE.UPDATE_CONTENT.value,
            PE.DELETE_CONTENT.value,
            PE.VIEW_CONTENT.value,
            PE.APPROVE_CONTENT.value,
        },
    )

    CONTENT_CREATOR = Role(
        name=RoleName("content_creator"),
        description="Creates and edits content",
        security_level=6,
        _permissions={
            PE.CREATE_CONTENT.value,
            PE.UPDATE_CONTENT.value,
            PE.VIEW_CONTENT.value,
        },
    )

    CONTENT_REVIEWER = Role(
        name=RoleName("content_reviewer"),
        description="Reviews and approves content",
        security_level=7,
        _permissions={
            PE.VIEW_CONTENT.value,
            PE.APPROVE_CONTENT.value,
        },
    )

    STANDARD_USER = Role(
        name=RoleName("user"),
        description="Normal application access",
        security_level=8,
        _permissions={
            PE.VIEW_CONTENT.value,
        },
    )

    # GUEST = Role(
    #     name=RoleName("guest"),
    #     description="Limited read-only access",
    #     security_level=9,
    #     _permissions={
    #         PE.VIEW_CONTENT.value.name,
    #     },
    # )
    #
    # API_CONSUMER = Role(
    #     name=RoleName("api_consumer"),
    #     description="Machine-to-machine API access",
    #     security_level=10,
    #     _permissions={
    #         PE.API_READ.value.name,
    #         PE.API_WRITE.value.name,
    #     },
    # )

    @classmethod
    def get_all_roles(cls):
        return [role.value for role in cls]
