from fastapi import FastAPI
from app.workers import rabbitmq
from app.api import darkbot

app = FastAPI()
app.include_router(darkbot.router)
