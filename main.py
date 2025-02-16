from fastapi import FastAPI

from auth.endpoints import router as auth_router
from notes.endpoints import router as notes_router

app = FastAPI(
    title="Notes API",
    description="""
## 📌 Описание  
Этот проект представляет собой API для управления заметками с поддержкой ролей пользователей (`User` и `Admin`).  
**Стек технологий:** FastAPI + MongoDB + JWT + Docker  

### 🚀 Основные функции:  
- 📌 **Регистрация** по email с кодом подтверждения  
- 🔑 **Авторизация** через JWT (токен хранится в куках)  
- 📝 **CRUD-операции** с заметками  
- 🛡️ **Разграничение доступа** (права `User` и `Admin`)  
- 📜 **Логирование** действий пользователей  
- 🐳 **Готовый Dockerfile** и `docker-compose.yml`  
- ⚙️ **Pytest** для тестирования эндпоинтов  
""",
    version="1.0.0",
)


app.include_router(auth_router, tags=["Auth🔑"])
app.include_router(notes_router, tags=["Notes📝"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
