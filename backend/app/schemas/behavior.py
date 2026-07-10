from pydantic import BaseModel


class BehaviorLogCreate(BaseModel):
    userId: int | None = None
    productId: int | None = None
    productName: str | None = None
    action: str
    category: str | None = None
    quantity: int | None = None
    skuId: int | None = None
    skuName: str | None = None
    orderId: int | None = None
    amount: float | None = None
    itemCount: int | None = None
