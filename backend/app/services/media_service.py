"""媒体存储服务 — 本地文件系统（默认）/ MinIO（配置 MINIO_ENDPOINT 后启用）

MinIO 不可用时自动回退到本地存储，不影响业务运行。
"""
import io
import os
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_client = None
_minio_available = None  # None=未检测, True=可用, False=不可用


def _check_minio():
    """检测 MinIO 是否可用（带超时，不阻塞）"""
    global _minio_available, _client
    if _minio_available is not None:
        return _minio_available

    endpoint = os.getenv("MINIO_ENDPOINT", "")
    if not endpoint:
        _minio_available = False
        return False

    try:
        from minio import Minio
        from app.core.config import MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE
        import socket
        host, port = endpoint.rsplit(":", 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        if result != 0:
            _minio_available = False
            return False

        _client = Minio(endpoint, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)
        # 确保 bucket
        from app.core.config import MINIO_BUCKET_PRODUCTS, MINIO_BUCKET_AVATARS, MINIO_BUCKET_LOGOS
        for bucket in [MINIO_BUCKET_PRODUCTS, MINIO_BUCKET_AVATARS, MINIO_BUCKET_LOGOS]:
            if not _client.bucket_exists(bucket):
                _client.make_bucket(bucket)
                _client.set_bucket_policy(bucket, {
                    "Version": "2012-10-17",
                    "Statement": [{"Effect": "Allow", "Principal": {"AWS": ["*"]}, "Action": ["s3:GetObject"], "Resource": [f"arn:aws:s3:::{bucket}/*"]}],
                })
        _minio_available = True
        return True
    except Exception:
        _minio_available = False
        return False


def ensure_buckets():
    """启动时调用，不阻塞"""
    _check_minio()


def upload_image(data: bytes, filename: str, content_type: str = "image/webp",
                 folder: str = "products") -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "webp"
    object_key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    if _check_minio() and _client:
        from app.core.config import MINIO_BUCKET_PRODUCTS, MINIO_BUCKET_AVATARS, MINIO_BUCKET_LOGOS
        bucket = {"avatars": MINIO_BUCKET_AVATARS, "shop-logos": MINIO_BUCKET_LOGOS}.get(folder, MINIO_BUCKET_PRODUCTS)
        _client.put_object(bucket, object_key, io.BytesIO(data), length=len(data), content_type=content_type)
    else:
        target = UPLOAD_DIR / object_key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    return object_key


def get_object_url(object_key: str, folder: str = "products") -> str:
    if _check_minio():
        from app.core.config import MINIO_ENDPOINT, MINIO_BUCKET_PRODUCTS, MINIO_BUCKET_AVATARS, MINIO_BUCKET_LOGOS
        bucket = {"avatars": MINIO_BUCKET_AVATARS, "shop-logos": MINIO_BUCKET_LOGOS}.get(folder, MINIO_BUCKET_PRODUCTS)
        return f"http://{MINIO_ENDPOINT}/{bucket}/{object_key}"
    return f"/static/uploads/{object_key}"


def delete_object(object_key: str, folder: str = "products") -> None:
    if _check_minio() and _client:
        from app.core.config import MINIO_BUCKET_PRODUCTS, MINIO_BUCKET_AVATARS, MINIO_BUCKET_LOGOS
        bucket = {"avatars": MINIO_BUCKET_AVATARS, "shop-logos": MINIO_BUCKET_LOGOS}.get(folder, MINIO_BUCKET_PRODUCTS)
        try:
            _client.remove_object(bucket, object_key)
        except Exception:
            pass
    else:
        target = UPLOAD_DIR / object_key
        if target.exists():
            target.unlink()
