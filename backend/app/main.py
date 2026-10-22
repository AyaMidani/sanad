from fastapi import FastAPI

from app.api.routes import ask, health

app = FastAPI(title="Sanad")

app.include_router(health.router)
app.include_router(ask.router)
