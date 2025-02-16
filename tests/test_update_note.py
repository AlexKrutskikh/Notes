from unittest.mock import AsyncMock

import pytest
from bson import ObjectId
from httpx import AsyncClient

from auth.tokens import generate_fake_token
from main import app

"""Тест для обновления заметки"""


@pytest.mark.asyncio
async def test_update_note_success(mocker):

    mock_update = mocker.patch("notes.endpoints.notes_collection.update_one", new_callable=AsyncMock)

    mock_update.return_value.modified_count = 1

    mock_find = mocker.patch("notes.endpoints.notes_collection.find_one", new_callable=AsyncMock)
    mock_find.return_value = {
        "_id": ObjectId("5f1a8c9e6ed5ef3a9405e207"),
        "user_id": "123",
        "title": "Test Note",
        "body": "Test Body",
    }

    cookies = generate_fake_token(user_id="123")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/notes/update-note",
            json={"note_id": "5f1a8c9e6ed5ef3a9405e207", "title": "Updated Note", "body": "Updated Body"},
            cookies=cookies,
        )

    assert response.status_code == 200

    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["message"] == "Заметка обновлена"
