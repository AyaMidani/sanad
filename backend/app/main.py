from fastapi import FastAPI

from app.api.routes import health

app = FastAPI(title="Sanad")

app.include_router(health.router)
