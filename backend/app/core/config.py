"""应用配置"""
import os
from pathlib import Path

# 自动加载 .env（若 python-dotenv 可用）
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("BACON_DB_PATH") or str(BASE_DIR / "bacon_mall.db")

_cors_raw = os.getenv("BACON_CORS_ORIGINS") or "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://localhost:5173,http://localhost:5174,http://localhost:5175"
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

# MinIO 配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT") or "127.0.0.1:9000"
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY") or "minioadmin"
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY") or "minioadmin"
MINIO_SECURE = (os.getenv("MINIO_SECURE") or "false").lower() == "true"
MINIO_BUCKET_PRODUCTS = os.getenv("MINIO_BUCKET_PRODUCTS") or "product-images"
MINIO_BUCKET_AVATARS = os.getenv("MINIO_BUCKET_AVATARS") or "avatars"
MINIO_BUCKET_LOGOS = os.getenv("MINIO_BUCKET_LOGOS") or "shop-logos"
