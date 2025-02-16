from datetime import datetime, timedelta

from fastapi import Response

from settings import security

"""Генерирует и устанавливает access и refresh токены в куки"""


def generate_and_set_tokens(user, response: Response) -> Response:
    user_id = str(user["_id"])
    role = user["role"]

    access_token = security.create_access_token(
        subject=user_id, expires_in=timedelta(hours=10), uid=f"{user_id}-{role}"
    )

    refresh_token = security.create_refresh_token(
        subject=user_id, expires_in=datetime.now() + timedelta(days=7), uid=f"{user_id}-{role}"
    )

    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=timedelta(hours=10))
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=timedelta(days=7))

    return response


"""Генерирует фейкового токена для теста"""


def generate_fake_token(user_id):

    access_token = security.create_access_token(subject=user_id, expires_in=timedelta(hours=10), uid=user_id)

    refresh_token = security.create_refresh_token(
        subject=user_id, expires_in=datetime.now() + timedelta(days=7), uid=user_id
    )

    return {"access_token": access_token, "refresh_token": refresh_token}
