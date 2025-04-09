import orjson
import src.domain as domain

from src.application.base.security.jwt_user import JWTUserInterface
from dataclasses import dataclass, field
from typing import List, Self, Dict, Any

from src.application.dto.token import Token


@dataclass
class SecurityUser(JWTUserInterface):
    id: str
    roles: List[str]
    permissions: List[str]
    security_level: int | None = field(default=None)
    device_id: str | None = field(default=None)

    @classmethod
    def create_from_domain_user(cls, domain_user: domain.User) -> Self:
        if domain_user.jwt_data is None:
            domain_user._set_jwt_user_data()

        jwt_data = orjson.loads(domain_user.jwt_data)

        return cls(
            id=jwt_data["sub"],
            roles=jwt_data["roles"],
            permissions=jwt_data["permissions"],
        )

    @classmethod
    def create_from_jwt_data(
        cls, jwt_data: bytes, device_id: str | None = None
    ) -> Self:
        data = orjson.loads(jwt_data)

        return cls(
            id=data["sub"],
            device_id=device_id,
            security_level=data["lvl"],
            roles=data["roles"],
            permissions=data["permissions"],
        )

    @classmethod
    def create_from_payload(cls, payload: Dict[str, Any]) -> Self:
        return cls(
            id=payload["sub"],
            roles=payload["roles"],
            security_level=payload["lvl"],
            device_id=payload["device_id"],
            permissions=payload["permissions"],
        )

    @classmethod
    def create_from_token_dto(cls, token_dto: Token) -> Self:
        return cls(
            id=token_dto.sub,
            device_id=token_dto.did,
            security_level=token_dto.lvl,
            roles=token_dto.roles,
            permissions=token_dto.permissions,
        )

    def set_device_id(self, device_id: str) -> None:
        self.device_id = device_id

    def get_roles(self) -> List[str]:
        return self.roles

    def get_permissions(self) -> List[str]:
        return self.permissions

    def get_user_identifier(self) -> str:
        return self.id

    def get_device_id(self) -> str | None:
        return self.device_id

    def get_security_level(self) -> int | None:
        return self.security_level
