"""种子数据：demo 用户 + 30 商品（与前端 mock 对齐）"""
import json
import sqlite3

from app.core.security import hash_password
from app.db.database import now_iso

PRODUCT_SEEDS = [
    ("智能降噪耳机", "通勤、运动和学习都适合的无线蓝牙耳机，支持主动降噪与通透模式。", 188, "数码",
     ["https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85"]),
    ("轻薄机械键盘", "适合办公、学习和编程的轻薄机械键盘，红轴静音设计。", 269, "数码",
     ["https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85"]),
    ("保温咖啡杯", "简洁耐用的日常保温杯，适合办公桌和通勤，12 小时保温。", 79, "家居",
     ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1577937927133-6c9a5c1c5c9f?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1563297320-b6a2c95cd396?auto=format&fit=crop&w=900&q=85"]),
    ("运动休闲背包", "轻便大容量，适合上课、出行和日常通勤，防泼水面料。", 159, "服饰",
     ["https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85"]),
    ("护眼台灯", "柔和照明，适合夜间学习和居家办公，多档亮度和色温调节。", 129, "家居",
     ["https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85"]),
    ("便携移动电源", "20000mAh 大容量，小巧便携，满足手机、耳机等设备日常充电。", 109, "数码",
     ["https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85"]),
    ("无线充电底座", "桌面无线快充，支持手机和耳机同时补电，兼容 Qi 协议。", 99, "数码",
     ["https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1622045246592-7b3b8b3b3b3b?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85"]),
    ("简约双肩包", "适合通勤和短途出行的轻量背包，多隔层设计，背负舒适。", 139, "服饰",
     ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85"]),
    ("人体工学鼠标", "长时间办公更舒适，减少手腕压力，支持蓝牙和 2.4G 双模连接。", 119, "数码",
     ["https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85"]),
    ("香薰加湿器", "适合宿舍和卧室的小型桌面加湿器，搭配精油使用更放松。", 89, "家居",
     ["https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1585342289952-2ef11c70c5c5?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85"]),
    ("瑜伽垫", "加厚防滑设计，适合居家健身和瑜伽练习，附赠收纳绑带。", 79, "运动",
     ["https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85"]),
    ("速干跑步短袖", "透气速干面料，适合夏季户外运动和日常穿搭。", 69, "运动",
     ["https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1434389677669-e08b4cda4a10?auto=format&fit=crop&w=900&q=85"]),
    ("智能手环", "心率血氧监测，50 米防水，14 天超长续航，支持多种运动模式。", 229, "数码",
     ["https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1557438159-51eec7a6c9e8?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85"]),
    ("简约帆布鞋", "百搭经典款，舒适耐磨，适合日常通勤和休闲出行。", 149, "服饰",
     ["https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85"]),
    ("桌面 LED 补光灯", "三色温调节，适合直播补光、视频会议和桌面摄影。", 129, "数码",
     ["https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1517242027094-631f8c218a0f?auto=format&fit=crop&w=900&q=85"]),
    ("纯棉床笠三件套", "亲肤纯棉面料，弹力包裹床垫，含床笠 + 枕套一对。", 179, "家居",
     ["https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1616627562376-f1e5c9ba8f4e?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85"]),
    ("零食大礼包", "坚果果干混合装，办公室休闲零食组合，独立小包装方便分享。", 88, "食品",
     ["https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85"]),
    ("手冲咖啡套装", "包含手冲壶、滤杯和分享壶，适合入门手冲咖啡爱好者。", 219, "食品",
     ["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?auto=format&fit=crop&w=900&q=85"]),
    ("高清网络摄像头", "1080P 自动对焦，内置降噪麦克风，即插即用适合远程办公。", 169, "数码",
     ["https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85"]),
    ("羊毛混纺围巾", "秋冬保暖必备，柔软舒适不扎脖，多色可选百搭实用。", 89, "服饰",
     ["https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1606744824167-1e3fbc2a67d7?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85"]),
    ("无绳跳绳", "配重球设计模拟真实跳绳手感，室内静音不扰邻，适合居家运动。", 39, "运动",
     ["https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1601422407692-ec4eeec6207a?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85"]),
    ("实木置物架", "多层开放式设计，适合客厅、书房收纳书籍和装饰品。", 259, "家居",
     ["https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85"]),
    ("颈挂式运动耳机", "轻量化颈挂设计，IPX5 防水防汗，12 小时续航适合户外运动。", 139, "数码",
     ["https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85"]),
    ("弹力修身长裤", "高弹力面料穿着舒适，修身版型不紧绷，适合通勤和商务休闲。", 169, "服饰",
     ["https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85"]),
    ("冷萃咖啡壶", "玻璃瓶身 + 细密滤网，睡前加水冷藏，早起即享顺滑冷萃。", 99, "食品",
     ["https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85"]),
    ("防蓝光眼镜", "适合长时间面对屏幕的办公和学习人群，减少眼疲劳。", 59, "数码",
     ["https://images.unsplash.com/photo-1574258495973-f010dfbb5371?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1577803645773-f96470509666?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85"]),
    ("瑜伽砖两块装", "高密度 EVA 材质，辅助拉伸和体式练习，初学者必备工具。", 35, "运动",
     ["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85"]),
    ("遮光窗帘", "加厚三层遮光面料，隔音隔热，适合卧室和影音室使用。", 119, "家居",
     ["https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85"]),
    ("每日坚果混合装", "核桃腰果巴旦木开心果 4 种混合，每日一小袋补充营养。", 69, "食品",
     ["https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1536591146385-e7fa9ab39d28?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1508717272100-8ee02bc8593c?auto=format&fit=crop&w=900&q=85"]),
    ("折叠露营椅", "轻量铝合金框架，承重 120kg，收纳方便适合户外郊游。", 189, "运动",
     ["https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85",
      "https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85"]),
]

COLORS = ["深空灰", "珍珠白", "午夜蓝"]
VERSIONS = [
    ("标准版", 0, 0),
    ("Pro 版", 60, -15),
    ("旗舰版", 130, -30),
]


def seed_demo_data(conn: sqlite3.Connection) -> None:
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        ts = now_iso()
        conn.execute(
            """INSERT INTO users (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            ("荣同学", "student@example.com", "13800002026", "buyer", None, None, hash_password("123456"), "active", ts, ts),
        )
        conn.execute(
            """INSERT INTO users (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            ("Bacon 数码旗舰店", "seller@example.com", "13900002026", "seller", "Bacon 数码旗舰店", "数码", hash_password("123456"), "active", ts, ts),
        )

    product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if product_count > 0:
        return

    seller = conn.execute("SELECT user_id FROM users WHERE role = 'seller' LIMIT 1").fetchone()
    seller_id = seller["user_id"] if seller else None
    ts = now_iso()

    for idx, (name, desc, price, cat, imgs) in enumerate(PRODUCT_SEEDS):
        product_id = 1001 + idx
        cur = conn.execute(
            """INSERT INTO products (product_id, seller_id, name, description, price, stock, status, image_urls, category, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (product_id, seller_id, name, desc, price, 0, "active", json.dumps(imgs, ensure_ascii=False), cat, ts, ts),
        )
        total_stock = 0
        total_price = float("inf")
        for ci, color in enumerate(COLORS):
            for vi, (vname, vdelta, sdelta) in enumerate(VERSIONS):
                sku_name = f"{color} · {vname}"
                sku_price = price + vdelta
                sku_stock = max(5, 40 - ci * 8 - sdelta)
                total_stock += sku_stock
                total_price = min(total_price, sku_price)
                conn.execute(
                    """INSERT INTO product_skus (product_id, name, price, stock, image_url, attributes)
                       VALUES (?,?,?,?,?,?)""",
                    (product_id, sku_name, sku_price, sku_stock, imgs[ci % len(imgs)], json.dumps({"颜色": color, "版本": vname}, ensure_ascii=False)),
                )
        # 更新商品级别的价格和库存
        conn.execute(
            "UPDATE products SET price = ?, stock = ? WHERE product_id = ?",
            (total_price, total_stock, product_id),
        )
