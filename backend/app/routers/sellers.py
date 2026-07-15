"""商家路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Query
from app.schemas.common import ApiResponse
from app.schemas.product import SellerProductCreate, SellerProductUpdate, ProductStatusUpdate, ShopUpdate
from app.services.auth import get_current_user
from app.services.product import (
    seller_create_product, seller_update_product, seller_update_product_status,
    seller_list_products, list_products, get_shop_profile,
)
from app.services.order import seller_ship_order, seller_list_orders
from app.db.database import get_connection, now_iso

router = APIRouter(prefix="/api/seller", tags=["商家"])

AUTH = Annotated[str | None, Header()]


def _require_seller(auth: str | None) -> dict:
    user = get_current_user(auth)
    if not user: raise HTTPException(401, "请先登录")
    if user["role"] != "seller": raise HTTPException(403, "仅商家可操作")
    return user


# ---- 商品管理 ----
@router.get("/products", response_model=ApiResponse)
def seller_product_list(authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    return ApiResponse(data=seller_list_products(u["userId"]))


@router.post("/products", response_model=ApiResponse)
def seller_create(payload: SellerProductCreate, authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    try:
        p = seller_create_product(u["userId"], payload.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return ApiResponse(data=p)


@router.put("/products/{product_id}", response_model=ApiResponse)
def seller_update(product_id: int, payload: SellerProductUpdate, authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    try:
        p = seller_update_product(
            product_id,
            u["userId"],
            payload.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not p: raise HTTPException(404, "商品不存在或非本人商品")
    return ApiResponse(data=p)


@router.patch("/products/{product_id}/status", response_model=ApiResponse)
def seller_toggle_status(product_id: int, payload: ProductStatusUpdate, authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    if payload.status not in ("active", "inactive", "draft"):
        raise HTTPException(400, "无效状态，可选值: active, inactive, draft")
    p = seller_update_product_status(product_id, u["userId"], payload.status)
    if not p: raise HTTPException(404, "商品不存在或非本人商品")
    return ApiResponse(data=p)


# ---- 订单管理 ----
@router.get("/orders", response_model=ApiResponse)
def seller_orders(authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    return ApiResponse(data=seller_list_orders(u["userId"]))


@router.post("/orders/{order_id}/ship", response_model=ApiResponse)
def seller_ship(order_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    o = seller_ship_order(u["userId"], order_id)
    if not o: raise HTTPException(400, "订单不可发货")
    return ApiResponse(data=o)


# ---- 数据看板 ----
@router.get("/dashboard", response_model=ApiResponse)
def seller_dashboard(authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    sid = u["userId"]
    with get_connection() as conn:
        products = conn.execute(
            "SELECT COUNT(*) AS cnt, SUM(stock) AS total_stock FROM products WHERE seller_id = ?",
            (sid,),
        ).fetchone()
        active_products = conn.execute(
            "SELECT COUNT(*) FROM products WHERE seller_id = ? AND status = 'active'",
            (sid,),
        ).fetchone()[0]

        order_stats = conn.execute("""
            SELECT COUNT(*) AS total_orders,
                   SUM(CASE WHEN o.status = 'paid' THEN 1 ELSE 0 END) AS pending_ship,
                   SUM(CASE WHEN o.status = 'completed' THEN o.payable_amount ELSE 0 END) AS revenue
            FROM orders o
            WHERE o.status != 'cancelled'
              AND EXISTS (
                  SELECT 1
                  FROM order_items oi
                  JOIN products p ON p.product_id = oi.product_id
                  WHERE oi.order_id = o.order_id AND p.seller_id = ?
              )
        """, (sid,)).fetchone()

        recent = conn.execute("""
            SELECT DISTINCT o.* FROM orders o
            JOIN order_items oi ON oi.order_id = o.order_id
            JOIN products p ON p.product_id = oi.product_id
            WHERE p.seller_id = ?
            ORDER BY o.created_at DESC LIMIT 10
        """, (sid,)).fetchall()

        from app.services.order import _order_to_dict
        recent_orders = [_order_to_dict(conn, r) for r in recent]

    return ApiResponse(data={
        "totalProducts": products["cnt"],
        "activeProducts": active_products,
        "totalStock": products["total_stock"] or 0,
        "totalOrders": order_stats["total_orders"] or 0,
        "pendingShipment": order_stats["pending_ship"] or 0,
        "totalRevenue": round(order_stats["revenue"] or 0, 2),
        "recentOrders": recent_orders,
    })


# ---- 店铺 ----
@router.get("/shop", response_model=ApiResponse)
def my_shop(authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    shop = get_shop_profile(u["userId"])
    if not shop: raise HTTPException(404, "店铺不存在")
    return ApiResponse(data=shop)


@router.put("/shop", response_model=ApiResponse)
def update_my_shop(payload: ShopUpdate, authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    ts = now_iso()
    data = payload.model_dump(exclude_none=True)
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM shops WHERE owner_user_id = ?", (u["userId"],)).fetchone()
        if not row: raise HTTPException(404, "店铺不存在")
        conn.execute(
            "UPDATE shops SET name=COALESCE(?,name), description=COALESCE(?,description), logo_url=COALESCE(?,logo_url), updated_at=? WHERE owner_user_id=?",
            (data.get("name"), data.get("description"), data.get("logoUrl"), ts, u["userId"]),
        )
        if "name" in data:
            conn.execute(
                "UPDATE users SET shop_name = ?, updated_at = ? WHERE user_id = ?",
                (data["name"], ts, u["userId"]),
            )
    shop = get_shop_profile(u["userId"])
    return ApiResponse(data=shop)
