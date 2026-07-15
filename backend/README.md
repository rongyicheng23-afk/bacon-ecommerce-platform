# Bacon Mall Backend

FastAPI 后端，位于 monorepo 的 `backend/` 目录下。

## 启动方式

```bash
cd bacon-mall-frontend/backend
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

启动后打开：

- Swagger 文档：http://127.0.0.1:8001/docs
- 健康检查：http://127.0.0.1:8001/api/health

## MinIO 对象存储

```bash
bash scripts/start_minio.sh
```

| 服务 | 地址 | 账号 |
|------|------|------|
| API | http://127.0.0.1:9002 | minioadmin / minioadmin |
| 控制台 | http://127.0.0.1:9001 | minioadmin / minioadmin |

三个桶：`product-images` / `avatars` / `shop-logos`（启动后自动创建）。

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 买家 | student@example.com | 123456 |
| 商家 | seller@example.com | 123456 |

## 数据库重建

```bash
rm -f bacon_mall.db
# 重启后端会自动建表 + 种子数据
```
