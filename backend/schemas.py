from typing import Any, Literal

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: str = "0000"
    info: str = "success"
    data: Any = None


class UserPublic(BaseModel):
    userId: int
    username: str
    email: str
    phone: str = ""
    role: Literal["buyer", "seller"]
    shopName: str | None = None
    mainCategory: str | None = None
    status: str = "active"
    createdAt: str
    updatedAt: str


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    email: str
    password: str = Field(min_length=6)
    phone: str | None = ""
    role: Literal["buyer", "seller"] = "buyer"
    shopName: str | None = None
    mainCategory: str | None = None


class ProductSku(BaseModel):
    skuId: int
    productId: int
    name: str
    price: float
    stock: int
    imageUrl: str
    attributes: dict[str, str]


class Product(BaseModel):
    productId: int
    sellerId: int | None = None
    name: str
    description: str
    price: float
    stock: int
    status: Literal["active", "inactive"]
    imageUrls: list[str]
    category: str
    skus: list[ProductSku]
    createdAt: str
    updatedAt: str


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
