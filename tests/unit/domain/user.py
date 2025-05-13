from uuid6 import uuid7

from src.domain.permission.entity.permission import Permission
from src.domain.permission.values import PermissionName
from src.domain.role.entity.role import Role
from src.domain.role.values import RoleName
from src.domain.user.entity.user import User
from src.domain.user.values import Email, Password, UserId, Username


async def test_create_user():
    user_id = UserId(value=str(uuid7()))
    username = Username(value="test_user")
    email = Email(value="test_email@test.com")
    password = Password.create("te1stpa1SSword")

    write: Permission = Permission(PermissionName("write"))
    read: Permission = Permission(PermissionName("read"))

    user_role: Role = Role(name=RoleName("user"))
    user_role.add_permission(read)

    moderator: Role = Role(name=RoleName("moderator"))
    moderator.add_permission(read)
    moderator.add_permission(write)

    user = User.create(
        user_id=user_id,
        username=username,
        email=email,
        password=password,
        role=user_role,
    )

    assert user.id == user_id
    assert user.username == username
    assert user.email == email
