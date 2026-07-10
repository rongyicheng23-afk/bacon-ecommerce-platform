"""行为日志 & 浏览足迹 & 推荐路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Query
from app.schemas.common import ApiResponse
from app.schemas.behavior import BehaviorLogCreate
from app.services.auth import get_current_user
from app.services.product import list_products
from app.db.database import get_connection, now_iso

router = APIRouter(prefix="/api", tags=["行为 & 推荐"])

AUTH = Annotated[str | None, Header()]


@router.post("/behaviors", response_model=ApiResponse)
def create_behavior(payload: BehaviorLogCreate, authorization: AUTH = None) -> ApiResponse:
    user = get_current_user(authorization)
    user_id = user["userId"] if user else payload.userId
    ts = now_iso()
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO behavior_logs (user_id, product_id, product_name, action, category, quantity, sku_id, sku_name, order_id, amount, item_count, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (user_id, payload.productId, payload.productName, payload.action,
             payload.category, payload.quantity, payload.skuId, payload.skuName,
             payload.orderId, payload.amount, payload.itemCount, ts),
        )
    return ApiResponse(data={"logId": cur.lastrowid, "createdAt": ts})


@router.get("/history", response_model=ApiResponse)
def browsing_history(authorization: AUTH = None) -> ApiResponse:
    user = get_current_user(authorization)
    if not user: raise HTTPException(401, "请先登录")
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM behavior_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 200",
            (user["userId"],),
        ).fetchall()
    return ApiResponse(data=[{
        "userId": r["user_id"], "productId": r["product_id"],
        "productName": r["product_name"], "action": r["action"],
        "category": r["category"], "timestamp": r["created_at"],
    } for r in rows])


@router.delete("/history", response_model=ApiResponse)
def clear_history(authorization: AUTH = None) -> ApiResponse:
    user = get_current_user(authorization)
    if not user: raise HTTPException(401, "请先登录")
    with get_connection() as conn:
        conn.execute("DELETE FROM behavior_logs WHERE user_id = ?", (user["userId"],))
    return ApiResponse(data=None)


@router.get("/recommendations", response_model=ApiResponse)
def recommendations(
    authorization: AUTH = None,
    userId: int | None = None,
    limit: int = Query(20, ge=1, le=60),
) -> ApiResponse:
    user = get_current_user(authorization)
    real_uid = user["userId"] if user else userId

    with get_connection() as conn:
        cats: list[str] = []
        if real_uid:
            rows = conn.execute(
                """SELECT category, COUNT(*) AS score FROM behavior_logs
                   WHERE user_id = ? AND category IS NOT NULL AND category != '订单'
                   GROUP BY category ORDER BY score DESC LIMIT 3""",
                (real_uid,),
            ).fetchall()
            cats = [r["category"] for r in rows]

    result = list_products(page=1, page_size=100)
    items = result["items"]
    if not cats:
        return ApiResponse(data=items[:limit])

    ranked = sorted(items, key=lambda p: (0 if p["category"] in cats else 1, -p["stock"]))
    return ApiResponse(data=ranked[:limit])
