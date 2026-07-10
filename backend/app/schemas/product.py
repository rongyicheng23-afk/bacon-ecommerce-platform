from pydantic import BaseModel


class ProductSkuOut(BaseModel):
    skuId: int
    productId: int
    name: str
    price: float
    stock: int
    imageUrl: str
    attributes: dict[str, str]


class ProductOut(BaseModel):
    productId: int
    sellerId: int | None = None
    name: str
    description: str
    price: float
    stock: int
    status: str
    imageUrls: list[str]
    category: str
    skus: list[ProductSkuOut] = []
    createdAt: str
    updatedAt: str


class ProductListParams(BaseModel):
    page: int = 1
    pageSize: int = 20
    keyword: str | None = None
    category: str | None = None
    sort: str | None = None  # price-asc / price-desc / stock-desc


class SellerProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str


class SellerProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category: str | None = None
