from typing import re

from tests.conftest import client
from tests.parametrize_data import user_create, user_update_username
import pytest

parametrize = pytest.mark.parametrize


async def test_create_and_get_user():
    data = {
        "user_id": "test_user_id",
        "username": "test_username",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "middle_name": "test_middle_name",
    }

    response = client.post("/user/", json=data)

    response_data = response.json()

    assert response.status_code == 201
    assert response_data["user_id"] == "test_user_id"
    assert response_data["username"] == "test_username"

    response = client.get("/user/test_user_id")
    assert response.status_code == 200


def test_get_user(create_test_user):
    response = client.get("/user/user_id")
    assert response.status_code == 200


@parametrize(*user_create)
def test_create_user_use_cases(
    userdata, expected_status, expected_response_detail, create_test_user
):
    response = client.post("/user/", json=userdata)

    if response.status_code == 201:
        for k, v in expected_response_detail.items():
            assert response.json()[k] == v
        assert "created_at" in response.json()

    else:
        assert response.status_code == expected_status
        assert response.json() == expected_response_detail


# @parametrize(*user_update_username)
# def test_update_user_use_cases(
#     user_id, userdata, expected_status, expected_response_detail, create_test_user
# ):
#     response = client.put(f"/{user_id}/username", json=userdata)
#
#     assert response.status_code == expected_status
#     assert response.json() == expected_response_detail
#

# async def test_create_user(test_client):
#     response = await test_client.post(
#         "/user/",
#         json={
#             "user_id": "test_user_id",
#             "username": "test_username",
#             "first_name": "test_first_name",
#             "last_name": "test_last_name",
#             "middle_name": "test_middle_name",
#         },
#     )
#     print(response.json())
#     assert response.status_code == 201
