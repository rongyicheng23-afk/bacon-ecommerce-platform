"""兼容旧导入；新代码应从 app.schemas 的对应模块导入。"""
from app.schemas.behavior import BehaviorLogCreate
from app.schemas.common import ApiResponse
from app.schemas.product import ProductOut as Product, ProductSkuOut as ProductSku
from app.schemas.user import LoginRequest, RegisterRequest, UserPublic


__all__ = [
    "ApiResponse",
    "BehaviorLogCreate",
    "LoginRequest",
    "Product",
    "ProductSku",
    "RegisterRequest",
    "UserPublic",
]
