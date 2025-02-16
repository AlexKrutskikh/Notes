from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from auth.tokens import generate_fake_token
from main import app

"""Тест для создания заметки"""


@pytest.mark.asyncio
async def test_create_notes_success_without_token(mocker):

    mock_insert = mocker.patch("notes.endpoints.notes_collection.insert_one", new_callable=AsyncMock)

    mock_insert.return_value.inserted_id = "note_id"

    cookies = generate_fake_token(user_id="123")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/notes/create-notes",
            json={"title": "Test Note", "body": "This is a test note."},
            cookies=cookies,
        )

    assert response.status_code == 201

    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["message"] == "Заметка создана"
    assert json_response["note_id"] == "note_id"
