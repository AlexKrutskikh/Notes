from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

"""Модель для заметки"""


class Notes(BaseModel):

    title: str = Field(..., max_length=256)
    body: str = Field(..., max_length=65536)
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: str = Field(..., description="Идентификатор пользователя, который создал заметку")
