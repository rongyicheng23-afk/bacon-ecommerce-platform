"""购物车 & 收藏 & 地址路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from app.schemas.common import ApiResponse
from app.schemas.cart import CartItemAdd, CartItemUpdate
from app.services.auth import get_current_user
from app.db.database import get_connection
from app.services.order import (
    get_cart, add_cart_item, update_cart_item, remove_cart_item,
    list_favorites, add_favorite, remove_favorite,
    list_addresses, create_address, update_address, delete_address,
)

router = APIRouter(prefix="/api", tags=["购物车"])

AUTH = Annotated[str | None, Header()]


def _require_buyer(auth: str | None) -> dict:
    user = get_current_user(auth)
    if not user:
        raise HTTPException(401, "请先登录")
    if user["role"] != "buyer":
        raise HTTPException(403, "仅买家可操作")
    return user


# 购物车
@router.get("/cart", response_model=ApiResponse)
def cart_get(authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    return ApiResponse(data=get_cart(u["userId"]))


@router.post("/cart/items", response_model=ApiResponse)
def cart_add(payload: CartItemAdd, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    # 未指定 SKU 时取第一个 SKU
    sku_id = payload.skuId
    if not sku_id:
        with get_connection() as conn:
            row = conn.execute("SELECT sku_id FROM product_skus WHERE product_id = ? ORDER BY sku_id LIMIT 1", (payload.productId,)).fetchone()
            if not row: raise HTTPException(400, "商品无可用SKU")
            sku_id = row["sku_id"]
    return ApiResponse(data=add_cart_item(u["userId"], payload.productId, sku_id, payload.quantity))


@router.put("/cart/items/{item_id}", response_model=ApiResponse)
def cart_update(item_id: int, payload: CartItemUpdate, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    return ApiResponse(data=update_cart_item(u["userId"], item_id, payload.quantity))


@router.delete("/cart/items/{item_id}", response_model=ApiResponse)
def cart_remove(item_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    return ApiResponse(data=remove_cart_item(u["userId"], item_id))


# 收藏
@router.get("/favorites", response_model=ApiResponse)
def favorites_list(authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    return ApiResponse(data=list_favorites(u["userId"]))


@router.post("/favorites/{product_id}", response_model=ApiResponse)
def favorites_add(product_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    add_favorite(u["userId"], product_id)
    return ApiResponse(data=list_favorites(u["userId"]))


@router.delete("/favorites/{product_id}", response_model=ApiResponse)
def favorites_remove(product_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    remove_favorite(u["userId"], product_id)
    return ApiResponse(data=list_favorites(u["userId"]))


# 地址
@router.get("/addresses", response_model=ApiResponse)
def addresses_list(authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    return ApiResponse(data=list_addresses(u["userId"]))


@router.post("/addresses", response_model=ApiResponse)
def addresses_create(payload: dict, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    if not payload.get("name") or not payload.get("phone") or not payload.get("detail"):
        raise HTTPException(400, "收件人、手机号、详细地址不能为空")
    return ApiResponse(data=create_address(u["userId"], payload))


@router.put("/addresses/{address_id}", response_model=ApiResponse)
def addresses_update(address_id: int, payload: dict, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    r = update_address(u["userId"], address_id, payload)
    if not r:
        raise HTTPException(404, "地址不存在")
    return ApiResponse(data=r)


@router.delete("/addresses/{address_id}", response_model=ApiResponse)
def addresses_delete(address_id: int, authorization: AUTH = None) -> ApiResponse:
    u = _require_buyer(authorization)
    if not delete_address(u["userId"], address_id):
        raise HTTPException(404, "地址不存在")
    return ApiResponse(data=None)
