import src.domain as domain
import src.infrastructure.db.models as models

from src.domain.user.values import (
    Email,
    Password,
    UserId,
    Username,
)
from src.domain.role.entity.role import Role
from src.domain.role.values.role_name import RoleName
from src.domain.permission.values.permission_name import PermissionName


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
            updated_at=user_model.updated_at,
            version=user_model.version,
        )

        # Convert sessions
        for session in user_model.sessions:
            if session:
                user_session = domain.Session(
                    id=session.id,
                    user_id=session.user_id,
                    device_info=session.device_info,
                    user_agent=session.device_info,
                    last_activity=session.last_activity,
                    is_active=session.is_active,
                )
                domain_user.add_session(user_session)

        # Convert roles with permissions
        for role_model in user_model.roles:
            role_domain = Role(
                id=role_model.id,
                name=RoleName(role_model.name),
            )
            for perm in role_model.permissions:
                permission = domain.Permission(
                    id=perm.id,
                    permission_name=PermissionName(perm.name),
                )
                role_domain.add_permission(permission)

            domain_user.add_role(role_domain)

        return domain_user

    @staticmethod
    def role_to_domain(role_model: models.Role) -> Role:
        role_domain = Role(
            id=role_model.id,
            name=RoleName(role_model.name),
        )
        for perm in role_model.permissions:
            permission = domain.Permission(
                id=perm.id,
                permission_name=PermissionName(perm.name),
            )
            role_domain.add_permission(permission)

        return role_domain

    @staticmethod
    def permission_to_domain(permission_id: str, name: str) -> domain.Permission:
        return domain.Permission(
            id=permission_id,
            permission_name=PermissionName(name),
        )

class DomainToOrmConverter:
    @staticmethod
    def domain_to_user_model(user: domain.User) -> models.User:
        user_model = models.User(
            id=user.id.to_raw(),
            username=user.username.to_raw(),
            email=user.email.to_raw(),
            hashed_password=user.password.to_raw(),
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
            hashed_password=user.password.to_raw(),
            deleted_at=user.deleted_at,
            updated_at=user.updated_at,
            version=user.version,
        )

        if len(user.sessions) > 0:
            user_model.sessions = [
                models.UserSession(
                    id=session.id.to_raw(),
                    user_id=session.user_id,  # type: ignore
                    device_info=session.device_info,
                    user_agent=session.user_agent,
                    last_activity=session.last_activity,
                    is_active=session.is_active,
                )
                for session in user.sessions
            ]

        user_model.roles = [
            models.Role(
                id=role.id,
                name=role.name.to_raw(),
                permissions=[
                    models.Permission(
                        id=permission.id,
                        name=permission.permission_name.to_raw(),
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
            permissions=[]
        )

    @staticmethod
    def domain_to_role(role: domain.Role) -> models.Role:
        return models.Role(
            id=role.id,
            name=role.name.to_raw(),
            permissions=[
                models.Permission(
                    id=permission.id,
                    name=permission.permission_name.to_raw(),
                )
                for permission in role.permission
            ],
        )

# def convert_db_model_to_user_entity(user: models.User) -> entities.User:
#     return entities.User(
#         id=UserId(user.id),
#         username=Username(user.username),
#         fullname=fullname,
#         deleted_at=DeletedAt(user.deleted_at),
#         version=user.version,
#     )
#
#
# def convert_db_model_to_active_user_entity(user: models.User) -> entities.User:
#     if user.deleted_at is not None:
#         raise UserIsDeletedException(user.id)
#
#     fullname = FullName(
#         first_name=user.first_name,
#         last_name=user.last_name,
#         middle_name=user.middle_name,
#     )
#     return entities.User(
#         id=UserId(user.id),
#         username=Username(user.username),
#         fullname=fullname,
#         deleted_at=DeletedAt(user.deleted_at),
#         version=user.version,
#     )
#
#
# def convert_user_entity_to_db_model(user: entities.User) -> models.User:
#     return models.User(
#         id=user.id.to_raw(),
#         username=user.username.to_raw(),
#         first_name=user.fullname.first_name,
#         last_name=user.fullname.last_name,
#         middle_name=user.fullname.middle_name,
#         deleted_at=user.deleted_at.value,
#         version=user.version,
#     )
#
#
# def convert_user_entity_to_db_dict(user: entities.User) -> dict:
#     return dict(
#         id=user.id.to_raw(),
#         username=user.username.to_raw(),
#         first_name=user.fullname.first_name,
#         last_name=user.fullname.last_name,
#         middle_name=user.fullname.middle_name,
#         deleted_at=user.deleted_at.value,
#         version=user.version,
#     )
#
#
# #
# # await self._session.execute(
# #     text(
# #         """
# #         INSERT INTO user (id, username, first_name, last_name, middle_name, deleted_at, version)
# #         VALUES (:id, :username, :first_name, :last_name, :middle_name, :deleted_at, :version)
# #         """
# #     ),
# #     c.convert_user_entity_to_db_model(user),
# # )
