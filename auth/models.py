from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, conint

"""Модель пользователя в системе"""


class UserModel(BaseModel):
    name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: EmailStr
    role: str = "User"
    registration_time: datetime
    last_login: Optional[datetime] = None


"""Модель кода подтверждения для верификации email"""


class VerifyCode(BaseModel):
    email: EmailStr
    code: conint(ge=0, le=99999)
    created_at: datetime
