"""Bacon Mall API — FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import CORS_ORIGINS
from app.db.database import init_db
from app.routers import auth, products, carts, orders, sellers, behaviors, frontend_compat, media


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
app.include_router(frontend_compat.router)
app.include_router(media.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Bacon Mall backend is running"}


# 挂载本地上传目录（MinIO 不可用时的回退方案）
import os
from pathlib import Path
_upload_dir = Path(__file__).resolve().parent.parent / "uploads"
os.makedirs(_upload_dir, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=str(_upload_dir)), name="uploads")
