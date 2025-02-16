from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from auth.tokens import generate_fake_token
from main import app

"""Тест для восстанволения заметки"""


@pytest.mark.asyncio
async def test_restore_note_success(mocker):

    mock_basket_collection = mocker.patch("notes.endpoints.basket_collection.find_one", new_callable=AsyncMock)
    mock_basket_collection.return_value = {
        "_id": "5f1a8c9e6ed5ef3a9405e209",
        "user_id": "333-Admin",
        "title": "Test Note",
        "body": "Test Body",
    }

    mock_insert = mocker.patch("notes.endpoints.notes_collection.insert_one", new_callable=AsyncMock)
    mock_delete = mocker.patch("notes.endpoints.basket_collection.delete_one", new_callable=AsyncMock)

    cookies = generate_fake_token(user_id="334-Admin")

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/notes/restore-note", json={"note_id": "5f1a8c9e6ed5ef3a9405e209"}, cookies=cookies
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Заметка успешно восстановлена"}

    mock_insert.assert_called_once()
    mock_delete.assert_called_once()
