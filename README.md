# Bacon Mall — 电商个性化推荐系统

"专业实习2"项目：基于用户行为日志的电商个性化推荐系统。前端 Vue 3 + 后端 FastAPI + 大数据 Hadoop。

## 项目结构

```
bacon-mall-frontend/     ← Git 仓库根目录
├── src/                 # Vue 3 前端源码
├── backend/             # FastAPI 后端源码
│   ├── app/
│   │   ├── main.py      # 应用入口
│   │   ├── core/        # 配置、安全
│   │   ├── db/          # 数据库、模型、种子数据
│   │   ├── routers/     # API 路由
│   │   ├── schemas/     # Pydantic 数据模型
│   │   └── services/    # 业务逻辑
│   ├── .env.example     # 环境变量模板
│   └── requirements.txt
└── package.json
```

---

## 快速启动

### 后端

```bash
cd backend

# 1. 创建虚拟环境（仅首次）
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 启动
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动后打开：
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

### 前端

```bash
# 在项目根目录
npm install
npm run dev -- --host 127.0.0.1
```

浏览器打开 http://127.0.0.1:5173/

---

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 买家 | student@example.com | 123456 |
| 商家 | seller@example.com | 123456 |

---

## 页面入口

```text
/                 首页
/products         商品库
/product/:id      商品详情
/cart             购物车
/checkout         订单确认
/payment/:orderId 模拟支付
/orders           我的订单
/order/:id        订单详情
/profile          个人中心
/login            登录
/register         注册
/seller           商家后台
/category/:cat    分类页
```

---

## 环境变量

后端 `backend/.env`（可选，默认值即可运行）：

```bash
BACON_DB_PATH=                  # 数据库路径，默认 backend/bacon_mall.db
BACON_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

前端 `.env`（可选）：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite 6 + TypeScript + Pinia + Axios |
| 后端 | FastAPI + SQLite + Pydantic |
| 大数据 | Hadoop HDFS + YARN + Streaming（计划中） |

## 后续计划

见 [backend/BACKEND_BIGDATA_PLAN.md](backend/BACKEND_BIGDATA_PLAN.md)
