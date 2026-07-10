"""行为日志写入工具。行为数据是 Hadoop 离线计算的原始输入。"""
import secrets
import sqlite3

from app.db.database import now_iso


ACTION_WEIGHTS = {
    "view": 1,
    "search_click": 2,
    "favorite": 3,
    "unfavorite": -2,
    "cart": 5,
    "purchase": 10,
    "refund": -8,
}


def insert_behavior(
    conn: sqlite3.Connection,
    *,
    user_id: int | None,
    action: str,
    session_id: str | None = None,
    product_id: int | None = None,
    product_name: str | None = None,
    category: str | None = None,
    quantity: int | None = None,
    sku_id: int | None = None,
    sku_name: str | None = None,
    order_id: int | None = None,
    amount: float | None = None,
    item_count: int | None = None,
    source: str | None = None,
) -> dict:
    if action not in ACTION_WEIGHTS:
        raise ValueError("不支持的行为类型")

    event_id = secrets.token_urlsafe(18)
    created_at = now_iso()
    cur = conn.execute(
        """
        INSERT INTO behavior_logs
          (event_id, user_id, session_id, product_id, product_name, action,
           category, quantity, sku_id, sku_name, order_id, amount, item_count,
           source, exported_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
        """,
        (
            event_id,
            user_id,
            session_id,
            product_id,
            product_name,
            action,
            category,
            quantity,
            sku_id,
            sku_name,
            order_id,
            amount,
            item_count,
            source,
            created_at,
        ),
    )
    return {"logId": cur.lastrowid, "eventId": event_id, "createdAt": created_at}
