"""媒体上传路由"""
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, UploadFile, File
from app.schemas.common import ApiResponse
from app.services.auth import get_current_user
from app.services.media_service import MediaStorageError, upload_image, get_object_url, delete_object

router = APIRouter(prefix="/api", tags=["媒体"])

AUTH = Annotated[str | None, Header()]
MAX_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "image/gif", "image/svg+xml", "video/mp4",
}


def _require_auth(auth: str | None) -> dict:
    user = get_current_user(auth)
    if not user:
        raise HTTPException(401, "请先登录")
    return user


@router.post("/media/upload", response_model=ApiResponse)
async def upload(
    file: UploadFile = File(...),
    folder: str = "products",
    authorization: AUTH = None,
) -> ApiResponse:
    user = _require_auth(authorization)
    if folder not in VALID_FOLDERS:
        raise HTTPException(400, f"无效的文件夹: {folder}")
    if user["role"] == "buyer" and folder not in ("avatars",):
        raise HTTPException(403, "买家仅可上传头像")

    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"不支持的文件类型: {file.content_type}")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(400, f"文件过大，最大 {MAX_SIZE // 1024 // 1024} MB")

    filename = file.filename or "upload.webp"
    try:
        object_key = upload_image(data, filename, file.content_type or "image/webp", folder)
    except MediaStorageError as exc:
        raise HTTPException(503, str(exc)) from exc
    url = get_object_url(object_key, folder)

    # 记录到 media_assets 表
    from app.db.database import get_connection, now_iso
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO media_assets (owner_id, object_key, folder, filename, content_type, size_bytes, created_at) VALUES (?,?,?,?,?,?,?)",
            (user["userId"], object_key, folder, filename, file.content_type or "image/webp", len(data), now_iso()),
        )

    return ApiResponse(data={"objectKey": object_key, "url": url, "folder": folder})


VALID_FOLDERS = {"products", "avatars", "shop-logos"}


def _validate_object_key(key: str) -> str:
    """防止路径穿越：拒绝 .. / 和绝对路径"""
    if not key or ".." in key or key.startswith("/") or "\\" in key:
        raise HTTPException(400, "无效的文件路径")
    return key


@router.delete("/media/delete", response_model=ApiResponse)
def delete(object_key: str, folder: str = "products", authorization: AUTH = None) -> ApiResponse:
    user = _require_auth(authorization)
    if folder not in VALID_FOLDERS:
        raise HTTPException(400, f"无效的文件夹: {folder}")
    _validate_object_key(object_key)
    # 商品图和店铺图仅商家可删
    if folder in ("products", "shop-logos") and user["role"] != "seller":
        raise HTTPException(403, "仅商家可删除商品/店铺图片")
    try:
        delete_object(object_key, folder)
    except MediaStorageError as exc:
        raise HTTPException(503, str(exc)) from exc
    return ApiResponse(data=None)
