"""应用配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("BACON_DB_PATH", str(BASE_DIR / "bacon_mall.db"))

CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
