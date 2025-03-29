user_create = (
    "userdata, expected_status, expected_response_detail",
    [
        # Success case
        (
            {
                "user_id": "existing_id",
                "username": "existing_user",
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "Smith",
            },
            201,
            {
                "is_deleted": False,
                "user_id": "existing_id",
                "username": "existing_user",
            },
        ),
        # Pydantic validation failures
        (
            {},
            422,
            {
                "detail": [
                    {
                        "input": {},
                        "loc": ["body", "user_id"],
                        "msg": "Field required",
                        "type": "missing",
                    },
                    {
                        "input": {},
                        "loc": ["body", "username"],
                        "msg": "Field required",
                        "type": "missing",
                    },
                    {
                        "input": {},
                        "loc": ["body", "first_name"],
                        "msg": "Field required",
                        "type": "missing",
                    },
                    {
                        "input": {},
                        "loc": ["body", "last_name"],
                        "msg": "Field required",
                        "type": "missing",
                    },
                ]
            },
        ),
        (
            {
                "user_id": 12345,  # Not a string
                "username": "valid_user",
                "first_name": "John",
                "last_name": "Doe",
            },
            422,
            {
                "detail": [
                    {
                        "input": 12345,
                        "loc": ["body", "user_id"],
                        "msg": "Input should be a valid string",
                        "type": "string_type",
                    }
                ]
            },
        ),
        # Domain validation failures
        (
            {
                "user_id": "usr12345",
                "username": "a",  # Too short username
                "first_name": "John",
                "last_name": "Doe",
            },
            422,
            {
                "error": {
                    "message": "Username a has wrong format!",
                    "type": "WrongUsernameFormatException",
                }
            },
        ),
        (
            {
                "user_id": "usr123452",
                "username": "existing_user",  # Already exists
                "first_name": "John",
                "last_name": "Doe",
            },
            409,
            {
                "error": {
                    "message": "Given username: 'existing_user' already exists",
                    "type": "UsernameAlreadyExistsException",
                }
            },
        ),
        (
            {
                "user_id": "existing_id",  # Already exists
                "username": "new_user",
                "first_name": "Jane",
                "last_name": "Smith",
            },
            409,
            {
                "error": {
                    "message": 'A user with the "existing_id" user_id already exists',
                    "type": "UserIdAlreadyExistsErrorException",
                }
            },
        ),
    ],
)

user_update_username = (
    "user_id, userdata, expected_status, expected_response_detail",
    [
        # Pydantic validation failures
        (
            "usr12345",
            {
                "username": 123,  # Not a string
            },
            422,
            {
                "detail": [
                    {
                        "input": 123,
                        "loc": ["body", "username"],
                        "msg": "Input should be a valid string",
                        "type": "string_type",
                    }
                ]
            },
        ),
        # Domain validation failures
        (
            "non_existent_id",
            {
                "username": "new_username",
            },
            404,
            {
                "error": {
                    "message": "User with specified ID does not exist",
                    "type": "UserDoesNotExistException",
                }
            },
        ),
        (
            "usr12345",
            {"username": "existing_user"},  # Already taken
            409,
            {
                "error": {
                    "message": "Username already exists",
                    "type": "UsernameAlreadyExistsException",
                }
            },
        ),
        (
            "usr12345",
            {"first_name": "J0hn"},  # Invalid format (contains numbers)
            422,
            {
                "error": {
                    "message": "First name must contain only letters",
                    "type": "ValidationException",
                }
            },
        ),
        (
            "deleted_user_id",
            {"username": "new_name"},
            410,
            {
                "error": {
                    "message": "User has been deleted",
                    "type": "UserIsDeletedException",
                }
            },
        ),
        # Success case
        (
            "usr12345",
            {"username": "updated_user", "first_name": "Jane", "last_name": "Smith"},
            200,
            {
                "user_id": "usr12345",
                "username": "updated_user",
                "first_name": "Jane",
                "last_name": "Smith",
                "middle_name": "Smith",  # Assuming this is retained from original
            },
        ),
    ],
)
