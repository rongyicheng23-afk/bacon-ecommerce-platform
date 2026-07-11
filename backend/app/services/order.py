"""订单 & 购物车 & 收藏 & 地址业务逻辑"""
import json
import secrets
from datetime import datetime

from app.db.database import get_connection, now_iso
from app.services.behavior import insert_behavior


# ---- 地址 ----
def list_addresses(user_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC, address_id", (user_id,)).fetchall()
        return [{"id": r["address_id"], "name": r["name"], "phone": r["phone"], "detail": r["detail"], "isDefault": bool(r["is_default"])} for r in rows]


def create_address(user_id: int, data: dict) -> dict:
    with get_connection() as conn:
        if data.get("isDefault"):
            conn.execute("UPDATE addresses SET is_default = 0 WHERE user_id = ?", (user_id,))
        cur = conn.execute(
            "INSERT INTO addresses (user_id, name, phone, detail, is_default) VALUES (?,?,?,?,?)",
            (user_id, data["name"], data["phone"], data["detail"], 1 if data.get("isDefault") else 0),
        )
        row = conn.execute("SELECT * FROM addresses WHERE address_id = ?", (cur.lastrowid,)).fetchone()
        return {"id": row["address_id"], "name": row["name"], "phone": row["phone"], "detail": row["detail"], "isDefault": bool(row["is_default"])}


def update_address(user_id: int, address_id: int, data: dict) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM addresses WHERE address_id = ? AND user_id = ?", (address_id, user_id)).fetchone()
        if not row: return None
        if data.get("isDefault") is True:
            conn.execute("UPDATE addresses SET is_default = 0 WHERE user_id = ?", (user_id,))
        is_default = None
        if "isDefault" in data:
            is_default = 1 if data["isDefault"] else 0
        conn.execute(
            "UPDATE addresses SET name=COALESCE(?,name), phone=COALESCE(?,phone), detail=COALESCE(?,detail), is_default=COALESCE(?,is_default) WHERE address_id=?",
            (data.get("name"), data.get("phone"), data.get("detail"), is_default, address_id),
        )
        row = conn.execute("SELECT * FROM addresses WHERE address_id = ?", (address_id,)).fetchone()
        return {"id": row["address_id"], "name": row["name"], "phone": row["phone"], "detail": row["detail"], "isDefault": bool(row["is_default"])}


def delete_address(user_id: int, address_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM addresses WHERE address_id = ? AND user_id = ?", (address_id, user_id))
        return cur.rowcount > 0


# ---- 购物车 ----
def get_cart(user_id: int) -> dict:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT ci.*, p.name, p.description, p.image_urls, p.category, p.status AS product_status,
                   ps.name AS sku_name, ps.price AS sku_price, ps.stock AS sku_stock, ps.image_url AS sku_image
            FROM cart_items ci
            JOIN products p ON p.product_id = ci.product_id
            JOIN product_skus ps ON ps.sku_id = ci.sku_id
            WHERE ci.user_id = ?
            ORDER BY ci.created_at DESC
        """, (user_id,)).fetchall()

        items = []
        for r in rows:
            items.append({
                "cartItemId": r["cart_item_id"], "productId": r["product_id"],
                "skuId": r["sku_id"], "skuName": r["sku_name"],
                "quantity": r["quantity"], "price": r["sku_price"],
                "stock": r["sku_stock"], "name": r["name"],
                "description": r["description"],
                "imageUrl": r["sku_image"] or json.loads(r["image_urls"])[0],
                "category": r["category"], "selected": bool(r["selected"]),
                "createdAt": r["created_at"], "updatedAt": r["updated_at"],
            })
        total_qty = sum(i["quantity"] for i in items if i["selected"])
        total_amt = sum(i["price"] * i["quantity"] for i in items if i["selected"])
        return {"items": items, "totalQuantity": total_qty, "totalAmount": round(total_amt, 2)}


def add_cart_item(user_id: int, product_id: int, sku_id: int, quantity: int = 1) -> dict:
    ts = now_iso()
    with get_connection() as conn:
        sku = conn.execute(
            """SELECT ps.*, p.name AS product_name, p.category, p.status AS product_status
               FROM product_skus ps
               JOIN products p ON p.product_id = ps.product_id
               WHERE ps.sku_id = ? AND ps.product_id = ?""",
            (sku_id, product_id),
        ).fetchone()
        if not sku or sku["product_status"] != "active":
            raise ValueError("商品或 SKU 不存在")

        current = conn.execute(
            "SELECT quantity FROM cart_items WHERE user_id = ? AND sku_id = ?",
            (user_id, sku_id),
        ).fetchone()
        next_quantity = quantity + (current["quantity"] if current else 0)
        if next_quantity > sku["stock"]:
            raise ValueError(f"库存不足，当前最多可购买 {sku['stock']} 件")

        conn.execute(
            """INSERT INTO cart_items (user_id, sku_id, product_id, quantity, selected, created_at, updated_at)
               VALUES (?,?,?,?,1,?,?) ON CONFLICT(user_id, sku_id) DO UPDATE SET quantity = quantity + ?, updated_at = ?""",
            (user_id, sku_id, product_id, quantity, ts, ts, quantity, ts),
        )
        insert_behavior(
            conn,
            user_id=user_id,
            action="cart",
            product_id=product_id,
            product_name=sku["product_name"],
            category=sku["category"],
            quantity=quantity,
            sku_id=sku_id,
            sku_name=sku["name"],
            source="cart_api",
        )
    return get_cart(user_id)


def update_cart_item(user_id: int, item_id: int, quantity: int) -> dict:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute(
            """SELECT ci.cart_item_id, ps.stock
               FROM cart_items ci
               JOIN product_skus ps ON ps.sku_id = ci.sku_id
               WHERE ci.cart_item_id = ? AND ci.user_id = ?""",
            (item_id, user_id),
        ).fetchone()
        if not row:
            raise ValueError("购物车商品不存在")
        if quantity > row["stock"]:
            raise ValueError(f"库存不足，当前最多可购买 {row['stock']} 件")
        conn.execute("UPDATE cart_items SET quantity = ?, updated_at = ? WHERE cart_item_id = ? AND user_id = ?",
                     (quantity, ts, item_id, user_id))
    return get_cart(user_id)


def remove_cart_item(user_id: int, item_id: int) -> dict:
    with get_connection() as conn:
        conn.execute("DELETE FROM cart_items WHERE cart_item_id = ? AND user_id = ?", (item_id, user_id))
    return get_cart(user_id)


# ---- 收藏 ----
def list_favorites(user_id: int) -> list[int]:
    with get_connection() as conn:
        rows = conn.execute("SELECT product_id FROM favorites WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        return [r["product_id"] for r in rows]


def add_favorite(user_id: int, product_id: int) -> None:
    with get_connection() as conn:
        product = conn.execute(
            "SELECT name, category FROM products WHERE product_id = ? AND status = 'active'",
            (product_id,),
        ).fetchone()
        if not product:
            raise ValueError("商品不存在或已下架")
        cur = conn.execute(
            "INSERT OR IGNORE INTO favorites (user_id, product_id, created_at) VALUES (?,?,?)",
            (user_id, product_id, now_iso()),
        )
        if cur.rowcount:
            insert_behavior(
                conn,
                user_id=user_id,
                action="favorite",
                product_id=product_id,
                product_name=product["name"],
                category=product["category"],
                source="favorite_api",
            )


def remove_favorite(user_id: int, product_id: int) -> None:
    with get_connection() as conn:
        product = conn.execute(
            "SELECT name, category FROM products WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        cur = conn.execute(
            "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        )
        if cur.rowcount and product:
            insert_behavior(
                conn,
                user_id=user_id,
                action="unfavorite",
                product_id=product_id,
                product_name=product["name"],
                category=product["category"],
                source="favorite_api",
            )


# ---- 订单 ----
def _generate_order_id(conn) -> int:
    # 15 位数字不会超过 JavaScript 的安全整数范围；随机尾号避免同秒重复。
    prefix = int(datetime.now().strftime("%y%m%d%H%M%S")) * 1000
    for _ in range(20):
        order_id = prefix + secrets.randbelow(1000)
        exists = conn.execute(
            "SELECT 1 FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()
        if not exists:
            return order_id
    raise ValueError("订单号生成失败，请稍后重试")


def create_order(user_id: int, data: dict) -> dict:
    ts = now_iso()
    with get_connection() as conn:
        # 读取购物车选中项
        cart_rows = conn.execute("""
            SELECT ci.*, ps.price AS sku_price, ps.stock AS sku_stock, ps.name AS sku_name, ps.image_url AS sku_image,
                   p.name AS product_name, p.image_urls, p.category, p.status AS product_status,
                   p.seller_id
            FROM cart_items ci
            JOIN product_skus ps ON ps.sku_id = ci.sku_id
            JOIN products p ON p.product_id = ci.product_id
            WHERE ci.user_id = ? AND ci.selected = 1
        """, (user_id,)).fetchall()
        if not cart_rows:
            raise ValueError("购物车没有选中商品")

        seller_ids = {row["seller_id"] for row in cart_rows}
        if None in seller_ids:
            raise ValueError("购物车中存在无所属商家的商品")
        if len(seller_ids) != 1:
            raise ValueError("暂不支持跨店铺合并下单，请按店铺分别结算")

        for row in cart_rows:
            if row["product_status"] != "active":
                raise ValueError(f"《{row['product_name']}》已下架")
            if row["quantity"] < 1:
                raise ValueError("商品数量必须大于 0")
            if row["quantity"] > row["sku_stock"]:
                raise ValueError(f"《{row['product_name']}》库存不足")

        # 读取地址快照
        addr = conn.execute("SELECT * FROM addresses WHERE address_id = ? AND user_id = ?", (data["addressId"], user_id)).fetchone()
        if not addr:
            raise ValueError("收货地址不存在")
        addr_json = json.dumps(
            {"name": addr["name"], "phone": addr["phone"], "detail": addr["detail"]},
            ensure_ascii=False,
        )

        order_id = _generate_order_id(conn)
        total = sum(r["sku_price"] * r["quantity"] for r in cart_rows)
        delivery_fee = 12 if data.get("deliveryType") == "express" else 0

        conn.execute(
            """INSERT INTO orders (order_id, user_id, status, total_amount, payable_amount, delivery_fee, delivery_type, payment_type, address_json, remark, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (order_id, user_id, "pending_payment", total, total + delivery_fee, delivery_fee,
             data.get("deliveryType", "standard"), data.get("paymentType", "alipay"),
             addr_json, data.get("remark", ""), ts, ts),
        )
        for r in cart_rows:
            stock_update = conn.execute(
                "UPDATE product_skus SET stock = stock - ? WHERE sku_id = ? AND stock >= ?",
                (r["quantity"], r["sku_id"], r["quantity"]),
            )
            if stock_update.rowcount != 1:
                raise ValueError(f"《{r['product_name']}》库存不足")
            conn.execute(
                "UPDATE products SET stock = MAX(0, stock - ?), updated_at = ? WHERE product_id = ?",
                (r["quantity"], ts, r["product_id"]),
            )
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, sku_id, product_name, sku_name, price, quantity, image_url) VALUES (?,?,?,?,?,?,?,?)",
                (order_id, r["product_id"], r["sku_id"], r["product_name"], r["sku_name"], r["sku_price"], r["quantity"], r["sku_image"] or json.loads(r["image_urls"])[0]),
            )
        # 清除购物车已下单商品
        conn.execute("DELETE FROM cart_items WHERE user_id = ? AND selected = 1", (user_id,))
    return get_order(order_id, user_id)


def list_orders(user_id: int, status: str | None = None) -> list[dict]:
    with get_connection() as conn:
        wheres = ["user_id = ?"]
        params: list = [user_id]
        if status:
            wheres.append("status = ?")
            params.append(status)
        where = " AND ".join(wheres)
        rows = conn.execute(f"SELECT * FROM orders WHERE {where} ORDER BY created_at DESC", params).fetchall()
        return [_order_to_dict(conn, r) for r in rows]


def get_order(order_id: int, user_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_id = ? AND user_id = ?", (order_id, user_id)).fetchone()
        if not row:
            return None
        return _order_to_dict(conn, row)


def _order_to_dict(conn, row) -> dict:
    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (row["order_id"],)).fetchall()
    return {
        "orderId": row["order_id"], "userId": row["user_id"],
        "totalAmount": row["total_amount"], "payableAmount": row["payable_amount"],
        "deliveryFee": row["delivery_fee"], "deliveryType": row["delivery_type"],
        "paymentType": row["payment_type"], "status": row["status"],
        "address": json.loads(row["address_json"]) if row["address_json"] else None,
        "remark": row["remark"], "paidAt": row["paid_at"],
        "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        "items": [{
            "orderItemId": i["order_item_id"], "productId": i["product_id"],
            "skuId": i["sku_id"], "skuName": i["sku_name"],
            "productName": i["product_name"], "price": i["price"],
            "quantity": i["quantity"], "imageUrl": i["image_url"],
        } for i in items],
    }


def cancel_order(user_id: int, order_id: int) -> dict | None:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_id = ? AND user_id = ? AND status = 'pending_payment'", (order_id, user_id)).fetchone()
        if not row: return None
        items = conn.execute(
            "SELECT product_id, sku_id, quantity FROM order_items WHERE order_id = ?",
            (order_id,),
        ).fetchall()
        for item in items:
            if item["sku_id"] is not None:
                conn.execute(
                    "UPDATE product_skus SET stock = stock + ? WHERE sku_id = ?",
                    (item["quantity"], item["sku_id"]),
                )
            conn.execute(
                "UPDATE products SET stock = stock + ?, updated_at = ? WHERE product_id = ?",
                (item["quantity"], ts, item["product_id"]),
            )
        conn.execute("UPDATE orders SET status = 'cancelled', updated_at = ? WHERE order_id = ?", (ts, order_id))
    return get_order(order_id, user_id)


def pay_order(user_id: int, order_id: int, payment_type: str) -> dict | None:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_id = ? AND user_id = ? AND status = 'pending_payment'", (order_id, user_id)).fetchone()
        if not row: return None
        conn.execute("UPDATE orders SET status = 'paid', payment_type = ?, paid_at = ?, updated_at = ? WHERE order_id = ?", (payment_type, ts, ts, order_id))
        items = conn.execute(
            """SELECT oi.*, p.category
               FROM order_items oi
               JOIN products p ON p.product_id = oi.product_id
               WHERE oi.order_id = ?""",
            (order_id,),
        ).fetchall()
        for item in items:
            insert_behavior(
                conn,
                user_id=user_id,
                action="purchase",
                product_id=item["product_id"],
                product_name=item["product_name"],
                category=item["category"],
                quantity=item["quantity"],
                sku_id=item["sku_id"],
                sku_name=item["sku_name"],
                order_id=order_id,
                amount=item["price"] * item["quantity"],
                item_count=item["quantity"],
                source="order_payment",
            )
    return get_order(order_id, user_id)


def seller_ship_order(seller_id: int, order_id: int) -> dict | None:
    ts = now_iso()
    with get_connection() as conn:
        row = conn.execute(
            """SELECT o.* FROM orders o
               WHERE o.order_id = ? AND o.status = 'paid'
                 AND EXISTS (
                     SELECT 1 FROM order_items oi
                     JOIN products p ON p.product_id = oi.product_id
                     WHERE oi.order_id = o.order_id AND p.seller_id = ?
                 )
                 AND NOT EXISTS (
                     SELECT 1 FROM order_items oi
                     JOIN products p ON p.product_id = oi.product_id
                     WHERE oi.order_id = o.order_id
                       AND (p.seller_id IS NULL OR p.seller_id != ?)
                 )""",
            (order_id, seller_id, seller_id),
        ).fetchone()
        if not row: return None
        conn.execute("UPDATE orders SET status = 'shipped', updated_at = ? WHERE order_id = ?", (ts, order_id))
    return get_order(order_id, row["user_id"])


def seller_list_orders(seller_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT DISTINCT o.* FROM orders o
            JOIN order_items oi ON oi.order_id = o.order_id
            JOIN products p ON p.product_id = oi.product_id
            WHERE p.seller_id = ?
            ORDER BY o.created_at DESC
        """, (seller_id,)).fetchall()
        return [_order_to_dict(conn, r) for r in rows]
