from fastapi import FastAPI
from app.api.endpoints import bots
from app.workers.rabbitmq import broker

app = FastAPI()
app.include_router(bots.router)

@app.on_event("startup")
async def startup():
    await broker.connect()

@app.on_event("shutdown")
async def shutdown():
    await broker.close()
