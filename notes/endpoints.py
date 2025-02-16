from datetime import datetime

from authx import TokenPayload
from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from notes.models import Notes
from notes.schemes import NoteSchema
from notes.utils import serialize_data
from settings import basket_collection, logger, notes_collection
from settings import router_auth as router
from settings import security

"""Создание новой заметки"""


@router.post("/v1/notes/create-notes", operation_id="create_new_note")
async def create_notes(data: NoteSchema, payload: TokenPayload = Depends(security.access_token_required)):
    try:

        note = Notes(title=data.title, body=data.body, created_at=datetime.now(), user_id=payload.sub)

        note_inf = await notes_collection.insert_one(note.model_dump())

        logger.info(f"Создана новая заметка. ID: {str(note_inf.inserted_id)}, Пользователь: {payload.sub}")

        return JSONResponse(
            content={"success": True, "message": "Заметка создана", "note_id": str(note_inf.inserted_id)},
            status_code=201,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")


"""Обновление заметки"""


@router.post("/v1/notes/update-note", operation_id="update_note")
async def update_note(data: NoteSchema, payload: TokenPayload = Depends(security.access_token_required)):
    try:

        note = await notes_collection.find_one({"_id": ObjectId(data.note_id)})
        if not note:
            raise HTTPException(status_code=404, detail="Заметка не найдена")

        if note["user_id"] != payload.sub:
            raise HTTPException(status_code=403, detail="Нет доступа к этой заметке")

        update_data = {"title": data.title, "body": data.body, "updated_at": datetime.now()}
        await notes_collection.update_one({"_id": ObjectId(data.note_id)}, {"$set": update_data})

        logger.info(f"Заметка обновлена. ID: {data.note_id}, Пользователь: {payload.sub}")

        return JSONResponse(content={"success": True, "message": "Заметка обновлена"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")


"""Удаление заметки (перемещение в корзину)"""


@router.post("/v1/notes/delete-note", operation_id="delete_note")
async def delete_note(data: NoteSchema, payload: TokenPayload = Depends(security.access_token_required)):

    try:

        user_id, role = payload.sub.split("-")

        note = await notes_collection.find_one({"_id": ObjectId(data.note_id)})
        if not note:
            raise HTTPException(status_code=404, detail="Заметка не найдена")

        if note["user_id"] != payload.sub:

            raise HTTPException(status_code=403, detail="Нет доступа к этой заметке")

        if role != "User":

            raise HTTPException(
                status_code=403, detail="Перемещение в корзину доступно только пользователям с ролью 'User'"
            )

        note["deleted_at"] = datetime.now()
        await basket_collection.insert_one(note)

        await notes_collection.delete_one({"_id": ObjectId(data.note_id)})

        logger.info(f"Заметка перемещена в корзину. ID: {data.note_id}, Пользователь: {payload.sub}")

        return JSONResponse(content={"success": True, "message": "Заметка перемещена в корзину"}, status_code=200)

    except Exception as e:

        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")


"""Получение всех заметок (для администратора) или своих заметок (для пользователя)"""


@router.get("/v1/notes/get-notes", operation_id="get_notes")
async def get_notes(payload: TokenPayload = Depends(security.access_token_required)):
    try:
        user_id, role = payload.sub.split("-")

        if role == "Admin":
            notes_cursor = await notes_collection.find().to_list(None)
        elif role == "User":

            notes_cursor = await notes_collection.find({"user_id": payload.sub}).to_list(None)
        else:
            raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения действия")

        notes = serialize_data(notes_cursor)

        return JSONResponse(content={"success": True, "notes": notes}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")


"""Получение одной заметки"""


@router.get("/v1/notes/get-note/", operation_id="get_note")
async def get_note(data: NoteSchema, payload: TokenPayload = Depends(security.access_token_required)):
    try:
        user_id, role = payload.sub.split("-")

        try:
            note_object_id = ObjectId(data.note_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Неверный формат ID заметки")

        note = await notes_collection.find_one({"_id": note_object_id})

        if not note:
            raise HTTPException(status_code=404, detail="Заметка не найдена")

        if role == "User" and note["user_id"] != payload.sub:
            raise HTTPException(status_code=403, detail="Нет доступа к этой заметке")

        note_data = serialize_data(note)

        return JSONResponse(content={"success": True, "note": note_data}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")


"""Восстановление удаленной заметки (для администратора)"""


@router.post("/v1/notes/restore-note", operation_id="restore_note")
async def restore_note(data: NoteSchema, payload: TokenPayload = Depends(security.access_token_required)):
    try:
        user_id, role = payload.sub.split("-")

        if role != "Admin":
            raise HTTPException(
                status_code=403, detail="Доступ запрещён. Только администратор может восстанавливать заметки."
            )

        try:
            note_object_id = ObjectId(data.note_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Неверный формат ID заметки")

        note = await basket_collection.find_one({"_id": note_object_id})
        if not note:
            raise HTTPException(status_code=404, detail="Заметка не найдена в корзине")

        note.pop("deleted_at", None)

        await notes_collection.insert_one(note)

        await basket_collection.delete_one({"_id": note_object_id})

        logger.info(f"Заметка восстановлена. ID: {data.note_id}, Администратор: {payload.sub}")

        return JSONResponse(content={"success": True, "message": "Заметка успешно восстановлена"}, status_code=200)

    except Exception as e:

        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")
