"""媒体存储：未配置 MinIO 时使用本地文件，配置后必须写入 MinIO。"""
import io
import json
import os
import threading
import time
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_client = None
_next_retry_at = 0.0
_lock = threading.Lock()
_RETRY_SECONDS = 5


class MediaStorageError(RuntimeError):
    """对象存储已配置但暂时不可用。"""


def _bucket_for(folder: str) -> str:
    if folder == "avatars":
        return os.getenv("MINIO_BUCKET_AVATARS", "avatars")
    if folder == "shop-logos":
        return os.getenv("MINIO_BUCKET_LOGOS", "shop-logos")
    return os.getenv("MINIO_BUCKET_PRODUCTS", "product-images")


def _minio_configured() -> bool:
    return bool(os.getenv("MINIO_ENDPOINT"))


def _try_minio():
    """建立连接并执行一次轻量 S3 请求，确认 MinIO 真的可用。"""
    try:
        from minio import Minio
        endpoint = os.getenv("MINIO_ENDPOINT", "")
        if not endpoint:
            return None
        c = Minio(
            endpoint,
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=(os.getenv("MINIO_SECURE", "false").lower() == "true"),
        )
        c.bucket_exists(_bucket_for("products"))
        return c
    except Exception:
        return None


def _ensure_minio():
    """连接失败只短暂缓存，避免 MinIO 恢复后仍永久回退到本地。"""
    global _client, _next_retry_at
    if not _minio_configured():
        return None
    if _client is not None:
        return _client
    if time.monotonic() < _next_retry_at:
        return None

    with _lock:
        if _client is not None:
            return _client
        if time.monotonic() < _next_retry_at:
            return None
        _client = _try_minio()
        if _client is None:
            _next_retry_at = time.monotonic() + _RETRY_SECONDS
        return _client


def _mark_minio_unavailable() -> None:
    global _client, _next_retry_at
    _client = None
    _next_retry_at = time.monotonic() + _RETRY_SECONDS


def ensure_buckets():
    """在 MinIO 可用时补齐项目需要的公开读取桶。"""
    client = _ensure_minio()
    if not client:
        return False
    try:
        for folder in ("products", "avatars", "shop-logos"):
            bucket = _bucket_for(folder)
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
            client.set_bucket_policy(
                bucket,
                json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket}/*"],
                    }],
                }),
            )
        return True
    except Exception:
        _mark_minio_unavailable()
        return False


def upload_image(data, filename, content_type="image/webp", folder="products"):
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "webp"
    object_key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    if _minio_configured():
        client = _ensure_minio()
        if not client:
            raise MediaStorageError("MinIO 暂时不可用，请稍后重试上传")
        try:
            client.put_object(_bucket_for(folder), object_key, io.BytesIO(data), len(data), content_type)
            return object_key
        except Exception as exc:
            _mark_minio_unavailable()
            raise MediaStorageError("MinIO 上传失败，请稍后重试") from exc

    # 仅当项目完全未配置 MinIO 时才使用本地文件。
    target = UPLOAD_DIR / object_key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return object_key


def get_object_url(object_key, folder="products"):
    if _minio_configured():
        ep = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9002")
        return f"http://{ep}/{_bucket_for(folder)}/{object_key}"
    return f"/static/uploads/{object_key}"


def delete_object(object_key, folder="products"):
    if _minio_configured():
        client = _ensure_minio()
        if not client:
            raise MediaStorageError("MinIO 暂时不可用，请稍后重试删除")
        try:
            client.remove_object(_bucket_for(folder), object_key)
            return
        except Exception as exc:
            _mark_minio_unavailable()
            raise MediaStorageError("MinIO 删除失败，请稍后重试") from exc

    target = UPLOAD_DIR / object_key
    if target.exists():
        target.unlink()
