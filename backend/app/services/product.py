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
        rows = conn.execute("SELECT DISTINCT category FROM products WHERE status = 'active' ORDER BY category").fetchall()
        return [r["category"] for r in rows]


def seller_update_product(product_id: int, seller_id: int, data: dict) -> dict | None:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM products WHERE product_id = ? AND seller_id = ?", (product_id, seller_id)).fetchone()
        if not row:
            return None
        conn.execute(
            """UPDATE products SET name=COALESCE(?,name), description=COALESCE(?,description),
               category=COALESCE(?,category), updated_at=? WHERE product_id=?""",
            (data.get("name"), data.get("description"), data.get("category"), ts, product_id),
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
