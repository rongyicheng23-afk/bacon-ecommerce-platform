export interface User {
  userId: number;
  username: string;
  email: string;
  phone: string;
  role: 'buyer' | 'seller';
  shopName?: string;
  mainCategory?: string;
  status: 'active' | 'inactive';
  createdAt: string;
  updatedAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone?: string;
  role: 'buyer' | 'seller';
  shopName?: string;
  mainCategory?: string;
}

export interface AuthResponse {
  code: string;
  info: string;
  data: {
    token: string;
    user: User;
  };
}
