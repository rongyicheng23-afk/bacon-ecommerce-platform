"""数据库表创建"""
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
            status        TEXT    NOT NULL DEFAULT 'active',
            history_cleared_at TEXT,
            created_at    TEXT    NOT NULL,
            updated_at    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            created_at  TEXT    NOT NULL,
            expires_at  TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id   INTEGER,
            name        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'active',
            image_urls  TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL,
            FOREIGN KEY (seller_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS product_skus (
            sku_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL,
            image_url   TEXT    NOT NULL,
            attributes  TEXT    NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS addresses (
            address_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            detail      TEXT    NOT NULL,
            is_default  INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            sku_id       INTEGER NOT NULL,
            product_id   INTEGER NOT NULL,
            quantity     INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
            selected     INTEGER NOT NULL DEFAULT 1,
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL,
            FOREIGN KEY (user_id)    REFERENCES users(user_id),
            FOREIGN KEY (sku_id)     REFERENCES product_skus(sku_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, sku_id)
        );

        CREATE TABLE IF NOT EXISTS favorites (
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            created_at  TEXT    NOT NULL,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (user_id)    REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id       INTEGER PRIMARY KEY,
            user_id        INTEGER NOT NULL,
            status         TEXT    NOT NULL DEFAULT 'pending_payment'
                           CHECK(status IN ('pending_payment','paid','shipped','completed','cancelled')),
            total_amount   REAL    NOT NULL,
            payable_amount REAL    NOT NULL,
            delivery_fee   REAL    NOT NULL DEFAULT 0,
            delivery_type  TEXT    NOT NULL DEFAULT 'standard',
            payment_type   TEXT,
            address_json   TEXT,
            remark         TEXT    DEFAULT '',
            paid_at        TEXT,
            created_at     TEXT    NOT NULL,
            updated_at     TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            sku_id        INTEGER,
            product_name  TEXT    NOT NULL,
            sku_name      TEXT,
            price         REAL    NOT NULL,
            quantity      INTEGER NOT NULL,
            image_url     TEXT,
            FOREIGN KEY (order_id)   REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS behavior_logs (
            log_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id     TEXT UNIQUE,
            user_id      INTEGER,
            session_id   TEXT,
            product_id   INTEGER,
            product_name TEXT,
            action       TEXT    NOT NULL,
            category     TEXT,
            quantity     INTEGER,
            sku_id       INTEGER,
            sku_name     TEXT,
            order_id     INTEGER,
            amount       REAL,
            item_count   INTEGER,
            source       TEXT,
            exported_at  TEXT,
            created_at   TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_behavior_user_time
            ON behavior_logs(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_behavior_product
            ON behavior_logs(product_id);
        CREATE INDEX IF NOT EXISTS idx_orders_user
            ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_cart_user
            ON cart_items(user_id);
    """)

    # 兼容已经存在的 SQLite 数据库。CREATE TABLE IF NOT EXISTS 不会自动补新列。
    _add_column_if_missing(conn, "users", "history_cleared_at", "TEXT")
    _add_column_if_missing(conn, "sessions", "expires_at", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "event_id", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "session_id", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "source", "TEXT")
    _add_column_if_missing(conn, "behavior_logs", "exported_at", "TEXT")

    conn.execute(
        "UPDATE behavior_logs SET event_id = 'legacy-' || log_id WHERE event_id IS NULL"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_behavior_event_id ON behavior_logs(event_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_behavior_exported ON behavior_logs(exported_at, created_at)"
    )
