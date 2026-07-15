"""数据库升级脚本 — 用于已有数据库的结构迁移。

使用方法:
    cd backend && source .venv/bin/activate
    python -m app.db.migrate

该脚本会安全地补全缺失的列、表和索引，不会删除已有数据。
"""
from app.db.database import get_connection, now_iso


def upgrade():
    ts = now_iso()
    with get_connection() as conn:
        print(f"[migrate] 开始升级 {conn.execute('PRAGMA database_list').fetchone()['file']}")

        # ---- products 补列 ----
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(products)")}
        migrations = [
            ("sales_count", "INTEGER NOT NULL DEFAULT 0"),
            ("shop_id", "INTEGER REFERENCES shops(shop_id)"),
        ]
        for col, defn in migrations:
            if col not in cols:
                conn.execute(f"ALTER TABLE products ADD COLUMN {col} {defn}")
                print(f"[migrate] products.{col} 已添加")

        # ---- product_skus 补列 ----
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(product_skus)")}
        migrations = [
            ("sku_code", "TEXT DEFAULT ''"),
            ("created_at", "TEXT DEFAULT ''"),
            ("updated_at", "TEXT DEFAULT ''"),
        ]
        for col, defn in migrations:
            if col not in cols:
                conn.execute(f"ALTER TABLE product_skus ADD COLUMN {col} {defn}")
                print(f"[migrate] product_skus.{col} 已添加")

        # ---- addresses 补列 ----
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(addresses)")}
        migrations = [
            ("province", "TEXT DEFAULT ''"),
            ("city", "TEXT DEFAULT ''"),
            ("district", "TEXT DEFAULT ''"),
            ("created_at", "TEXT DEFAULT ''"),
            ("updated_at", "TEXT DEFAULT ''"),
        ]
        for col, defn in migrations:
            if col not in cols:
                conn.execute(f"ALTER TABLE addresses ADD COLUMN {col} {defn}")
                print(f"[migrate] addresses.{col} 已添加")

        # ---- orders 补列 ----
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(orders)")}
        migrations = [
            ("shop_id", "INTEGER REFERENCES shops(shop_id)"),
            ("seller_id", "INTEGER REFERENCES users(user_id)"),
            ("shipped_at", "TEXT"),
            ("completed_at", "TEXT"),
            ("cancelled_at", "TEXT"),
        ]
        for col, defn in migrations:
            if col not in cols:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {col} {defn}")
                print(f"[migrate] orders.{col} 已添加")

        # ---- behavior_logs 补列 ----
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(behavior_logs)")}
        migrations = [
            ("event_id", "TEXT"),
            ("session_id", "TEXT"),
            ("source", "TEXT"),
            ("exported_at", "TEXT"),
        ]
        for col, defn in migrations:
            if col not in cols:
                conn.execute(f"ALTER TABLE behavior_logs ADD COLUMN {col} {defn}")
                print(f"[migrate] behavior_logs.{col} 已添加")

        # ---- 新建表（IF NOT EXISTS 安全） ----
        new_tables = [
            ("shops", """CREATE TABLE IF NOT EXISTS shops (
                shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL, description TEXT DEFAULT '',
                logo_url TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('pending','active','closed')),
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                FOREIGN KEY (owner_user_id) REFERENCES users(user_id)
            )"""),
            ("categories", """CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE, parent_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','inactive')),
                icon TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES categories(category_id)
            )"""),
            ("recommendation_results", """CREATE TABLE IF NOT EXISTS recommendation_results (
                rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
                score REAL NOT NULL DEFAULT 0, reason_code TEXT DEFAULT '',
                rank_no INTEGER NOT NULL DEFAULT 0,
                batch_date TEXT NOT NULL, created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                UNIQUE(user_id, product_id, batch_date)
            )"""),
            ("recommendation_runs", """CREATE TABLE IF NOT EXISTS recommendation_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','running','completed','failed')),
                total_users INTEGER DEFAULT 0, total_products INTEGER DEFAULT 0,
                duration_ms INTEGER, error_msg TEXT,
                started_at TEXT, finished_at TEXT, created_at TEXT NOT NULL
            )"""),
        ]
        for table_name, sql in new_tables:
            exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
            ).fetchone()
            if not exists:
                conn.execute(sql)
                print(f"[migrate] 新建表 {table_name}")

        # ---- 补齐索引 ----
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_behavior_action ON behavior_logs(action)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_shop ON orders(shop_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_products_seller ON products(seller_id)",
            "CREATE INDEX IF NOT EXISTS idx_product_skus_product ON product_skus(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_recommendation_user_batch ON recommendation_results(user_id, batch_date)",
            "CREATE INDEX IF NOT EXISTS idx_recommendation_run_batch ON recommendation_runs(batch_date)",
        ]
        for sql in indexes:
            conn.execute(sql)

        # ---- 补齐 event_id ----
        conn.execute("UPDATE behavior_logs SET event_id = 'legacy-' || log_id WHERE event_id IS NULL")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_behavior_event_id ON behavior_logs(event_id)")

        print("[migrate] 升级完成")


if __name__ == "__main__":
    upgrade()
