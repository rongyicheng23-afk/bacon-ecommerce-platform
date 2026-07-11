from pydantic import BaseModel, Field


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
    skus: list[ProductSkuOut] = Field(default_factory=list)
    createdAt: str
    updatedAt: str


class ProductListParams(BaseModel):
    page: int = 1
    pageSize: int = 20
    keyword: str | None = None
    category: str | None = None
    sort: str | None = None  # price-asc / price-desc / stock-desc


class SellerProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    category: str
    imageUrls: list[str] | None = None


class SellerProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = None


class ProductStatusUpdate(BaseModel):
    status: str  # active / inactive / draft
