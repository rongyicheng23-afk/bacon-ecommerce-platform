# Bacon Mall 演示脚本

## 演示路径

```
用户登录 → 浏览数码商品 → 收藏耳机 → 加购键盘 → 购买移动电源
    → 导出行为日志 → Hadoop 计算 → 导入推荐 → 首页数码占比上升
```

---

## 第一步：启动系统

```bash
# 终端 1 — 后端
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 终端 2 — 前端
npm run dev -- --host 127.0.0.1
```

打开 `http://127.0.0.1:5173/`

---

## 第二步：用户登录 + 浏览数码商品

```bash
# 登录（或浏览器操作）
curl -X POST http://127.0.0.1:8000/api/user/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"123456"}'
```

在浏览器中：
1. 登录 `student@example.com / 123456`
2. 首页 → 浏览以下数码商品（点击进入详情页）：

| 商品ID | 商品名 | 分类 |
|--------|--------|------|
| 1001 | 智能降噪耳机 | 数码 |
| 1002 | 轻薄机械键盘 | 数码 |
| 1006 | 便携移动电源 | 数码 |
| 1009 | 人体工学鼠标 | 数码 |
| 1013 | 智能手环 | 数码 |
| 1015 | 桌面LED补光灯 | 数码 |
| 1019 | 高清网络摄像头 | 数码 |

每次进入详情页 = 一条 `view` 行为日志。

---

## 第三步：收藏 + 加购 + 购买

```bash
TOKEN="<从上一步获取>"

# 1. 收藏耳机 (productId=1001)
curl -X POST http://127.0.0.1:8000/api/favorites/1001 \
  -H "Authorization: Bearer $TOKEN"

# 2. 加购键盘 (productId=1002, quantity=1)
curl -X POST http://127.0.0.1:8000/api/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"product_id":1002,"quantity":1}'

# 3. 购买移动电源 (productId=1006)
# 先加购
curl -X POST http://127.0.0.1:8000/api/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"product_id":1006,"quantity":1}'

# 下单
curl -X POST http://127.0.0.1:8000/api/order/create \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"products":[{"productId":1006,"quantity":1}]}'

# 获取订单ID并支付
ORDER_ID=$(curl -s http://127.0.0.1:8000/api/order/list \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['orderId'])")

curl -X POST http://127.0.0.1:8000/api/payment/pay \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"orderId\":$ORDER_ID,\"paymentMethod\":1}"
```

**此时行为日志表已有：7 view + 1 favorite + 2 cart + 1 purchase = 11 条。**

---

## 第四步：查看行为日志

```bash
cd backend && source .venv/bin/activate
python3 -c "
from app.db.database import get_connection
with get_connection() as conn:
    rows = conn.execute('SELECT action, category, COUNT(*) FROM behavior_logs GROUP BY action, category').fetchall()
    for r in rows: print(f'{r[0]:12s} {r[1]:6s} x{r[2]}')
"
```

---

## 第五步：导出 → Hadoop → 推荐

```bash
# 本地模式（不需要 Hadoop 集群）
bash bigdata/scripts/run_pipeline.sh local
```

---

## 第六步：查看推荐结果

```bash
python3 -c "
from app.db.database import get_connection
with get_connection() as conn:
    recs = conn.execute('''
        SELECT p.name, p.category, r.score, r.reason_code
        FROM recommendation_results r
        JOIN products p ON p.product_id = r.product_id
        WHERE r.user_id = 1
        ORDER BY r.rank_no LIMIT 10
    ''').fetchall()
    for r in recs:
        print(f'  {r[\"name\"]:20s} {r[\"category\"]:4s} {r[\"score\"]:5.1f} — {r[\"reason_code\"]}')
"
```

**预期：Top 10 中数码商品 ≥ 8 个。**

---

## 第七步：刷新首页

浏览器刷新 `http://127.0.0.1:5173/`

"为你精选"区域应展示更多数码商品（耳机、键盘、鼠标、摄像头…）。

---

## 演示检查清单

- [ ] 后端启动，`/docs` 可访问
- [ ] 前端首页正常加载 104 件商品
- [ ] 登录成功，行为日志开始记录
- [ ] 浏览数码商品 → behavior_logs 有 view 记录
- [ ] 收藏/加购/购买 → behavior_logs 有对应记录
- [ ] 导出 JSONL 文件 → `exports/behavior-YYYY-MM-DD.jsonl`
- [ ] 管道运行成功 → `recommendation_results` 表有数据
- [ ] 推荐结果可解释 → reason_code 显示"偏好数码分类"
- [ ] 首页推荐变化 → 数码商品占比上升
