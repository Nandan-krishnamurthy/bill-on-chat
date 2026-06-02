from fastapi import FastAPI

from app.routes.chat import router as chat_router


app = FastAPI(title="Project Beta API", version="0.1.0")
app.include_router(chat_router)
