import hashlib
import json
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bacon_mall.db"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: str | None = None) -> str:
    real_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), real_salt.encode("utf-8"), 120_000)
    return f"{real_salt}${digest.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, _ = stored_password.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_password(password, salt), stored_password)


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE,
              phone TEXT DEFAULT '',
              role TEXT NOT NULL CHECK(role IN ('buyer', 'seller')),
              shop_name TEXT,
              main_category TEXT,
              password_hash TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'active',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS products (
              product_id INTEGER PRIMARY KEY AUTOINCREMENT,
              seller_id INTEGER,
              name TEXT NOT NULL,
              description TEXT NOT NULL,
              price REAL NOT NULL,
              stock INTEGER NOT NULL,
              status TEXT NOT NULL DEFAULT 'active',
              image_urls TEXT NOT NULL,
              category TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY (seller_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS product_skus (
              sku_id INTEGER PRIMARY KEY AUTOINCREMENT,
              product_id INTEGER NOT NULL,
              name TEXT NOT NULL,
              price REAL NOT NULL,
              stock INTEGER NOT NULL,
              image_url TEXT NOT NULL,
              attributes TEXT NOT NULL,
              FOREIGN KEY (product_id) REFERENCES products(product_id)
            );

            CREATE TABLE IF NOT EXISTS behavior_logs (
              log_id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              product_id INTEGER,
              product_name TEXT,
              action TEXT NOT NULL,
              category TEXT,
              quantity INTEGER,
              sku_id INTEGER,
              sku_name TEXT,
              order_id INTEGER,
              amount REAL,
              item_count INTEGER,
              created_at TEXT NOT NULL
            );
            """
        )
        seed_demo_data(conn)


def seed_demo_data(conn: sqlite3.Connection) -> None:
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        created_at = now_iso()
        conn.execute(
            """
            INSERT INTO users
              (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("荣同学", "student@example.com", "13800002026", "buyer", None, None, hash_password("123456"), "active", created_at, created_at),
        )
        conn.execute(
            """
            INSERT INTO users
              (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Bacon 数码旗舰店", "seller@example.com", "13900002026", "seller", "Bacon 数码旗舰店", "数码", hash_password("123456"), "active", created_at, created_at),
        )

    product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if product_count > 0:
        return

    seller = conn.execute("SELECT user_id FROM users WHERE role = 'seller' LIMIT 1").fetchone()
    seller_id = seller["user_id"] if seller else None
    created_at = now_iso()
    products = [
        ("智能降噪耳机", "通勤、运动和学习都适合的无线蓝牙耳机，支持主动降噪。", 188, 53, "数码", [
            "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85",
        ]),
        ("轻薄机械键盘", "适合办公、学习和编程的轻薄机械键盘，红轴静音设计。", 269, 88, "数码", [
            "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85",
            "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85",
        ]),
        ("保温咖啡杯", "简洁耐用的日常保温杯，适合办公桌和通勤。", 79, 120, "家居", [
            "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85",
            "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85",
        ]),
        ("运动休闲背包", "轻便大容量，适合上课、出行和日常通勤。", 159, 76, "服饰", [
            "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85",
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85",
        ]),
        ("护眼台灯", "柔和照明，适合夜间学习和居家办公。", 129, 64, "家居", [
            "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85",
            "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85",
        ]),
        ("便携移动电源", "20000mAh 大容量，小巧便携，满足日常充电。", 109, 91, "数码", [
            "https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85",
            "https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85",
        ]),
    ]

    for name, description, price, stock, category, image_urls in products:
        cur = conn.execute(
            """
            INSERT INTO products
              (seller_id, name, description, price, stock, status, image_urls, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (seller_id, name, description, price, stock, "active", json.dumps(image_urls, ensure_ascii=False), category, created_at, created_at),
        )
        product_id = cur.lastrowid
        for sku_name, rate in [("标准版", 1), ("Pro 版", 1.18)]:
            sku_price = round(price * rate, 2)
            conn.execute(
                """
                INSERT INTO product_skus
                  (product_id, name, price, stock, image_url, attributes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    sku_name,
                    sku_price,
                    max(1, stock // 2),
                    image_urls[0],
                    json.dumps({"版本": sku_name}, ensure_ascii=False),
                ),
            )
