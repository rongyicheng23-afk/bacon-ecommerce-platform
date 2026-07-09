export interface Order {
  orderId: number;
  userId: number;
  /** 商品原价总和 */
  totalAmount: number;
  /** 实付金额（优惠 + 运费后） */
  payableAmount: number;
  status: OrderStatus;
  payType?: PaymentType;
  payTime?: string;
  createdAt: string;
  updatedAt: string;
  items: OrderItem[];
}

export type OrderStatus = 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled';
export type PaymentType = 1 | 2 | 3; // 1: alipay, 2: wechat, 3: credit card

export interface OrderItem {
  orderItemId: number;
  productId: number;
  quantity: number;
  price: number;
  productName: string;
  productImage?: string;
}

export interface CreateOrderRequest {
  products: Array<{
    productId: number;
    quantity: number;
  }>;
}

export interface OrderResponse {
  code: string;
  info: string;
  data: Order;
}

export interface OrderListResponse {
  code: string;
  info: string;
  data: Order[];
}
