from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from auth.endpoints import router as auth_router
from main import app

app.include_router(auth_router, prefix="/auth", tags=["auth"])

"""Тест для верификации кода"""


@pytest.mark.asyncio
async def test_verify_code_successful(mocker):

    mock_find_one_verification = mocker.patch(
        "auth.endpoints.verification_codes_collection.find_one", new_callable=AsyncMock
    )
    mock_find_one_user = mocker.patch("auth.endpoints.users_collection.find_one", new_callable=AsyncMock)

    mock_find_one_verification.return_value = {
        "email": "test@example.com",
        "code": int("12345"),
        "created_at": "some_date",
    }
    mock_find_one_user.return_value = {
        "_id": "some_user_id",
        "email": "test@example.com",
        "last_login": "some_date",
        "role": "User",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/v1/auth/verify-code", json={"email": "test@example.com", "code": "12345"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["message"] == "Успешный вход"

    mock_find_one_verification.assert_called_once_with({"email": "test@example.com"}, sort=[("created_at", -1)])
