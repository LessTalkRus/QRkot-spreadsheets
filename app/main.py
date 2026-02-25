from fastapi import FastAPI

from app.api.routers import main_router

app = FastAPI(
    title="Благотворительный фонд поддержки котиков QRKot",
    description="Сервис для поддержки котиков",
    version="0.1.0",
)

app.include_router(main_router)
