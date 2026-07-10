"""Bacon Mall API — FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.db.database import init_db
from app.routers import auth, products, carts, orders, sellers, behaviors


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Bacon Mall API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(carts.router)
app.include_router(orders.router)
app.include_router(sellers.router)
app.include_router(behaviors.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Bacon Mall backend is running"}
