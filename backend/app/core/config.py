"""应用配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("BACON_DB_PATH", str(BASE_DIR / "bacon_mall.db"))

_cors_raw = os.getenv("BACON_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

# MinIO 配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9002")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET_PRODUCTS = os.getenv("MINIO_BUCKET_PRODUCTS", "product-images")
MINIO_BUCKET_AVATARS = os.getenv("MINIO_BUCKET_AVATARS", "avatars")
MINIO_BUCKET_LOGOS = os.getenv("MINIO_BUCKET_LOGOS", "shop-logos")
