# Bacon Mall 系统架构

## 系统架构图

```mermaid
flowchart TB
    subgraph 前端["🖥️ 前端 (Vue 3 + Vite)"]
        Home["首页"]
        ProductList["商品库"]
        ProductDetail["商品详情"]
        Cart["购物车"]
        Order["订单"]
        Profile["个人中心"]
        SellerDashboard["商家后台"]
    end

    subgraph 后端["⚙️ 后端 (FastAPI)"]
        Auth["认证模块"]
        Products["商品模块"]
        CartModule["购物车模块"]
        OrderModule["订单模块"]
        BehaviorAPI["行为日志 API"]
        MediaUpload["媒体上传"]
        RecommendationAPI["推荐 API"]
    end

    subgraph 存储["💾 数据层"]
        SQLite["SQLite (15 表)"]
        MinIO["MinIO / 本地存储"]
    end

    subgraph 大数据["📊 大数据 (Hadoop)"]
        HDFS["HDFS 行为日志"]
        YARN["YARN Streaming"]
        Mapper["Python Mapper"]
        Reducer["Python Reducer"]
    end

    frontend -->|HTTP JSON| 后端
    后端 --> SQLite
    后端 --> MinIO
    BehaviorAPI -->|export| HDFS
    HDFS --> YARN
    YARN --> Mapper --> Reducer
    Reducer -->|推荐结果| SQLite
    RecommendationAPI -->|查询| SQLite
    RecommendationAPI -->|返回| Home
```

## 数据库 ER 图

```mermaid
erDiagram
    USERS ||--o| SHOPS : "owns (1:1)"
    USERS ||--o{ SESSIONS : "has"
    USERS ||--o{ ADDRESSES : "has"
    USERS ||--o{ CART_ITEMS : "has"
    USERS ||--o{ FAVORITES : "creates"
    USERS ||--o{ ORDERS : "places"
    USERS ||--o{ BEHAVIOR_LOGS : "produces"
    USERS ||--o{ RECOMMENDATION_RESULTS : "receives"

    SHOPS ||--o{ PRODUCTS : "sells"
    CATEGORIES ||--o{ PRODUCTS : "contains"
    PRODUCTS ||--o{ PRODUCT_SKUS : "has"
    PRODUCTS ||--o{ CART_ITEMS : "in"
    PRODUCTS ||--o{ FAVORITES : "receives"
    PRODUCTS ||--o{ ORDER_ITEMS : "appears_in"
    PRODUCTS ||--o{ BEHAVIOR_LOGS : "tracked"

    ORDERS ||--o{ ORDER_ITEMS : "contains"
    ORDERS ||--o{ PAYMENTS : "has"

    USERS {
        int user_id PK
        string username
        string email UK
        string role "buyer|seller"
        string status "active|disabled"
    }

    SHOPS {
        int shop_id PK
        int owner_user_id FK
        string name
        string status
    }

    PRODUCTS {
        int product_id PK
        int seller_id FK
        int shop_id FK
        string name
        float price "CHECK >=0"
        int stock "CHECK >=0"
        int sales_count
        string status "active|inactive|draft|deleted"
    }

    PRODUCT_SKUS {
        int sku_id PK
        int product_id FK
        string name
        float price
        int stock
        string attributes "JSON"
    }

    ORDERS {
        int order_id PK
        int user_id FK
        int shop_id FK
        string status "7 states"
        float payable_amount
    }

    BEHAVIOR_LOGS {
        int log_id PK
        string event_id UK
        int user_id FK
        int product_id FK
        string action "view|search|favorite|cart|purchase|refund"
        string category
        int quantity
        string exported_at
    }

    RECOMMENDATION_RESULTS {
        int rec_id PK
        int user_id FK
        int product_id FK
        float score
        string reason_code
        int rank_no
        string batch_date
    }
```

## 推荐流程

```mermaid
flowchart LR
    A["用户行为\n(view/favorite/cart/purchase)"] --> B["behavior_logs 表"]
    B --> C["export_behaviors.py\n导出 JSONL"]
    C --> D["HDFS\n/bacon-mall/raw/behavior/"]
    D --> E["Hadoop Streaming\nMapper × 2"]
    E --> F["用户×分类偏好"]
    E --> G["用户×商品偏好"]
    F --> H["generate_recommendations.py"]
    G --> H
    I["products 表\n(销量/库存)"] --> H
    H --> J["recommendation_results 表"]
    J --> K["GET /api/recommendations"]
    K --> L["首页 '为你精选'"]
```

### 推荐公式

```
score = category_preference × 0.5 + product_preference × 0.3 + popularity × 0.2
```

### 行为权重

| 行为 | 权重 | 含义 |
|------|------|------|
| view | 1 | 浏览 |
| search | 2 | 搜索 |
| favorite | 3 | 收藏 |
| cart | 4 | 加购 |
| purchase | 5 | 购买 |

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 前端框架 | Vue 3 + Vite 6 + TypeScript | SPA |
| 状态管理 | Pinia | 组件状态 |
| HTTP 客户端 | Axios + 拦截器 | 自动 Token |
| 后端框架 | FastAPI | Python Web API |
| 数据库 | SQLite 3 | 15 张表 |
| ORM | 原生 sqlite3 | 轻量无依赖 |
| 对象存储 | MinIO / 本地 FS | 双模 |
| 认证 | Session Token + PBKDF2 | 密码哈希 |
| 大数据计算 | Hadoop 3.x + YARN | Streaming |
| 计算语言 | Python 3 | Mapper/Reducer |
| 数据格式 | JSON Lines | 行为日志 |
