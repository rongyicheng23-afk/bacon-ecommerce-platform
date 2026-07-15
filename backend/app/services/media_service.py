"""媒体存储 — 自动检测 MinIO / 本地回退"""
import io, os, uuid, threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_client = None
_minio_ok = None  # None=未检测, True=可用, False=不可用


def _try_minio():
    """在子线程中检测 MinIO（防止 SDK 挂起主线程）"""
    try:
        from minio import Minio
        endpoint = os.getenv("MINIO_ENDPOINT", "")
        if not endpoint:
            return None
        c = Minio(endpoint, access_key=os.getenv("MINIO_ACCESS_KEY","minioadmin"),
                  secret_key=os.getenv("MINIO_SECRET_KEY","minioadmin"), secure=False)
        c.list_buckets()
        return c
    except Exception:
        return None


def _ensure_minio():
    global _client, _minio_ok
    if _minio_ok is not None:
        return _client if _minio_ok else None

    result = [None]
    def runner():
        result[0] = _try_minio()
    t = threading.Thread(target=runner, daemon=True)
    t.start()
    t.join(timeout=3)  # 最多等 3 秒

    if result[0] is not None:
        _client = result[0]
        _minio_ok = True
        return _client
    else:
        _minio_ok = False
        return None


def ensure_buckets():
    _ensure_minio()


def upload_image(data, filename, content_type="image/webp", folder="products"):
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "webp"
    object_key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    client = _ensure_minio()
    if client:
        try:
            bucket = os.getenv("MINIO_BUCKET_PRODUCTS", "product-images")
            if folder == "avatars":
                bucket = os.getenv("MINIO_BUCKET_AVATARS", "avatars")
            elif folder == "shop-logos":
                bucket = os.getenv("MINIO_BUCKET_LOGOS", "shop-logos")

            def do_upload():
                client.put_object(bucket, object_key, io.BytesIO(data), len(data), content_type)
            t = threading.Thread(target=do_upload, daemon=True)
            t.start()
            t.join(timeout=5)
            if not t.is_alive():
                return object_key
        except Exception:
            pass

    # 本地回退
    target = UPLOAD_DIR / object_key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return object_key


def get_object_url(object_key, folder="products"):
    if _ensure_minio():
        ep = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9002")
        bucket = os.getenv("MINIO_BUCKET_PRODUCTS", "product-images")
        return f"http://{ep}/{bucket}/{object_key}"
    return f"/static/uploads/{object_key}"


def delete_object(object_key, folder="products"):
    client = _ensure_minio()
    if client:
        try:
            bucket = os.getenv("MINIO_BUCKET_PRODUCTS", "product-images")
            client.remove_object(bucket, object_key)
        except Exception:
            pass
    else:
        target = UPLOAD_DIR / object_key
        if target.exists():
            target.unlink()
