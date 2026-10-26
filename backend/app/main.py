from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, conversations, health

app = FastAPI(title="Sanad")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://sanad-kappa-nine.vercel.app"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-Visitor-Id"],
)

app.include_router(health.router)
app.include_router(ask.router)
app.include_router(conversations.router)
