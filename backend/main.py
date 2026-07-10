import json
import secrets
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, hash_password, init_db, now_iso, verify_password
from schemas import ApiResponse, BehaviorLogCreate, LoginRequest, RegisterRequest


app = FastAPI(title="Bacon Mall API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


def row_to_user(row) -> dict:
    return {
        "userId": row["user_id"],
        "username": row["username"],
        "email": row["email"],
        "phone": row["phone"] or "",
        "role": row["role"],
        "shopName": row["shop_name"],
        "mainCategory": row["main_category"],
        "status": row["status"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def row_to_product(row, skus: list[dict]) -> dict:
    return {
        "productId": row["product_id"],
        "sellerId": row["seller_id"],
        "name": row["name"],
        "description": row["description"],
        "price": row["price"],
        "stock": row["stock"],
        "status": row["status"],
        "imageUrls": json.loads(row["image_urls"]),
        "category": row["category"],
        "skus": skus,
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def row_to_sku(row) -> dict:
    return {
        "skuId": row["sku_id"],
        "productId": row["product_id"],
        "name": row["name"],
        "price": row["price"],
        "stock": row["stock"],
        "imageUrl": row["image_url"],
        "attributes": json.loads(row["attributes"]),
    }


def read_products(category: str | None = None) -> list[dict]:
    with get_connection() as conn:
        if category:
            product_rows = conn.execute(
                "SELECT * FROM products WHERE status = 'active' AND category = ? ORDER BY product_id",
                (category,),
            ).fetchall()
        else:
            product_rows = conn.execute(
                "SELECT * FROM products WHERE status = 'active' ORDER BY product_id"
            ).fetchall()

        products = []
        for product_row in product_rows:
            sku_rows = conn.execute(
                "SELECT * FROM product_skus WHERE product_id = ? ORDER BY sku_id",
                (product_row["product_id"],),
            ).fetchall()
            products.append(row_to_product(product_row, [row_to_sku(row) for row in sku_rows]))
        return products


def read_current_user(authorization: str | None) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT users.*
            FROM sessions
            JOIN users ON users.user_id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
        return row_to_user(row) if row else None


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "message": "Bacon Mall backend is running"}


@app.post("/api/user/register", response_model=ApiResponse)
def register(payload: RegisterRequest) -> ApiResponse:
    if payload.role == "seller" and not payload.shopName:
        raise HTTPException(status_code=400, detail="商家账号需要填写店铺名称")

    created_at = now_iso()
    with get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (payload.email,)).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="该邮箱已经注册")

        cur = conn.execute(
            """
            INSERT INTO users
              (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.username,
                payload.email,
                payload.phone or "",
                payload.role,
                payload.shopName,
                payload.mainCategory,
                hash_password(payload.password),
                "active",
                created_at,
                created_at,
            ),
        )
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (cur.lastrowid,)).fetchone()
        token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user["user_id"], created_at),
        )

    return ApiResponse(data={"token": token, "user": row_to_user(user)})


@app.post("/api/user/login", response_model=ApiResponse)
def login(payload: LoginRequest) -> ApiResponse:
    created_at = now_iso()
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (payload.email,)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="邮箱或密码不正确")

        token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user["user_id"], created_at),
        )

    return ApiResponse(data={"token": token, "user": row_to_user(user)})


@app.get("/api/product/list", response_model=ApiResponse)
def product_list(category: str | None = None) -> ApiResponse:
    return ApiResponse(data=read_products(category))


@app.get("/api/product/get", response_model=ApiResponse)
def product_get(productId: int = Query(...)) -> ApiResponse:
    products = read_products()
    product = next((item for item in products if item["productId"] == productId), None)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ApiResponse(data=product)


@app.get("/api/products", response_model=ApiResponse)
def products(category: str | None = None) -> ApiResponse:
    return ApiResponse(data=read_products(category))


@app.get("/api/products/{product_id}", response_model=ApiResponse)
def product_detail(product_id: int) -> ApiResponse:
    products = read_products()
    product = next((item for item in products if item["productId"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ApiResponse(data=product)


@app.post("/api/behavior-logs", response_model=ApiResponse)
def create_behavior_log(
    payload: BehaviorLogCreate,
    authorization: Annotated[str | None, Header()] = None,
) -> ApiResponse:
    user = read_current_user(authorization)
    user_id = user["userId"] if user else payload.userId
    created_at = now_iso()

    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO behavior_logs
              (user_id, product_id, product_name, action, category, quantity, sku_id, sku_name, order_id, amount, item_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                payload.productId,
                payload.productName,
                payload.action,
                payload.category,
                payload.quantity,
                payload.skuId,
                payload.skuName,
                payload.orderId,
                payload.amount,
                payload.itemCount,
                created_at,
            ),
        )

    return ApiResponse(data={"logId": cur.lastrowid, "createdAt": created_at})


@app.get("/api/recommendations", response_model=ApiResponse)
def recommendations(
    authorization: Annotated[str | None, Header()] = None,
    userId: int | None = None,
    limit: int = 20,
) -> ApiResponse:
    user = read_current_user(authorization)
    real_user_id = user["userId"] if user else userId

    with get_connection() as conn:
        categories: list[str] = []
        if real_user_id:
            rows = conn.execute(
                """
                SELECT category, COUNT(*) AS score
                FROM behavior_logs
                WHERE user_id = ? AND category IS NOT NULL AND category != '订单'
                GROUP BY category
                ORDER BY score DESC
                LIMIT 3
                """,
                (real_user_id,),
            ).fetchall()
            categories = [row["category"] for row in rows]

    all_products = read_products()
    if not categories:
        return ApiResponse(data=all_products[:limit])

    ranked = sorted(
        all_products,
        key=lambda product: (0 if product["category"] in categories else 1, -product["stock"]),
    )
    return ApiResponse(data=ranked[:limit])
