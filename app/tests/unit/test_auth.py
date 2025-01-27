from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.parametrize(
    "email, user_in_db, expected_status, expected_message",
    [
        ("user@example.com", None, 201, {"message": "Вы успешно зарегистрированы!"}),
        ("user@example.com", MagicMock(), 409, {"detail": "Пользователь уже существует"}),
    ],
    ids=["success", "user already exists"],
)
@pytest.mark.asyncio
async def test_register_user(
    client,
    email,
    user_in_db,
    expected_status,
    expected_message,
):
    data = {
        "email": email,
        "phone_number": "+777777",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
        "confirm_password": "string",
    }

    # with patch("app.api.auth.dao.UsersDAO.find_one_or_none", return_value=None):
    with patch("app.api.auth.dao.UsersDAO.find_one_or_none") as mock_find:
        mock_find.return_value = user_in_db

        response = await client.post("/register", json=data)
        assert response.status_code == expected_status
        assert response.json() == expected_message
