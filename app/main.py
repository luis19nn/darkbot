from fastapi import FastAPI
from app.workers import rabbitmq
from app.api.endpoints import bots

app = FastAPI()
app.include_router(bots.router)
