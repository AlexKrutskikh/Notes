import secrets
from datetime import datetime

from authx import TokenPayload
from bson import ObjectId
from fastapi import Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from auth.models import UserModel, VerifyCode
from auth.schemes import ChangeRoleSchema, RequestCodeSchema, VerifyCodeSchema
from auth.tokens import generate_and_set_tokens
from auth.utils import send_verification_code
from settings import (
    KEY_ROLE,
    logger,
    router,
    security,
    users_collection,
    verification_codes_collection,
)

"""Отправка кода подтверждения на email"""


@router.post("/v1/auth/sent-code", operation_id="send_verification_code")
async def request_code(data: RequestCodeSchema):
    code = int("".join(secrets.choice("0123456789") for _ in range(5)))

    try:
        verification_code = VerifyCode(email=data.email, code=code, created_at=datetime.now())
        await verification_codes_collection.insert_one(verification_code.model_dump())
        await send_verification_code(data.email, code)

        logger.info(f"Код подтверждения отправлен на {data.email}. Код: {code}")

        return {"success": True, "message": f"Код {code} отправлен на {data.email}"}
    except Exception as e:
        logger.error(f"Ошибка при отправке кода на {data.email}: {str(e)}")
        return {"success": False, "error": str(e)}


"""Проверка введенного пользователем кода и аутентификация"""


@router.post("/v1/auth/verify-code", operation_id="validate_verification_code")
async def verify_code(data: VerifyCodeSchema):
    verification = await verification_codes_collection.find_one({"email": data.email}, sort=[("created_at", -1)])

    if not verification:
        logger.warning(f"Код не найден для {data.email}")
        raise HTTPException(status_code=400, detail="Код не найден")

    if verification["code"] != data.code:
        print(data.code)
        print(verification["code"])
        logger.warning(f"Неверный код для {data.email}. Введенный код: {data.code}")
        raise HTTPException(status_code=400, detail="Неверный код")

    existing_user = await users_collection.find_one({"email": data.email})

    if existing_user is not None:
        await users_collection.update_one({"email": data.email}, {"$set": {"last_login": datetime.now()}})

        response = JSONResponse(content={"success": True, "message": "Успешный вход"})
        logger.info(f"Пользователь {data.email} успешно вошел в систему.")

        return generate_and_set_tokens(existing_user, response)

    else:
        new_user = UserModel(
            name=None,
            last_name=None,
            email=data.email,
            registration_time=datetime.now(),
            last_login=None,
        )

        await users_collection.insert_one(new_user.model_dump())

        response = JSONResponse(content={"success": True, "message": "Пользователь зарегистрирован"})
        logger.info(f"Новый пользователь зарегистрирован: {data.email}")

        return generate_and_set_tokens(new_user, response)


"""Обновление токена на основе refresh-токена"""


@router.post("/v1/refresh-token")
async def refresh(refresh_payload: TokenPayload = Depends(security.refresh_token_required)) -> Response:
    try:
        user_id, role = refresh_payload.sub.split("-")
    except ValueError:
        user_id = refresh_payload.sub

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        logger.warning(f"Попытка обновления токена для несуществующего пользователя: {refresh_payload.sub}")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    response = JSONResponse(content={"success": True, "message": "Токен обновлен"})
    logger.info(f"Токен обновлен для пользователя: {refresh_payload.sub}")

    return generate_and_set_tokens(user, response)


@router.post("/v1/users/change-role", operation_id="change_user_role")
async def change_user_role(data: ChangeRoleSchema):
    try:
        user_id = ObjectId(data.user_id)  # Преобразуем строку в ObjectId
    except Exception as e:
        logger.error(f"Ошибка преобразования ID: {data.user_id}, ошибка: {e}")
        raise HTTPException(status_code=400, detail="Неверный формат ID")

    user = await users_collection.find_one({"_id": user_id})

    if not user:
        logger.warning(f"Пользователь с ID {data.user_id} не найден.")
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if data.secret_key != KEY_ROLE:
        logger.warning(f"Неверный секретный ключ для пользователя {data.user_id}")
        raise HTTPException(status_code=403, detail="Неверный секретный ключ")

    if data.role not in ["User", "Admin"]:
        logger.warning(f"Неверная роль: {data.role} для пользователя {data.user_id}")
        raise HTTPException(status_code=400, detail="Неверная роль. Доступны только 'User' и 'Admin'")

    result = await users_collection.update_one(
        {"_id": user_id}, {"$set": {"role": data.role, "last_login": datetime.now()}}
    )

    if result.matched_count == 0:
        logger.error(f"Не удалось обновить роль пользователя {data.user_id}. Возможно, пользователь не существует.")
        raise HTTPException(status_code=500, detail="Не удалось обновить роль пользователя")

    logger.info(f"Роль пользователя {data.user_id} изменена на {data.role}")

    response = JSONResponse(
        content={"success": True, "message": f"Роль пользователя {data.user_id} изменена на {data.role}"}
    )
    return response
