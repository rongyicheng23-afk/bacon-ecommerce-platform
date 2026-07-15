"""认证业务逻辑"""
import sqlite3
from datetime import datetime, timedelta

from app.core.security import generate_token, hash_password, verify_password
from app.db.database import get_connection, now_iso


def _session_expiry() -> str:
    return (datetime.now() + timedelta(days=7)).isoformat(timespec="seconds")


def row_to_user(row) -> dict:
    return {
        "userId": row["user_id"], "username": row["username"],
        "email": row["email"], "phone": row["phone"] or "",
        "role": row["role"], "shopName": row["shop_name"],
        "mainCategory": row["main_category"], "status": row["status"],
        "createdAt": row["created_at"], "updatedAt": row["updated_at"],
    }


def get_current_user(token: str | None) -> dict | None:
    if not token or not token.startswith("Bearer "):
        return None
    token = token.removeprefix("Bearer ").strip()
    with get_connection() as conn:
        row = conn.execute(
            """SELECT u.* FROM sessions s
               JOIN users u ON u.user_id = s.user_id
               WHERE s.token = ?
                 AND u.status = 'active'
                 AND (s.expires_at IS NULL OR s.expires_at > ?)""",
            (token, now_iso()),
        ).fetchone()
        return row_to_user(row) if row else None


def register_user(data: dict) -> dict:
    ts = now_iso()
    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email = ?", (data["email"],)).fetchone():
            raise ValueError("该邮箱已经注册")
        cur = conn.execute(
            """INSERT INTO users (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (data["username"], data["email"], data.get("phone", ""), data["role"],
             data.get("shopName"), data.get("mainCategory"),
             hash_password(data["password"]), "active", ts, ts),
        )
        user_id = cur.lastrowid
        # 商家注册时自动创建店铺
        if data["role"] == "seller":
            shop_name = data.get("shopName") or f"{data['username']}的店铺"
            conn.execute(
                "INSERT INTO shops (owner_user_id, name, status, created_at, updated_at) VALUES (?,?,?,?,?)",
                (user_id, shop_name, "active", ts, ts),
            )
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        token = generate_token()
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?,?,?,?)",
            (token, user["user_id"], ts, _session_expiry()),
        )
    return {"token": token, "user": row_to_user(user)}


def login_user(email: str, password: str) -> dict:
    ts = now_iso()
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or not verify_password(password, user["password_hash"]):
            raise ValueError("邮箱或密码不正确")
        token = generate_token()
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?,?,?,?)",
            (token, user["user_id"], ts, _session_expiry()),
        )
    return {"token": token, "user": row_to_user(user)}


def logout_user(token: str | None) -> None:
    if not token or not token.startswith("Bearer "):
        return
    token = token.removeprefix("Bearer ").strip()
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def update_profile(user_id: int, data: dict) -> dict:
    ts = now_iso()
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET username = COALESCE(?, username), phone = COALESCE(?, phone), updated_at = ? WHERE user_id = ?",
            (data.get("username"), data.get("phone"), ts, user_id),
        )
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row_to_user(row)
