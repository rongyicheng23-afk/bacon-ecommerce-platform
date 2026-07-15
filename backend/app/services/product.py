"""商品业务逻辑"""
import json
import sqlite3

from app.db.database import get_connection, now_iso


def row_to_sku(row) -> dict:
    return {
        "skuId": row["sku_id"], "productId": row["product_id"],
        "name": row["name"], "price": row["price"], "stock": row["stock"],
        "imageUrl": row["image_url"], "attributes": json.loads(row["attributes"]),
    }


def row_to_product(row, skus: list[dict]) -> dict:
    return {
        "productId": row["product_id"], "sellerId": row["seller_id"],
        "name": row["name"], "description": row["description"],
        "price": row["price"], "stock": row["stock"], "status": row["status"],
        "imageUrls": json.loads(row["image_urls"]), "category": row["category"],
        "skus": skus, "createdAt": row["created_at"], "updatedAt": row["updated_at"],
    }


def _load_skus(conn: sqlite3.Connection, product_id: int) -> list[dict]:
    rows = conn.execute("SELECT * FROM product_skus WHERE product_id = ? ORDER BY sku_id", (product_id,)).fetchall()
    return [row_to_sku(r) for r in rows]


def list_products(category: str | None = None, keyword: str | None = None,
                  sort: str | None = None, page: int = 1, page_size: int = 20) -> dict:
    with get_connection() as conn:
        wheres = ["status = 'active'"]
        params: list = []
        if category:
            wheres.append("category = ?")
            params.append(category)
        if keyword:
            wheres.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        where = " AND ".join(wheres)
        total = conn.execute(f"SELECT COUNT(*) FROM products WHERE {where}", params).fetchone()[0]

        order = "product_id"
        if sort == "price-asc": order = "price ASC"
        elif sort == "price-desc": order = "price DESC"
        elif sort == "stock-desc": order = "stock DESC"

        offset = (page - 1) * page_size
        rows = conn.execute(
            f"SELECT * FROM products WHERE {where} ORDER BY {order} LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()

        items = [row_to_product(r, _load_skus(conn, r["product_id"])) for r in rows]
        return {"items": items, "total": total, "page": page, "pageSize": page_size}


def get_product(product_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
        if not row:
            return None
        return row_to_product(row, _load_skus(conn, product_id))


def list_categories() -> list[str]:
    with get_connection() as conn:
        # 优先从 categories 表读取
        rows = conn.execute(
            "SELECT name FROM categories WHERE status = 'active' ORDER BY sort_order"
        ).fetchall()
        if rows:
            return [r["name"] for r in rows]
        # 兼容旧数据
        rows = conn.execute(
            "SELECT DISTINCT category FROM products WHERE status = 'active' ORDER BY category"
        ).fetchall()
        return [r["category"] for r in rows]


def get_category_tree() -> list[dict]:
    with get_connection() as conn:
        cats = conn.execute(
            "SELECT * FROM categories WHERE status = 'active' ORDER BY sort_order"
        ).fetchall()
        if not cats:
            # 兼容旧数据
            rows = conn.execute(
                "SELECT DISTINCT category FROM products WHERE status = 'active' ORDER BY category"
            ).fetchall()
            return [{"categoryId": 0, "name": r["category"], "parentId": None, "children": []} for r in rows]

        nodes = {}
        for c in cats:
            nodes[c["category_id"]] = {
                "categoryId": c["category_id"],
                "name": c["name"],
                "parentId": c["parent_id"],
                "sortOrder": c["sort_order"],
                "icon": c["icon"],
                "children": [],
            }

        roots = []
        for node in nodes.values():
            parent = nodes.get(node["parentId"])
            if parent:
                parent["children"].append(node)
            else:
                roots.append(node)
        return roots


def _validate_category(conn: sqlite3.Connection, category: str) -> str:
    category = category.strip()
    row = conn.execute(
        "SELECT 1 FROM categories WHERE name = ? AND status = 'active'",
        (category,),
    ).fetchone()
    if not row:
        raise ValueError("商品分类不存在或已停用")
    return category


def seller_create_product(seller_id: int, data: dict) -> dict:
    ts = now_iso()
    imgs = data.get("imageUrls") or [
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85",
        "https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85",
        "https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85",
        "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85",
    ]
    with get_connection() as conn:
        category = _validate_category(conn, data["category"])
        cur = conn.execute(
            """INSERT INTO products (seller_id, name, description, price, stock, status, image_urls, category, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (seller_id, data["name"], data["description"], data["price"], data["stock"],
             "active", json.dumps(imgs, ensure_ascii=False), category, ts, ts),
        )
        product_id = cur.lastrowid
        # 创建默认 SKU
        conn.execute(
            """INSERT INTO product_skus (product_id, name, price, stock, image_url, attributes)
               VALUES (?,?,?,?,?,?)""",
            (product_id, "标准版", data["price"], data["stock"], imgs[0],
             json.dumps({"颜色": "默认", "版本": "标准版"}, ensure_ascii=False)),
        )
        row = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
        return row_to_product(row, _load_skus(conn, product_id))


def seller_update_product_status(product_id: int, seller_id: int, status: str) -> dict | None:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE product_id = ? AND seller_id = ?",
            (product_id, seller_id),
        ).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE products SET status = ?, updated_at = ? WHERE product_id = ?",
            (status, ts, product_id),
        )
        row = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
        return row_to_product(row, _load_skus(conn, product_id))


def get_shop_profile(owner_user_id: int) -> dict | None:
    with get_connection() as conn:
        shop = conn.execute(
            "SELECT * FROM shops WHERE owner_user_id = ?", (owner_user_id,)
        ).fetchone()
        if not shop:
            return None
        products = conn.execute(
            "SELECT COUNT(*) AS cnt FROM products WHERE seller_id = ? AND status = 'active'",
            (owner_user_id,),
        ).fetchone()
        recent = conn.execute(
            "SELECT * FROM products WHERE seller_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 8",
            (owner_user_id,),
        ).fetchall()
        return {
            "shopId": shop["shop_id"],
            "ownerUserId": shop["owner_user_id"],
            "name": shop["name"],
            "description": shop["description"],
            "logoUrl": shop["logo_url"],
            "status": shop["status"],
            "productCount": products["cnt"],
            "createdAt": shop["created_at"],
            "updatedAt": shop["updated_at"],
            "recentProducts": [row_to_product(r, _load_skus(conn, r["product_id"])) for r in recent],
        }


def seller_list_products(seller_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE seller_id = ? ORDER BY created_at DESC",
            (seller_id,),
        ).fetchall()
        return [row_to_product(r, _load_skus(conn, r["product_id"])) for r in rows]


def seller_update_product(product_id: int, seller_id: int, data: dict) -> dict | None:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM products WHERE product_id = ? AND seller_id = ?", (product_id, seller_id)).fetchone()
        if not row:
            return None
        if "category" in data:
            data["category"] = _validate_category(conn, data["category"])
        conn.execute(
            """UPDATE products SET name=COALESCE(?,name), description=COALESCE(?,description),
               category=COALESCE(?,category), updated_at=? WHERE product_id=?""",
            (data.get("name"), data.get("description"), data.get("category"), ts, product_id),
        )

        # 更新 imageUrls（如果传入）
        if "imageUrls" in data and data["imageUrls"] is not None:
            conn.execute(
                "UPDATE products SET image_urls = ?, updated_at = ? WHERE product_id = ?",
                (json.dumps(data["imageUrls"], ensure_ascii=False), ts, product_id),
            )

        sku_rows = conn.execute(
            "SELECT sku_id, price FROM product_skus WHERE product_id = ? ORDER BY sku_id",
            (product_id,),
        ).fetchall()
        if "price" in data and sku_rows:
            price_delta = data["price"] - row["price"]
            for sku in sku_rows:
                conn.execute(
                    "UPDATE product_skus SET price = ? WHERE sku_id = ?",
                    (max(0, sku["price"] + price_delta), sku["sku_id"]),
                )

        if "stock" in data and sku_rows:
            base_stock, remainder = divmod(data["stock"], len(sku_rows))
            for index, sku in enumerate(sku_rows):
                conn.execute(
                    "UPDATE product_skus SET stock = ? WHERE sku_id = ?",
                    (base_stock + (1 if index < remainder else 0), sku["sku_id"]),
                )

        aggregate = conn.execute(
            "SELECT MIN(price) AS min_price, SUM(stock) AS total_stock FROM product_skus WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        conn.execute(
            "UPDATE products SET price = ?, stock = ?, updated_at = ? WHERE product_id = ?",
            (
                aggregate["min_price"] if aggregate["min_price"] is not None else data.get("price", row["price"]),
                aggregate["total_stock"] if aggregate["total_stock"] is not None else data.get("stock", row["stock"]),
                ts,
                product_id,
            ),
        )
        row = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
        return row_to_product(row, _load_skus(conn, product_id))
