"""前端兼容路由 — 路径和字段名对齐 Luna 的 Vue 前端。

前端 service 层的 API 调用路径和请求/响应字段名（snake_case、嵌套结构等）
与后端 RESTful API 有差异。本模块提供适配层，不做业务逻辑。
"""
import json
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from app.schemas.common import ApiResponse
from app.services.auth import get_current_user
from app.services.order import (
    get_cart, add_cart_item, update_cart_item, remove_cart_item,
    create_order, list_orders, get_order, cancel_order, pay_order,
)
from app.db.database import get_connection, now_iso

router = APIRouter(prefix="/api", tags=["前端兼容"])

AUTH = Annotated[str | None, Header()]

PAYMENT_MAP = {1: "alipay", 2: "wechat", 3: "card"}
PAYMENT_REVERSE = {"alipay": 1, "wechat": 2, "card": 3}


def _require_buyer(auth: str | None) -> dict:
    user = get_current_user(auth)
    if not user:
        raise HTTPException(401, "请先登录")
    if user["role"] != "buyer":
        raise HTTPException(403, "仅买家可操作")
    return user


def _adapt_cart(raw: dict, user_id: int) -> dict:
    """将后端购物车格式转为前端期望的 Cart/CartItem 格式"""
    now = now_iso()
    items = []
    for it in raw.get("items", []):
        items.append({
            "cartItemId": it["cartItemId"],
            "cartId": user_id,
            "productId": it["productId"],
            "skuId": it.get("skuId"),
            "skuName": it.get("skuName"),
            "quantity": it["quantity"],
            "totalPrice": round(it["price"] * it["quantity"], 2),
            "createdAt": it.get("createdAt", now),
            "updatedAt": it.get("updatedAt", now),
            "product": {
                "name": it["name"],
                "description": it.get("description", ""),
                "price": it["price"],
                "imageUrl": it.get("imageUrl"),
            },
        })
    return {
        "cartId": user_id,
        "userId": user_id,
        "items": items,
        "createdAt": now,
        "updatedAt": now,
    }


def _adapt_order(raw: dict) -> dict:
    """将后端订单格式转为前端期望的 Order 格式"""
    items = []
    for it in raw.get("items", []):
        items.append({
            "orderItemId": it["orderItemId"],
            "productId": it["productId"],
            "skuId": it.get("skuId"),
            "skuName": it.get("skuName"),
            "quantity": it["quantity"],
            "price": it["price"],
            "productName": it["productName"],
            "productImage": it.get("imageUrl"),
        })
    pay_type = PAYMENT_REVERSE.get(raw.get("paymentType") or "", 0) or None
    return {
        "orderId": raw["orderId"],
        "userId": raw["userId"],
        "totalAmount": raw["totalAmount"],
        "payableAmount": raw["payableAmount"],
        "status": raw["status"],
        "payType": pay_type,
        "payTime": raw.get("paidAt"),
        "createdAt": raw["createdAt"],
        "updatedAt": raw["updatedAt"],
        "items": items,
    }


# ═══════════════ 购物车 ═══════════════

@router.get("/cart/get", response_model=ApiResponse)
def cart_get(authorization: AUTH = None):
    u = _require_buyer(authorization)
    raw = get_cart(u["userId"])
    return ApiResponse(data=_adapt_cart(raw, u["userId"]))


@router.post("/cart/add", response_model=ApiResponse)
def cart_add(payload: dict, authorization: AUTH = None):
    u = _require_buyer(authorization)
    product_id = payload.get("product_id") or payload.get("productId")
    quantity = payload.get("quantity", 1)
    sku_id = payload.get("sku_id") or payload.get("skuId")
    if not product_id:
        raise HTTPException(400, "缺少 product_id")
    # 未指定 SKU 时取第一个
    if not sku_id:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT sku_id FROM product_skus WHERE product_id = ? ORDER BY sku_id LIMIT 1",
                (product_id,),
            ).fetchone()
            if not row:
                raise HTTPException(400, "商品无可用 SKU")
            sku_id = row["sku_id"]
    try:
        raw = add_cart_item(u["userId"], product_id, sku_id, quantity)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return ApiResponse(data=_adapt_cart(raw, u["userId"]))


@router.put("/cart/update", response_model=ApiResponse)
def cart_update(payload: dict, authorization: AUTH = None):
    u = _require_buyer(authorization)
    item_id = payload.get("cart_item_id") or payload.get("cartItemId")
    quantity = payload.get("quantity", 1)
    if not item_id:
        raise HTTPException(400, "缺少 cart_item_id")
    try:
        raw = update_cart_item(u["userId"], item_id, quantity)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return ApiResponse(data=_adapt_cart(raw, u["userId"]))


@router.delete("/cart/remove/{cart_item_id}", response_model=ApiResponse)
def cart_remove(cart_item_id: int, authorization: AUTH = None):
    u = _require_buyer(authorization)
    raw = remove_cart_item(u["userId"], cart_item_id)
    return ApiResponse(data=_adapt_cart(raw, u["userId"]))


@router.post("/cart/clear", response_model=ApiResponse)
def cart_clear(authorization: AUTH = None):
    u = _require_buyer(authorization)
    with get_connection() as conn:
        conn.execute("DELETE FROM cart_items WHERE user_id = ?", (u["userId"],))
    raw = get_cart(u["userId"])
    return ApiResponse(data=_adapt_cart(raw, u["userId"]))


# ═══════════════ 订单 ═══════════════

@router.post("/order/create", response_model=ApiResponse)
def order_create(payload: dict, authorization: AUTH = None):
    u = _require_buyer(authorization)
    products = payload.get("products", [])
    if not products:
        raise HTTPException(400, "订单商品列表不能为空")

    # 将前端传来的商品列表写入购物车（选中状态），复用现有下单逻辑
    with get_connection() as conn:
        # 清除当前用户的旧选中项
        conn.execute(
            "DELETE FROM cart_items WHERE user_id = ? AND selected = 1",
            (u["userId"],),
        )
        for p in products:
            pid = p.get("productId") or p.get("product_id")
            qty = p.get("quantity", 1)
            sku_id = p.get("skuId") or p.get("sku_id")
            if not sku_id:
                row = conn.execute(
                    "SELECT sku_id FROM product_skus WHERE product_id = ? ORDER BY sku_id LIMIT 1",
                    (pid,),
                ).fetchone()
                if not row:
                    raise HTTPException(400, f"商品 {pid} 无可用 SKU")
                sku_id = row["sku_id"]
            conn.execute(
                """INSERT INTO cart_items (user_id, sku_id, product_id, quantity, selected, created_at, updated_at)
                   VALUES (?,?,?,?,1,?,?)""",
                (u["userId"], sku_id, pid, qty, now_iso(), now_iso()),
            )

    # 取默认地址 ID，若无则自动创建
    with get_connection() as conn:
        addr = conn.execute(
            "SELECT address_id FROM addresses WHERE user_id = ? ORDER BY is_default DESC LIMIT 1",
            (u["userId"],),
        ).fetchone()
        if addr:
            address_id = addr["address_id"]
        else:
            ts = now_iso()
            cur = conn.execute(
                "INSERT INTO addresses (user_id, name, phone, detail, is_default) VALUES (?,?,?,?,1)",
                (u["userId"], "默认收货人", "13800000000", "请完善收货地址"),
            )
            address_id = cur.lastrowid

    order_data = {
        "addressId": address_id,
        "deliveryType": "standard",
        "paymentType": "alipay",
        "remark": "",
    }
    try:
        raw = create_order(u["userId"], order_data)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return ApiResponse(data=_adapt_order(raw))


@router.get("/order/list", response_model=ApiResponse)
def order_list(authorization: AUTH = None):
    u = _require_buyer(authorization)
    raw_list = list_orders(u["userId"])
    return ApiResponse(data=[_adapt_order(o) for o in raw_list])


@router.get("/order/get/{order_id}", response_model=ApiResponse)
def order_get(order_id: int, authorization: AUTH = None):
    u = _require_buyer(authorization)
    raw = get_order(order_id, u["userId"])
    if not raw:
        raise HTTPException(404, "订单不存在")
    return ApiResponse(data=_adapt_order(raw))


@router.post("/order/cancel/{order_id}", response_model=ApiResponse)
def order_cancel(order_id: int, authorization: AUTH = None):
    u = _require_buyer(authorization)
    raw = cancel_order(u["userId"], order_id)
    if not raw:
        raise HTTPException(400, "订单不可取消（仅待付款订单可取消）")
    return ApiResponse(data=_adapt_order(raw))


@router.get("/order/status/{order_id}", response_model=ApiResponse)
def order_status(order_id: int, authorization: AUTH = None):
    u = _require_buyer(authorization)
    raw = get_order(order_id, u["userId"])
    if not raw:
        raise HTTPException(404, "订单不存在")
    return ApiResponse(data={"orderId": raw["orderId"], "status": raw["status"]})


# ═══════════════ 支付 ═══════════════

@router.post("/payment/pay", response_model=ApiResponse)
def payment_pay(payload: dict, authorization: AUTH = None):
    u = _require_buyer(authorization)
    order_id = payload.get("orderId") or payload.get("order_id")
    payment_method = payload.get("paymentMethod") or payload.get("payment_method", 1)
    if not order_id:
        raise HTTPException(400, "缺少 orderId")

    payment_type = PAYMENT_MAP.get(payment_method, "alipay")
    raw = pay_order(u["userId"], order_id, payment_type)
    if not raw:
        raise HTTPException(400, "订单不可支付（仅待付款订单可支付）")
    return ApiResponse(data={
        "success": True,
        "paymentId": order_id,
        "status": "success",
    })


@router.post("/payment/cancel", response_model=ApiResponse)
def payment_cancel(payload: dict):
    # 前端 mock 行为：支付取消总是成功
    return ApiResponse(data={
        "success": False,
        "status": "cancelled",
    })
