from pydantic import BaseModel


class OrderItemOut(BaseModel):
    orderItemId: int
    productId: int
    skuId: int | None = None
    skuName: str | None = None
    productName: str
    price: float
    quantity: int
    imageUrl: str | None = None


class OrderOut(BaseModel):
    orderId: int
    userId: int
    totalAmount: float
    payableAmount: float
    deliveryFee: float
    deliveryType: str
    paymentType: str | None = None
    status: str
    address: dict | None = None
    remark: str
    paidAt: str | None = None
    createdAt: str
    updatedAt: str
    items: list[OrderItemOut] = []


class CreateOrderRequest(BaseModel):
    addressId: int
    deliveryType: str = "standard"
    paymentType: str = "alipay"
    remark: str = ""


class PayOrderRequest(BaseModel):
    paymentType: str = "alipay"
