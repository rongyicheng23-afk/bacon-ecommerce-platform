"""订单 & 支付路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from app.schemas.common import ApiResponse
from app.schemas.order import CreateOrderRequest, PayOrderRequest
from app.services.auth import get_current_user
from app.services.order import (
    create_order, list_orders, get_order, cancel_order, pay_order,
)

router = APIRouter(prefix="/api", tags=["订单"])

AUTH = Annotated[str | None, Header()]


def _require_buyer(auth: str | None) -> dict:
    user = get_current_user(auth)
    if not user: raise HTTPException(401, "请先登录")
    if user["role"] != "buyer": raise HTTPException(403, "仅买家可操作")
    return user


@router.post("/orders", response_model=ApiResponse)
def orders_create(payload: CreateOrderRequest, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    try:
        return ApiResponse(data=create_order(u["userId"], payload.model_dump()))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/orders", response_model=ApiResponse)
def orders_list(status: str | None = None, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    return ApiResponse(data=list_orders(u["userId"], status))


@router.get("/orders/{order_id}", response_model=ApiResponse)
def orders_detail(order_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    o = get_order(order_id, u["userId"])
    if not o: raise HTTPException(404, "订单不存在")
    return ApiResponse(data=o)


@router.post("/orders/{order_id}/cancel", response_model=ApiResponse)
def orders_cancel(order_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    o = cancel_order(u["userId"], order_id)
    if not o: raise HTTPException(400, "订单不可取消")
    return ApiResponse(data=o)


@router.post("/orders/{order_id}/pay", response_model=ApiResponse)
def orders_pay(order_id: int, payload: PayOrderRequest, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    o = pay_order(u["userId"], order_id, payload.paymentType)
    if not o: raise HTTPException(400, "订单不可支付")
    return ApiResponse(data=o)


@router.post("/orders/{order_id}/receive", response_model=ApiResponse)
def orders_receive(order_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    from app.services.order import get_order
    from app.db.database import get_connection, now_iso
    o = get_order(order_id, u["userId"])
    if not o or o["status"] != "shipped": raise HTTPException(400, "订单不可确认收货")
    ts = now_iso()
    with get_connection() as conn:
        conn.execute("UPDATE orders SET status = 'completed', updated_at = ? WHERE order_id = ?", (ts, order_id))
    return ApiResponse(data=get_order(order_id, u["userId"]))
