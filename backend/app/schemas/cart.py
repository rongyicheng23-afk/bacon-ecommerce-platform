from pydantic import BaseModel


class CartItemAdd(BaseModel):
    productId: int
    skuId: int | None = None
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    cartItemId: int
    productId: int
    skuId: int | None = None
    skuName: str | None = None
    quantity: int
    price: float
    stock: int
    name: str
    description: str
    imageUrl: str | None = None
    category: str
    selected: bool


class CartOut(BaseModel):
    items: list[CartItemOut]
    totalQuantity: int
    totalAmount: float
