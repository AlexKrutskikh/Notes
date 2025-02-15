from fastapi import FastAPI

from auth.endpoints import router as auth_router
from notes.endpoints import router as notes_router

app = FastAPI()

app.include_router(auth_router, tags=["auth"])
app.include_router(notes_router, tags=["notes"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
