from dataclasses import dataclass, field
from datetime import datetime, UTC
from src.domain.base.entity.aggregate import AggregateRoot
from src.domain.session.entity.session import Session
from src.domain.user.values import Password, Email, UserId, Username
from typing import Set, Self
from src.domain.role.entity.role import Role
from src.domain.user.exceptions import (
    UserIsDeletedException,
    PasswordDoesNotMatchException,
)
from src.domain.role.entity.role import Role
from src.domain.permission.entity.permission import Permission
import orjson


@dataclass
class User(AggregateRoot):
    id: UserId
    username: Username
    email: Email
    password: Password
    jwt_data: bytes | None = field(default=None)
    deleted_at: datetime | None = field(default=None)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _roles: Set[Role] = field(default_factory=set)
    _sessions: Set[Session] = field(default_factory=set)
    version: int = field(default=0, kw_only=True)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        username: Username,
        email: Email,
        password: Password,
        role: Role,
    ) -> Self:

        user = User(
            id=user_id,
            username=username,
            email=email,
            password=password,
        )

        user.add_role(role)

        return user

    def _set_jwt_user_data(self) -> None:
        permissions = set()
        roles = set()

        for role in self._roles:
            roles.add(role.name.to_raw())

            for permission in role.permission:
                permissions.add(permission.permission_name.to_raw())

        data = {
            "sub": self.id.to_raw(),
            "roles": list(roles),
            "permissions": list(permissions),
        }

        self.jwt_data = orjson.dumps(data)

    def add_role(self, role: Role) -> None:
        self._is_not_deleted()

        if role not in self._roles:
            self._roles.add(role)
            self._version_upgrade()
            self._set_jwt_user_data()

    def remove_role(self, role: Role) -> None:
        self._is_not_deleted()

        if role in self._roles:
            self._roles.remove(role)
            self._version_upgrade()
            self._set_jwt_user_data()

    def add_session(self, session: Session) -> None:
        self._is_not_deleted()

        if session not in self._sessions:
            self._sessions.add(session)
            self._version_upgrade()

    def remove_session(self, session: Session) -> None:
        self._is_not_deleted()

        if session in self._sessions:
            self._sessions.remove(session)
            self._version_upgrade()

    def set_username(self, username: Username) -> None:
        self._is_not_deleted()

        if username != self.username:
            self.username = username
            self._version_upgrade()

    def set_email(self, email: Email) -> None:
        self._is_not_deleted()

        if self.email != email:
            self.email = email
            self._version_upgrade()

    def set_password(self, old_pass: str, new_pass: str) -> None:
        self._is_not_deleted()
        self._pass_is_match(password=old_pass)

        self.password = Password.create(new_pass)

    def delete(self) -> None:
        if self.deleted_at is None:
            self.deleted_at = datetime.now(UTC)
            self._version_upgrade()

    def restore(self) -> None:
        if self.deleted_at:
            self.deleted_at = None
            self._version_upgrade()

    def _is_not_deleted(self):
        if self.deleted_at:
            raise UserIsDeletedException(user_id=self.id.to_raw())

    def _pass_is_match(self, password: str):
        if self.password.verify(password=password):
            raise PasswordDoesNotMatchException()

    def _version_upgrade(self) -> None:
        self.version += 1

    def as_dict(self):
        return {
            "id": self.id.to_raw(),
            "username": self.username.to_raw(),
            "email": self.email.to_raw(),
            "password": self.password.to_raw(),
            "jwt_data": self.jwt_data,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
            "updated_at": self.updated_at,
            "version": self.version,
        }

    @property
    def roles(self):
        return frozenset(self._roles)

    @property
    def sessions(self):
        return frozenset(self._sessions)
