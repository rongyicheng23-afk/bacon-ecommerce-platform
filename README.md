# Bacon Mall — 电商个性化推荐系统

"专业实习2"项目：基于用户行为日志的电商个性化推荐系统。

前端 Vue 3 + 后端 FastAPI + 大数据 Hadoop。

---

## 环境要求

| 工具 | 版本要求 | 检查命令 |
|------|---------|----------|
| Node.js | ≥ 18 | `node -v` |
| Python | ≥ 3.10 | `python3 --version` |
| Git | 任意 | `git --version` |

建议使用 **VS Code** 打开项目根目录，终端会自动定位到正确路径。

---

## 项目结构

```
bacon-mall-frontend/               ← Git 仓库根目录
├── src/                           # Vue 3 前端源码
├── package.json                   # 前端依赖
├── .env                           # 前端环境变量
├── docs/                          # 项目文档
└── backend/                       # ⚠️ 旧副本，已废弃，请勿修改
                                    #    ↓ 实际后端在这里 ↓

bacon-mall-backend/                ← 🟢 真实后端（用 VS Code 打开此目录开终端）
├── app/
│   ├── main.py                    # 应用入口
│   ├── core/config.py             # 配置 + .env 加载
│   ├── db/                        # 数据库模型、种子、迁移
│   ├── routers/                   # API 路由
│   ├── schemas/                   # Pydantic 模型
│   └── services/                  # 业务逻辑
├── bigdata/                       # Hadoop 推荐引擎
│   ├── streaming/                 # Mapper/Reducer
│   └── scripts/                   # 管道脚本
├── scripts/                       # 工具脚本（MinIO 启动等）
├── requirements.txt
├── .env                           # MinIO 等配置
└── .env.example
```

---

## 首次启动（完整步骤）

### 1. 克隆项目

```bash
git clone https://github.com/rongyicheng23-afk/bacon-ecommerce-platform.git
cd bacon-ecommerce-platform
```

### 2. 安装前端依赖

```bash
npm install
```

前端 `.env` 已内置在仓库中，通常无需修改。

### 3. 安装后端依赖

```bash
cd ../bacon-mall-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. 启动 MinIO（可选，存储商品图片）

```bash
cd ../bacon-mall-backend
bash scripts/start_minio.sh
# API: http://127.0.0.1:9002  控制台: http://127.0.0.1:9003
# 账号: minioadmin / minioadmin
```

### 5. 启动

**需要同时开三个终端：**

终端 1 — MinIO（可选）：
```bash
cd bacon-mall-backend && bash scripts/start_minio.sh
```

终端 2 — 后端：
```bash
cd bacon-mall-backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

终端 3 — 前端：
```bash
cd bacon-mall-frontend && npm run dev -- --host 127.0.0.1 --port 5175
```

### 6. 打开浏览器

| 地址 | 说明 |
|------|------|
| `http://127.0.0.1:5175/` | 前端页面 |
| `http://127.0.0.1:8001/docs` | 后端 API 文档（Swagger） |
| `http://127.0.0.1:8001/api/health` | 后端健康检查 |
| `http://127.0.0.1:9003` | MinIO 控制台 |

---

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 买家 | `student@example.com` | `123456` |
| 商家 | `seller@example.com` | `123456` |

首次启动后端会自动创建数据库和种子数据（104 件商品、2 个账号）。

---

## 页面一览

| 路径 | 页面 | 需要登录 |
|------|------|----------|
| `/` | 首页 | — |
| `/products` | 商品库 | — |
| `/product/:id` | 商品详情 | — |
| `/category/:cat` | 分类页 | — |
| `/login` | 登录 | — |
| `/register` | 注册 | — |
| `/cart` | 购物车 | 买家 |
| `/checkout` | 订单确认 | 买家 |
| `/payment/:orderId` | 模拟支付 | 买家 |
| `/orders` | 我的订单 | 买家 |
| `/order/:id` | 订单详情 | 买家 |
| `/profile` | 个人中心 | 买家 |
| `/history` | 浏览历史 | 买家 |
| `/seller` | 商家后台 | 商家 |
| `/messages` | 消息中心 | — |
| `/new-arrivals` | 新品首发 | — |
| `/hot-sales` | 热卖榜单 | — |

---

## 常见问题

### 前端页面报 "Network Error"

**原因**：后端未启动，或前端 `.env` 中 API 地址不对。

**解决**：
1. 确认终端 1 的后端正运行（看到 `Uvicorn running on http://127.0.0.1:8000`）
2. 确认 `项目根目录/.env` 中有 `VITE_API_BASE_URL=http://127.0.0.1:8000/api`
3. 重启前端（`Ctrl+C` 后重新 `npm run dev`）

### 后端启动报端口占用

```bash
# 查出占用 8000 端口的进程
lsof -i :8000
# 换一个端口启动
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```
如果换了端口，记得同步改前端 `.env` 中的端口号。

### 数据库删了想重建

```bash
cd backend
rm -f bacon_mall.db
# 重启后端会自动建表 + 种子数据
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 旧数据库升级

```bash
cd backend && source .venv/bin/activate
python -m app.db.migrate
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端框架 | Vue 3 + Vite + TypeScript |
| 状态管理 | Pinia |
| HTTP 客户端 | Axios（自动携带 Token） |
| 后端框架 | FastAPI |
| 数据库 | SQLite（15 张表，含 CHECK/FK/UNIQUE 约束） |
| 认证 | Session Token（PBKDF2 密码哈希） |
| 大数据 | Hadoop HDFS + YARN + Streaming（计划中） |

## 后续计划

见 [backend/BACKEND_BIGDATA_PLAN.md](backend/BACKEND_BIGDATA_PLAN.md)
