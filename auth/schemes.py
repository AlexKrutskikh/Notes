from pydantic import BaseModel, EmailStr

"""Схема запроса кода подтверждения"""


class RequestCodeSchema(BaseModel):
    email: EmailStr


"""Схема проверки кода подтверждения"""


class VerifyCodeSchema(BaseModel):
    email: EmailStr
    code: int
