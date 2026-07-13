from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    productId: int
    skuId: int | None = None
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1, le=99)
    selected: bool | None = None


class AddressCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=6, max_length=30)
    detail: str = Field(min_length=1, max_length=300)
    isDefault: bool = False


class AddressUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str | None = Field(default=None, min_length=6, max_length=30)
    detail: str | None = Field(default=None, min_length=1, max_length=300)
    isDefault: bool | None = None


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
