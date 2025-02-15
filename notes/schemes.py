from typing import Optional

from pydantic import BaseModel

"""Модель для заметки, используемая в запросах и ответах"""


class NoteSchema(BaseModel):

    note_id: Optional[str] = ""
    title: Optional[str] = ""
    body: Optional[str] = ""
