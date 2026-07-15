export interface CartItem {
  cartItemId: number;
  cartId: number;
  productId: number;
  skuId?: number;
  skuName?: string;
  quantity: number;
  totalPrice: number;
  createdAt: string;
  updatedAt: string;
  product?: {
    name: string;
    description: string;
    price: number;
    imageUrl?: string;
  };
}

export interface Cart {
  cartId: number;
  userId: number;
  items: CartItem[];
  createdAt: string;
  updatedAt: string;
}

export interface CartResponse {
  code: string;
  info: string;
  data: Cart;
}

export interface AddToCartRequest {
  productId: number;
  skuId?: number;
  quantity: number;
}
