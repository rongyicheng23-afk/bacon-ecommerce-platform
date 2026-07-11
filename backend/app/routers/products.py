"""商品路由"""
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from app.schemas.common import ApiResponse
from app.services.product import list_products, get_product, list_categories, get_category_tree, get_shop_profile

router = APIRouter(prefix="/api", tags=["商品"])


# ---- 公开店铺 ----
@router.get("/shops/{shop_id}", response_model=ApiResponse)
def shop_profile_by_id(shop_id: int) -> ApiResponse:
    from app.db.database import get_connection
    with get_connection() as conn:
        row = conn.execute(
            "SELECT owner_user_id FROM shops WHERE shop_id = ? AND status = 'active'",
            (shop_id,),
        ).fetchone()
    if not row:
        raise HTTPException(404, "店铺不存在")
    shop = get_shop_profile(row["owner_user_id"])
    if not shop:
        raise HTTPException(404, "店铺不存在")
    return ApiResponse(data=shop)


@router.get("/product/list", response_model=ApiResponse)
def product_list(
    category: str | None = None,
    keyword: str | None = None,
    sort: Literal["price-asc", "price-desc", "stock-desc"] | None = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
) -> ApiResponse:
    result = list_products(category=category, keyword=keyword, sort=sort, page=page, page_size=pageSize)
    return ApiResponse(data=result)


@router.get("/product/get", response_model=ApiResponse)
def product_get(productId: int = Query(...)) -> ApiResponse:
    p = get_product(productId)
    if not p:
        raise HTTPException(404, "商品不存在")
    return ApiResponse(data=p)


@router.get("/products", response_model=ApiResponse)
def products_all(
    category: str | None = None,
    keyword: str | None = None,
    sort: Literal["price-asc", "price-desc", "stock-desc"] | None = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
) -> ApiResponse:
    result = list_products(category=category, keyword=keyword, sort=sort, page=page, page_size=pageSize)
    return ApiResponse(data=result)


@router.get("/products/{product_id}", response_model=ApiResponse)
def product_detail(product_id: int) -> ApiResponse:
    p = get_product(product_id)
    if not p:
        raise HTTPException(404, "商品不存在")
    return ApiResponse(data=p)


@router.get("/categories", response_model=ApiResponse)
def categories() -> ApiResponse:
    return ApiResponse(data=list_categories())


@router.get("/categories/tree", response_model=ApiResponse)
def categories_tree() -> ApiResponse:
    return ApiResponse(data=get_category_tree())
