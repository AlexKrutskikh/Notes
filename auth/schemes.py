from pydantic import BaseModel, EmailStr

"""Схема запроса кода подтверждения"""


class RequestCodeSchema(BaseModel):
    email: EmailStr


"""Схема проверки кода подтверждения"""


class VerifyCodeSchema(BaseModel):
    email: EmailStr
    code: int


"""Схема для смены роли"""


class ChangeRoleSchema(BaseModel):
    user_id: str
    role: str
    secret_key: str
