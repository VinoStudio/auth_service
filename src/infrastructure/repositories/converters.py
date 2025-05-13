from src import domain
from src.domain.permission.values.permission_name import PermissionName
from src.domain.role.values.role_name import RoleName
from src.domain.session.values.device_info import DeviceInfo
from src.domain.user.values import (
    Email,
    Password,
    UserId,
    Username,
)
from src.infrastructure.db import models


class OrmToDomainConverter:
    """Converts SQLAlchemy ORM models to domain entities"""

    @staticmethod
    def user_to_domain(user_model: models.User) -> domain.User:
        # Create user
        domain_user: domain.User = domain.User(
            id=UserId(user_model.id),
            username=Username(user_model.username),
            email=Email(user_model.email),
            password=Password(user_model.hashed_password),
            deleted_at=user_model.deleted_at,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            version=user_model.version,
        )

        # Convert sessions
        for session in user_model.sessions:
            if session is not None:
                user_session = domain.Session(
                    id=session.id,
                    user_id=session.user_id,
                    device_info=DeviceInfo.create(session.device_info),
                    device_id=session.device_id,
                    user_agent=session.user_agent,
                    last_activity=session.last_activity,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    is_active=session.is_active,
                )
                domain_user.add_session(user_session)

        # Convert oauth accounts
        for account in user_model.oauth_accounts:
            if account is not None:
                oauth_account = domain.OAuthAccount(
                    id=account.id,
                    user_id=account.user_id,
                    provider=account.provider,
                    provider_user_id=account.provider_user_id,
                    provider_email=account.provider_email,
                    created_at=account.created_at,
                    updated_at=account.updated_at,
                    is_active=account.is_active,
                )
                domain_user.add_oauth_account(oauth_account)

        # Convert roles with permissions
        for role_model in user_model.roles:
            role_domain = domain.Role(
                id=role_model.id,
                name=RoleName(role_model.name),
                description=role_model.description,
                security_level=role_model.security_level,
                created_at=role_model.created_at,
                updated_at=role_model.updated_at,
            )
            for perm in role_model.permissions:
                permission = domain.Permission(
                    id=perm.id,
                    permission_name=PermissionName(perm.name),
                    created_at=perm.created_at,
                    updated_at=perm.updated_at,
                )
                role_domain.add_permission(permission)

            domain_user.add_role(role_domain)

        return domain_user

    @staticmethod
    def role_to_domain(role_model: models.Role) -> domain.Role:
        role_domain = domain.Role(
            id=role_model.id,
            name=RoleName(role_model.name),
            description=role_model.description,
            security_level=role_model.security_level,
            created_at=role_model.created_at,
            updated_at=role_model.updated_at,
        )
        for perm in role_model.permissions:
            permission = domain.Permission(
                id=perm.id,
                permission_name=PermissionName(perm.name),
                created_at=perm.created_at,
                updated_at=perm.updated_at,
            )
            role_domain.add_permission(permission)

        return role_domain

    @staticmethod
    def permission_to_domain(permission_id: str, name: str) -> domain.Permission:
        return domain.Permission(
            id=permission_id,
            permission_name=PermissionName(name),
        )

    @staticmethod
    def user_session_to_domain(session: models.UserSession) -> domain.Session:
        return domain.Session(
            id=session.id,
            user_id=session.user_id,
            device_info=DeviceInfo.create(session.device_info),
            device_id=session.device_id,
            user_agent=session.user_agent,
            last_activity=session.last_activity,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    @staticmethod
    def oauth_account_to_domain(account: models.OAuthAccount) -> domain.OAuthAccount:
        return domain.OAuthAccount(
            id=account.id,
            user_id=account.user_id,
            provider=account.provider,
            provider_user_id=account.provider_user_id,
            provider_email=account.provider_email,
            created_at=account.created_at,
            updated_at=account.updated_at,
            is_active=account.is_active,
        )


class DomainToOrmConverter:
    @staticmethod
    def domain_to_user_model(user: domain.User) -> models.User:
        user_model = models.User(
            id=user.id.to_raw(),
            username=user.username.to_raw(),
            email=user.email.to_raw(),
            hashed_password=user.password.to_raw(),
            jwt_data=user.jwt_data,
            created_at=user.created_at,
            deleted_at=user.deleted_at,
            updated_at=user.updated_at,
            version=user.version,
        )

        return user_model

    @staticmethod
    def domain_to_active_user(user: domain.User) -> models.User:
        user_model = models.User(
            id=user.id.to_raw(),
            username=user.username.to_raw(),
            email=user.email.to_raw(),
            jwt_data=user.jwt_data,
            hashed_password=user.password.to_raw(),
            created_at=user.created_at,
            deleted_at=user.deleted_at,
            updated_at=user.updated_at,
            version=user.version,
        )

        if len(user.sessions) > 0:
            user_model.sessions = [
                models.UserSession(
                    id=session.id,
                    user_id=session.user_id,  # type: ignore
                    device_info=session.device_info.to_bytes(),
                    user_agent=session.user_agent,
                    device_id=session.device_id,
                    last_activity=session.last_activity,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    is_active=session.is_active,
                )
                for session in user.sessions
            ]

        if len(user.oauth_accounts) > 0:
            user_model.oauth_accounts = [
                models.OAuthAccount(
                    id=oauth_account.id,
                    user_id=oauth_account.user_id,
                    provider=oauth_account.provider,
                    provider_user_id=oauth_account.provider_user_id,
                    provider_email=oauth_account.provider_email,
                    created_at=oauth_account.created_at,
                    updated_at=oauth_account.updated_at,
                    is_active=oauth_account.is_active,
                )
                for oauth_account in user.oauth_accounts
            ]

        user_model.roles = [
            models.Role(
                id=role.id,
                name=role.name.to_raw(),
                description=role.description,
                security_level=role.security_level,
                created_at=role.created_at,
                updated_at=role.updated_at,
                permissions=[
                    models.Permission(
                        id=permission.id,
                        name=permission.permission_name.to_raw(),
                        created_at=permission.created_at,
                        updated_at=permission.updated_at,
                    )
                    for permission in role.permission
                ],
            )
            for role in user.roles
        ]

        return user_model

    @staticmethod
    def domain_to_role_creator(role: domain.Role) -> models.Role:
        return models.Role(
            id=role.id,
            name=role.name.to_raw(),
            description=role.description,
            security_level=role.security_level,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=[],
        )

    @staticmethod
    def domain_to_role(role: domain.Role) -> models.Role:
        return models.Role(
            id=role.id,
            name=role.name.to_raw(),
            description=role.description,
            security_level=role.security_level,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=[
                models.Permission(
                    id=permission.id,
                    name=permission.permission_name.to_raw(),
                )
                for permission in role.permission
            ],
        )

    @staticmethod
    def domain_to_user_session(session: domain.Session) -> models.UserSession:
        return models.UserSession(
            id=session.id,
            user_id=session.user_id,  # type: ignore
            device_info=session.device_info.to_bytes(),
            user_agent=session.user_agent,
            device_id=session.device_id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_activity=session.last_activity,
            is_active=session.is_active,
        )

    @staticmethod
    def domain_to_oauth_account(oauth_account: domain.OAuthAccount) -> models.OAuthAccount:
        return models.OAuthAccount(
            id=oauth_account.id,
            user_id=oauth_account.user_id,
            provider=oauth_account.provider,
            provider_user_id=oauth_account.provider_user_id,
            provider_email=oauth_account.provider_email,
            created_at=oauth_account.created_at,
            updated_at=oauth_account.updated_at,
            is_active=oauth_account.is_active,
        )
