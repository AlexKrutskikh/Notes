import warnings
from unittest.mock import AsyncMock

warnings.filterwarnings("ignore", category=UserWarning, module="authx.token")


import pytest
from httpx import AsyncClient

from auth.endpoints import router as auth_router
from main import app

app.include_router(auth_router, prefix="/auth", tags=["auth"])

"""Тест успешной отправки кода"""


@pytest.mark.asyncio
async def test_request_code_successful(mocker):
    mock_insert = mocker.patch("auth.endpoints.verification_codes_collection.insert_one", new_callable=AsyncMock)
    mock_send_email = mocker.patch("auth.endpoints.send_verification_code", new_callable=AsyncMock)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/v1/auth/sent-code", json={"email": "test@example.com"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert "Код" in json_response["message"]

    mock_insert.assert_called_once()
    mock_send_email.assert_called_once_with("test@example.com", mocker.ANY)


"""Тест ошибки при записи в базу"""


@pytest.mark.asyncio
async def test_request_code_db_error(mocker):

    mock_insert = mocker.patch("auth.endpoints.verification_codes_collection.insert_one", new_callable=AsyncMock)
    mock_insert.side_effect = Exception("DB error")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/v1/auth/sent-code", json={"email": "test@example.com"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is False
    assert "DB error" in json_response["error"]


"""Тест ошибки при отправке кода"""


@pytest.mark.asyncio
async def test_request_code_email_error(mocker):

    mock_insert = mocker.patch("auth.endpoints.verification_codes_collection.insert_one", new_callable=AsyncMock)
    mock_send_email = mocker.patch("auth.endpoints.send_verification_code", new_callable=AsyncMock)
    mock_send_email.side_effect = Exception("Email send error")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/v1/auth/sent-code", json={"email": "test@example.com"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is False
    assert "Email send error" in json_response["error"]

    mock_insert.assert_called_once()
    mock_send_email.assert_called_once()
