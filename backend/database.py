"""兼容旧导入；新代码应从 app.db.database 和 app.core.security 导入。"""
from app.core.security import hash_password, verify_password
from app.db.database import get_connection, init_db, now_iso


__all__ = ["get_connection", "hash_password", "init_db", "now_iso", "verify_password"]
