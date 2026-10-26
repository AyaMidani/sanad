from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, health

app = FastAPI(title="Sanad")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)
app.include_router(ask.router)
