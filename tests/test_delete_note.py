from unittest.mock import ANY, AsyncMock

import pytest
from bson import ObjectId
from httpx import AsyncClient

from auth.tokens import generate_fake_token
from main import app

"""Тест для удаления заметки"""


@pytest.mark.asyncio
async def test_delete_note_success(mocker):

    mock_find = mocker.patch("notes.endpoints.notes_collection.find_one", new_callable=AsyncMock)
    mock_find.return_value = {
        "_id": ObjectId("5f1a8c9e6ed5ef3a9405e211"),
        "user_id": "334-User",
        "title": "Test Note",
        "body": "Test Body",
    }

    mock_insert = mocker.patch("notes.endpoints.basket_collection.insert_one", new_callable=AsyncMock)
    mock_delete = mocker.patch("notes.endpoints.notes_collection.delete_one", new_callable=AsyncMock)

    cookies = generate_fake_token(user_id="334-User")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/notes/delete-note",
            json={"note_id": "5f1a8c9e6ed5ef3a9405e211"},
            cookies=cookies,
        )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["message"] == "Заметка перемещена в корзину"

    mock_insert.assert_called_once_with(
        {
            "_id": ObjectId("5f1a8c9e6ed5ef3a9405e211"),
            "user_id": "334-User",
            "title": "Test Note",
            "body": "Test Body",
            "deleted_at": ANY,
        }
    )
    mock_delete.assert_called_once_with({"_id": ObjectId("5f1a8c9e6ed5ef3a9405e211")})
