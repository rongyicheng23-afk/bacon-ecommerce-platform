from typing import Literal

from pydantic import BaseModel, Field


class BehaviorLogCreate(BaseModel):
    # userId 只用于兼容旧前端；服务端不会允许游客冒充该用户。
    userId: int | None = None
    sessionId: str | None = Field(default=None, min_length=1, max_length=128)
    productId: int | None = None
    productName: str | None = None
    action: Literal[
        "view", "search", "search_click", "favorite", "unfavorite",
        "cart", "purchase", "refund"
    ]
    category: str | None = None
    quantity: int | None = Field(default=None, ge=1, le=99)
    skuId: int | None = None
    skuName: str | None = None
    orderId: int | None = None
    amount: float | None = None
    itemCount: int | None = None
    source: str | None = Field(default=None, max_length=100)
    queryText: str | None = Field(default=None, min_length=1, max_length=100)
