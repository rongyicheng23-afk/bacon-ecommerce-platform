"""数据库连接与基础操作"""
import sqlite3
from datetime import datetime

from app.core.config import DB_PATH


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """创建所有表并写入种子数据"""
    from app.db.models import create_tables
    from app.db.seed import seed_demo_data

    with get_connection() as conn:
        create_tables(conn)
        seed_demo_data(conn)
