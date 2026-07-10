"""商家路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from app.schemas.common import ApiResponse
from app.services.auth import get_current_user
from app.services.product import seller_update_product
from app.services.order import seller_ship_order, seller_list_orders

router = APIRouter(prefix="/api/seller", tags=["商家"])

AUTH = Annotated[str | None, Header()]


def _require_seller(auth: str | None) -> dict:
    user = get_current_user(auth)
    if not user: raise HTTPException(401, "请先登录")
    if user["role"] != "seller": raise HTTPException(403, "仅商家可操作")
    return user


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


@router.put("/products/{product_id}", response_model=ApiResponse)
def seller_update(product_id: int, payload: dict, authorization: AUTH = None) -> ApiResponse:
    u = _require_seller(authorization)
    p = seller_update_product(product_id, u["userId"], payload)
    if not p: raise HTTPException(404, "商品不存在或非本人商品")
    return ApiResponse(data=p)
