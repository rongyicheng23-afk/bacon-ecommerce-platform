# Bacon Mall Backend

这是 Bacon Mall 的 FastAPI 后端。正式应用代码位于 `app/` 目录。

## 启动方式

```bash
cd /Users/rongyicheng/Desktop/专业实习2-项目/bacon-mall-backend
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

如果 8000 端口被占用，可以换成：

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

启动后打开：

```txt
http://127.0.0.1:8000/docs
```

根目录的 `main.py` 仅用于兼容旧命令，新开发统一从 `app.main` 启动。

## 测试账号

买家：

```txt
student@example.com
123456
```

商家：

```txt
seller@example.com
123456
```
