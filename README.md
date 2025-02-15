
# 📝Notes API – Управление заметками и пользователями

## 📌 Описание
Этот проект представляет собой API для управления заметками с поддержкой ролей пользователей (User и Admin).  
**Стек технологий:** FastAPI + MongoDB + JWT + Docker .

## 🚀 Основные функции
- **📌 Регистрация по email с кодом подтверждения**
- **🔑 Авторизация через JWT (токен хранится в куках)**
- **📝 CRUD-операции с заметками**
- **🛡️ Разграничение доступа (права User и Admin)**
- **📜 Логирование действий пользователей**
- **📦 Готовый Dockerfile и docker-compose.yml**

## 📦 Установка и запуск

### 🐳 Запуск проекта в Docker
```bash
   git clone https://github.com/AlexKrutskikh/FreeVetbackend.git
   cd FreeVetbackend
   docker-compose up -d
  ```
### В процессе сборки запускаются три контейнера:

- 🚀 app – backend API

- 🗄️mongo_db – база данных

- 🔄  web – обратный прокси

После успешного запуска API будет доступно по адресу:
➡ http://localhost

### 🖥️ Локальный запуск
```bash
   git clone https://github.com/AlexKrutskikh/FreeVetbackend.git
   cd FreeVetbackend
   python main.py
  ```
#### Обновите переменные окружения в файле .env: 
###### Замените MONGO_HOST=mongo_db на MONGO_HOST=localhost.

###### Проект подключится к базе MONGO в ранее поднятом контейнере

## 🌐 Описание API:

### 📧 "/v1/auth/sent-code"
#### 📌 Отправка кода подтверждения на email.

Этот endpoint отправляет код подтверждения на указанный адрес электронной почты.

#### request-body:
```json
{
  "email": "krutskikh.ay@gmail.com"
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "message": "Код 10958 отправлен на krutskikh.ay@gmail.com"
}
```
###### 400 Bad Request:
```json
{
   "msg": "value is not a valid email address: An email address must have an @-sign."
}
```
### 🔐  "/v1/auth/verify-code"
#### 📌 Верификация кода.

Этот endpoint принимает код подтверждения и отправляет JWT токены в cookie
при успешном входе

#### request-body:
```json
{
    "email": "krutskikh.ay@gmail.com",
    "code":10958
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "message": "Успешный вход"
}
```
###### 400 Bad Request:
```json
{
    "detail": "Неверный код"
}
```
### 🔑  "/v1/refresh-token"
#### 📌 Обновление токенов.

Этот endpoint обновляет access_token и refresh_token 

#### request-body:
###### 200 OK (успешный запрос):
```json

{
    "success": true,
    "message": "Токен обновлен"
}
```
### 📧 "/v1/notes/create-notes"
#### 📌 Создание новой заметки.

Этот endpoint создает новую заметку, связывает ее с пользователем с помощью токена из cookie.

#### request-body:
```json
{
  "title": "string",
  "body": "string"
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "message": "Заметка создана",
    "note_id": "67b0a34a403bdd2109c7d4fe"
}
```
### 📧 "/v1/notes/update-note"
#### 📌 Обновление заметки.

Этот endpoint обновляет заметку.

#### request-body:
```json
{
  "note_id": "67b0a34a403bdd2109c7d4fe",
  "title": "string",
  "body": "string"
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "message": "Заметка обновлена"
}
```
###### 404 Bad Request:
```json
{
    "detail": "Заметка не найдена"
}
```
###### 403 Bad Request:
```json
{
    "detail": "Нет доступа к этой заметке"
}
```
### 📧 "/v1/notes/delete-note"
#### 📌 Удаление заметки.

Этот endpoint удаляет заметку.

#### request-body:
```json
{
  "note_id": "67b0a34a403bdd2109c7d4fe",
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "message": "Заметка перемещена в корзину"
}

```
###### 404 Bad Request:
```json
{
    "detail": "Заметка не найдена"
}
```
###### 403 Bad Request:
```json
{
    "detail": "Нет доступа к этой заметке"
}
```
###### 403 Bad Request:
```json
{
    "detail": "Перемещение в корзину доступно только пользователям с ролью 'User'",
}
```
### 📧 "/v1/notes/get-notes"
#### 📌 Получение всех заметок в зависимости от роли.

Этот endpoint отдает все заметки.

#### request-body:
```json
{
  "note_id": "67b0a34a403bdd2109c7d4fe",
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "notes": [
        {
            "_id": "67b0a34a403bdd2109c7d4fe",
            "title": "1",
            "body": "1",
            "created_at": "2025-02-15T17:23:06.871000",
            "updated_at": "2025-02-15T17:25:17.110000",
            "user_id": "67b09fb4e223fb830cec20bd-User"
        }
    ]
}

```
###### 403 Bad Request:
```json
{
    "detail": "Недостаточно прав для выполнения действия"
}
```
### 📧 "/v1/notes/get-note/"
#### 📌 Получение заметки в зависимости от роли..

Этот endpoint отдает  конкретную заметку.

#### request-body:
```json
{
  "note_id": "67b0a34a403bdd2109c7d4fe",
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "success": true,
    "note": {
        "_id": "67b0a34a403bdd2109c7d4fe",
        "title": "1",
        "body": "1",
        "created_at": "2025-02-15T17:23:06.871000",
        "updated_at": "2025-02-15T17:25:17.110000",
        "user_id": "67b09fb4e223fb830cec20bd-User"
    }
}

```
###### 404 Bad Request:
```json
{
    "detail": "Заметка не найдена"
}
```
###### 403 Bad Request:
```json
{
    "detail": "Нет доступа к этой заметке"
}
```
### 📧 "/v1/notes/restore-note"
#### 📌 Восстановление заметки.

Этот endpoint восстанавливает заметку из корзины.

#### request-body:
```json
{
  "note_id": "67b0a34a403bdd2109c7d4fe",
}
```
#### request-body:
###### 200 OK (успешный запрос):
```json
{
    "detail": "Заметка успешно восстановлена"
}

```
###### 404 Bad Request:
```json
{
    "detail": "Заметка не найдена в корзине"
}
```







