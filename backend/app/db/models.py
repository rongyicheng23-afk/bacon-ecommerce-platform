"""数据库表创建与升级"""
import sqlite3


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _add_column_if_missing(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    if column not in _column_names(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            phone         TEXT    DEFAULT '',
            role          TEXT    NOT NULL CHECK(role IN ('buyer','seller')),
            shop_name     TEXT,
            main_category TEXT,
            password_hash TEXT    NOT NULL,
            status        TEXT    NOT NULL DEFAULT 'active' CHECK(status IN ('active','disabled')),
            history_cleared_at TEXT,
            created_at    TEXT    NOT NULL,
            updated_at    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS shops (
            shop_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id   INTEGER NOT NULL UNIQUE,
            name            TEXT    NOT NULL,
            description     TEXT    DEFAULT '',
            logo_url        TEXT    DEFAULT '',
            status          TEXT    NOT NULL DEFAULT 'active' CHECK(status IN ('pending','active','closed')),
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL,
            FOREIGN KEY (owner_user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            parent_id   INTEGER,
            sort_order  INTEGER DEFAULT 0,
            status      TEXT    NOT NULL DEFAULT 'active' CHECK(status IN ('active','inactive')),
            icon        TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES categories(category_id)
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            created_at  TEXT    NOT NULL,
            expires_at  TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id   INTEGER NOT NULL,
            shop_id     INTEGER,
            name        TEXT    NOT NULL,
            description TEXT    NOT NULL DEFAULT '',
            price       REAL    NOT NULL CHECK(price >= 0),
            stock       INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            sales_count INTEGER NOT NULL DEFAULT 0 CHECK(sales_count >= 0),
            status      TEXT    NOT NULL DEFAULT 'active' CHECK(status IN ('active','inactive','draft','deleted')),
            image_urls  TEXT    NOT NULL DEFAULT '[]',
            category    TEXT    NOT NULL,
            subcategory TEXT    NOT NULL DEFAULT '',
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL,
            FOREIGN KEY (seller_id) REFERENCES users(user_id),
            FOREIGN KEY (shop_id)   REFERENCES shops(shop_id)
        );

        CREATE TABLE IF NOT EXISTS product_skus (
            sku_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL,
            sku_code    TEXT    DEFAULT '',
            name        TEXT    NOT NULL,
            price       REAL    NOT NULL CHECK(price >= 0),
            stock       INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            image_url   TEXT    NOT NULL DEFAULT '',
            attributes  TEXT    NOT NULL DEFAULT '{}',
            created_at  TEXT    NOT NULL DEFAULT '',
            updated_at  TEXT    NOT NULL DEFAULT '',
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS addresses (
            address_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            province    TEXT    DEFAULT '',
            city        TEXT    DEFAULT '',
            district    TEXT    DEFAULT '',
            detail      TEXT    NOT NULL,
            is_default  INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0,1)),
            created_at  TEXT    NOT NULL DEFAULT '',
            updated_at  TEXT    NOT NULL DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            sku_id       INTEGER NOT NULL,
            product_id   INTEGER NOT NULL,
            quantity     INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
            selected     INTEGER NOT NULL DEFAULT 1 CHECK(selected IN (0,1)),
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL,
            FOREIGN KEY (user_id)    REFERENCES users(user_id)    ON DELETE CASCADE,
            FOREIGN KEY (sku_id)     REFERENCES product_skus(sku_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, sku_id)
        );

        CREATE TABLE IF NOT EXISTS favorites (
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            created_at  TEXT    NOT NULL,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (user_id)    REFERENCES users(user_id)    ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id       INTEGER PRIMARY KEY,
            user_id        INTEGER NOT NULL,
            shop_id        INTEGER,
            seller_id      INTEGER,
            status         TEXT    NOT NULL DEFAULT 'pending_payment'
                           CHECK(status IN ('pending_payment','paid','shipped','completed','cancelled','refund_pending','refunded')),
            total_amount   REAL    NOT NULL CHECK(total_amount >= 0),
            payable_amount REAL    NOT NULL CHECK(payable_amount >= 0),
            delivery_fee   REAL    NOT NULL DEFAULT 0 CHECK(delivery_fee >= 0),
            delivery_type  TEXT    NOT NULL DEFAULT 'standard',
            payment_type   TEXT,
            address_json   TEXT,
            remark         TEXT    DEFAULT '',
            paid_at        TEXT,
            shipped_at     TEXT,
            completed_at   TEXT,
            cancelled_at   TEXT,
            created_at     TEXT    NOT NULL,
            updated_at     TEXT    NOT NULL,
            FOREIGN KEY (user_id)  REFERENCES users(user_id),
            FOREIGN KEY (shop_id)  REFERENCES shops(shop_id),
            FOREIGN KEY (seller_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            sku_id        INTEGER,
            product_name  TEXT    NOT NULL,
            sku_name      TEXT,
            price         REAL    NOT NULL CHECK(price >= 0),
            quantity      INTEGER NOT NULL CHECK(quantity > 0),
            image_url     TEXT,
            FOREIGN KEY (order_id)   REFERENCES orders(order_id)   ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (sku_id)     REFERENCES product_skus(sku_id)
        );

        CREATE TABLE IF NOT EXISTS behavior_logs (
            log_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id     TEXT NOT NULL UNIQUE,
            user_id      INTEGER,
            session_id   TEXT,
            product_id   INTEGER,
            product_name TEXT,
            action       TEXT NOT NULL CHECK(action IN ('view','search','search_click','favorite','unfavorite','cart','purchase','refund')),
            category     TEXT,
            quantity     INTEGER,
            sku_id       INTEGER,
            sku_name     TEXT,
            order_id     INTEGER,
            amount       REAL,
            item_count   INTEGER,
            source       TEXT,
            exported_at  TEXT,
            created_at   TEXT NOT NULL,
            FOREIGN KEY (user_id)    REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS recommendation_results (
            rec_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            score       REAL    NOT NULL DEFAULT 0,
            reason_code TEXT    DEFAULT '',
            rank_no     INTEGER NOT NULL DEFAULT 0,
            batch_date  TEXT    NOT NULL,
            created_at  TEXT    NOT NULL,
            FOREIGN KEY (user_id)    REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, product_id, batch_date)
        );

        CREATE TABLE IF NOT EXISTS recommendation_runs (
            run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_date  TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','running','completed','failed')),
            total_users INTEGER DEFAULT 0,
            total_products INTEGER DEFAULT 0,
            duration_ms INTEGER,
            error_msg   TEXT,
            started_at  TEXT,
            finished_at TEXT,
            created_at  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS media_assets (
            asset_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id    INTEGER NOT NULL,
            object_key  TEXT    NOT NULL UNIQUE,
            folder      TEXT    NOT NULL DEFAULT 'products',
            filename    TEXT    NOT NULL,
            content_type TEXT   NOT NULL DEFAULT 'image/webp',
            size_bytes  INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT    NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users(user_id)
        );

        -- 索引
        CREATE INDEX IF NOT EXISTS idx_behavior_user_time
            ON behavior_logs(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_behavior_product
            ON behavior_logs(product_id);
        CREATE INDEX IF NOT EXISTS idx_behavior_action
            ON behavior_logs(action);
        CREATE INDEX IF NOT EXISTS idx_orders_user
            ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status
            ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_orders_shop
            ON orders(shop_id);
        CREATE INDEX IF NOT EXISTS idx_cart_user
            ON cart_items(user_id);
        CREATE INDEX IF NOT EXISTS idx_products_category
            ON products(category);
        CREATE INDEX IF NOT EXISTS idx_products_seller
            ON products(seller_id);
        CREATE INDEX IF NOT EXISTS idx_product_skus_product
            ON product_skus(product_id);
        CREATE INDEX IF NOT EXISTS idx_recommendation_user_batch
            ON recommendation_results(user_id, batch_date);
        CREATE INDEX IF NOT EXISTS idx_recommendation_run_batch
            ON recommendation_runs(batch_date);
    """)

    # ---- 兼容旧数据库的列补充 ----
    _add_column_if_missing(conn, "users", "history_cleared_at", "TEXT")
    _add_column_if_missing(conn, "sessions", "expires_at", "TEXT")
    _add_column_if_missing(conn, "products", "sales_count", "INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing(conn, "products", "shop_id", "INTEGER REFERENCES shops(shop_id)")
    _add_column_if_missing(conn, "products", "subcategory", "TEXT NOT NULL DEFAULT ''")
    _add_column_if_missing(conn, "product_skus", "sku_code", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "product_skus", "created_at", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "product_skus", "updated_at", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "addresses", "province", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "addresses", "city", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "addresses", "district", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "addresses", "created_at", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "addresses", "updated_at", "TEXT DEFAULT ''")
    _add_column_if_missing(conn, "orders", "shop_id", "INTEGER REFERENCES shops(shop_id)")
    _add_column_if_missing(conn, "orders", "seller_id", "INTEGER REFERENCES users(user_id)")
    _add_column_if_missing(conn, "orders", "shipped_at", "TEXT")
    _add_column_if_missing(conn, "orders", "completed_at", "TEXT")
    _add_column_if_missing(conn, "orders", "cancelled_at", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "event_id", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "session_id", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "source", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "exported_at", "TEXT")

    # 确保旧数据 event_id 非空
    conn.execute(
        "UPDATE behavior_logs SET event_id = 'legacy-' || log_id WHERE event_id IS NULL"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_behavior_event_id ON behavior_logs(event_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_behavior_exported ON behavior_logs(exported_at, created_at)"
    )

    # 为无子分类的旧商品自动补齐 subcategory
    _seed_subcategories(conn)


def _seed_subcategories(conn: sqlite3.Connection) -> None:
    """根据商品名称关键词自动填充 subcategory 字段（仅更新空值行）。"""
    if not conn.execute("SELECT 1 FROM products WHERE subcategory = '' OR subcategory IS NULL LIMIT 1").fetchone():
        return

    mapping = [
        # 数码
        ("%耳机%", "音频设备"), ("%音箱%", "音频设备"),
        ("%键盘%", "电脑配件"), ("%鼠标%", "电脑配件"), ("%扩展坞%", "电脑配件"),
        ("%支架%", "电脑配件"), ("%投屏%", "电脑配件"),
        ("%充电%", "充电设备"), ("%移动电源%", "充电设备"), ("%数据线%", "充电设备"),
        ("%摄像头%", "电脑配件"), ("%手环%", "智能穿戴"), ("%云台%", "摄影配件"),
        # 服饰
        ("%背包%", "箱包"), ("%鞋%", "鞋服"), ("%卫衣%", "鞋服"), ("%T恤%", "鞋服"),
        ("%毛衣%", "鞋服"), ("%衬衫%", "鞋服"), ("%裤%", "鞋服"), ("%防晒衣%", "鞋服"),
        ("%围巾%", "配饰"), ("%袜%", "配饰"), ("%皮带%", "配饰"), ("%冰袖%", "配饰"),
        ("%腰带%", "配饰"),
        # 家居
        ("%台灯%", "灯具照明"), ("%补光灯%", "灯具照明"), ("%落地灯%", "灯具照明"),
        ("%挂灯%", "灯具照明"), ("%杯%", "收纳清洁"), ("%置物架%", "收纳清洁"),
        ("%收纳%", "收纳清洁"), ("%刀架%", "收纳清洁"), ("%衣架%", "收纳清洁"),
        ("%防滑垫%", "收纳清洁"), ("%窗帘%", "家纺"), ("%毯%", "家纺"),
        ("%坐垫%", "家纺"), ("%床笠%", "家纺"), ("%加湿器%", "灯具照明"),
        ("%挂钟%", "灯具照明"), ("%桌%", "收纳清洁"),
        # 运动
        ("%水壶%", "户外装备"), ("%登山杖%", "户外装备"), ("%腰包%", "户外装备"),
        ("%露营%", "户外装备"), ("%手套%", "运动配件"), ("%弹力带%", "运动配件"),
        ("%毛巾%", "运动配件"), ("%泳镜%", "运动配件"), ("%羽毛球%", "运动配件"),
        ("%护膝%", "运动配件"), ("%跳绳%", "运动配件"), ("%瑜伽%", "运动配件"),
        ("%短袖%", "运动配件"), ("%跑鞋%", "鞋服"),
        # 食品
        ("%茶%", "冲调饮品"), ("%咖啡%", "冲调饮品"), ("%蜂蜜%", "冲调饮品"),
        ("%燕麦%", "冲调饮品"), ("%巧克力%", "休闲零食"), ("%坚果%", "休闲零食"),
        ("%牛肉%", "休闲零食"), ("%果冻%", "休闲零食"), ("%零食%", "休闲零食"),
        ("%大礼包%", "休闲零食"), ("%面包%", "烘焙食材"), ("%粉%", "烘焙食材"),
        # 美妆
        ("%面霜%", "面部护肤"), ("%防晒%", "面部护肤"), ("%洗面奶%", "面部护肤"),
        ("%面膜%", "面部护肤"), ("%精华%", "面部护肤"), ("%卸妆%", "面部护肤"),
        ("%洁面%", "面部护肤"), ("%口红%", "彩妆"), ("%眼影%", "彩妆"),
        ("%眉笔%", "彩妆"), ("%沐浴%", "身体护理"), ("%护发%", "身体护理"),
        ("%精油%", "身体护理"),
        # 图书
        ("%计算机%", "科技"),
        ("%算法%", "科技"),
        ("%设计模式%", "科技"),
        ("%JavaScript%", "科技"),
        ("%Python%", "科技"),
        ("%人性%", "人文社科"),
        ("%思考%", "人文社科"),
        ("%三体%", "文学小说"),
        ("%百年孤独%", "文学小说"),
        ("%小王子%", "文学小说"),
    ]
    for pattern, subcat in mapping:
        conn.execute(
            "UPDATE products SET subcategory = ? WHERE (subcategory = '' OR subcategory IS NULL) AND (name LIKE ? OR name LIKE ?)",
            (subcat, pattern, pattern),
        )
    # 仍未匹配的归为默认
    conn.execute(
        "UPDATE products SET subcategory = '其他' WHERE subcategory = '' OR subcategory IS NULL"
    )
