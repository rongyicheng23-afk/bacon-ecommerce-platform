"""行为日志 & 浏览足迹 & 推荐路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Query
from app.schemas.common import ApiResponse
from app.schemas.behavior import BehaviorLogCreate
from app.services.auth import get_current_user
from app.services.behavior import insert_behavior
from app.services.product import list_products
from app.db.database import get_connection, now_iso

router = APIRouter(prefix="/api", tags=["行为 & 推荐"])

AUTH = Annotated[str | None, Header()]


@router.post("/behaviors", response_model=ApiResponse)
def create_behavior(payload: BehaviorLogCreate, authorization: AUTH = None) -> ApiResponse:
    user = get_current_user(authorization)
    if not user and payload.userId is not None:
        raise HTTPException(403, "游客不能指定其他用户的 userId")
    if not user and not payload.sessionId:
        raise HTTPException(400, "游客行为必须提供 sessionId")
    if payload.productId is None:
        raise HTTPException(400, "行为日志必须提供 productId")

    with get_connection() as conn:
        product = conn.execute(
            "SELECT name, category FROM products WHERE product_id = ?",
            (payload.productId,),
        ).fetchone()
        if not product:
            raise HTTPException(400, "商品不存在")

        result = insert_behavior(
            conn,
            user_id=user["userId"] if user else None,
            session_id=payload.sessionId,
            product_id=payload.productId,
            product_name=product["name"],
            action=payload.action,
            category=product["category"],
            quantity=payload.quantity,
            sku_id=payload.skuId,
            sku_name=payload.skuName,
            order_id=payload.orderId,
            amount=payload.amount,
            item_count=payload.itemCount,
            source=payload.source,
        )
    return ApiResponse(data=result)


@router.get("/history", response_model=ApiResponse)
def browsing_history(authorization: AUTH = None) -> ApiResponse:
    user = get_current_user(authorization)
    if not user: raise HTTPException(401, "请先登录")
    with get_connection() as conn:
        settings = conn.execute(
            "SELECT history_cleared_at FROM users WHERE user_id = ?",
            (user["userId"],),
        ).fetchone()
        cleared_at = settings["history_cleared_at"] if settings else None
        rows = conn.execute(
            """SELECT * FROM (
                   SELECT bl.*,
                          ROW_NUMBER() OVER (
                              PARTITION BY product_id
                              ORDER BY created_at DESC, log_id DESC
                          ) AS row_no
                   FROM behavior_logs bl
                   WHERE user_id = ?
                     AND action = 'view'
                     AND product_id IS NOT NULL
                     AND (? IS NULL OR created_at > ?)
               ) WHERE row_no = 1
               ORDER BY created_at DESC
               LIMIT 200""",
            (user["userId"], cleared_at, cleared_at),
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
        conn.execute(
            "UPDATE users SET history_cleared_at = ?, updated_at = ? WHERE user_id = ?",
            (now_iso(), now_iso(), user["userId"]),
        )
    return ApiResponse(data=None)


@router.get("/recommendations", response_model=ApiResponse)
def recommendations(
    authorization: AUTH = None,
    userId: int | None = None,
    limit: int = Query(20, ge=1, le=60),
) -> ApiResponse:
    """返回个性化推荐。优先读 recommendation_results（Hadoop 离线结果），无数据时兜底返回热销。"""
    user = get_current_user(authorization)
    if not user and userId is not None:
        raise HTTPException(403, "游客不能查看其他用户的推荐")
    real_uid = user["userId"] if user else userId

    with get_connection() as conn:
        items = []
        if real_uid:
            # 获取最新批次
            batch = conn.execute(
                "SELECT batch_date FROM recommendation_results WHERE user_id = ? ORDER BY batch_date DESC LIMIT 1",
                (real_uid,),
            ).fetchone()
            if batch:
                rows = conn.execute(
                    """SELECT p.* FROM recommendation_results r
                       JOIN products p ON p.product_id = r.product_id
                       WHERE r.user_id = ? AND r.batch_date = ? AND p.status = 'active'
                       ORDER BY r.rank_no LIMIT ?""",
                    (real_uid, batch["batch_date"], limit),
                ).fetchall()
                from app.services.product import row_to_product, _load_skus
                items = [row_to_product(r, _load_skus(conn, r["product_id"])) for r in rows]

        # 兜底：无 Hadoop 结果时返回全站热销
        if not items:
            rows = conn.execute(
                "SELECT * FROM products WHERE status = 'active' ORDER BY sales_count DESC LIMIT ?",
                (limit,),
            ).fetchall()
            from app.services.product import row_to_product, _load_skus
            items = [row_to_product(r, _load_skus(conn, r["product_id"])) for r in rows]

    return ApiResponse(data=items)
