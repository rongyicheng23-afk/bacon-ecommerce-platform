/** 商品 SKU（规格），对应数据库 product_sku 表 */
export interface ProductSku {
  skuId: number;
  productId: number;
  /** 规格名称，如 "黑色 · Pro 版" */
  name: string;
  price: number;
  stock: number;
  /** 该 SKU 对应的图片（MinIO 路径），不同颜色/版本可能用不同图片 */
  imageUrl: string;
  /** 规格属性，如 { 颜色: "黑色", 版本: "Pro 版" } */
  attributes: Record<string, string>;
}

/** 商品主数据，对应数据库 product 表 */
export interface Product {
  productId: number;
  name: string;
  description: string;
  /** 最低售价（所有 SKU 中的最低价，用于列表展示） */
  price: number;
  /** 总库存（所有 SKU 库存之和） */
  stock: number;
  status: 'active' | 'inactive';
  /** 商品图片列表（MinIO 路径数组），第一张为主图 */
  imageUrls: string[];
  category?: string;
  /** 商品下的所有 SKU */
  skus: ProductSku[];
  createdAt: string;
  updatedAt: string;
}

/** 获取商品主图（imageUrls 第一张，不存在时返回占位图） */
export const getPrimaryImage = (product: Product): string => {
  return (
    product.imageUrls[0] ||
    'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85'
  );
};

export interface ProductResponse {
  code: string;
  info: string;
  data: Product[] | Product;
}
