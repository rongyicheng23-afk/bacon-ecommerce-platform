"""用户认证路由"""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from app.schemas.common import ApiResponse
from app.schemas.user import LoginRequest, RegisterRequest, UpdateProfileRequest
from app.services.auth import get_current_user, register_user, login_user, logout_user, update_profile

router = APIRouter(prefix="/api", tags=["认证"])


@router.post("/user/register", response_model=ApiResponse)
@router.post("/auth/register", response_model=ApiResponse)
def register(payload: RegisterRequest) -> ApiResponse:
    if payload.role == "seller" and not payload.shopName:
        raise HTTPException(400, "商家账号需要填写店铺名称")
    try:
        return ApiResponse(data=register_user(payload.model_dump()))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/user/login", response_model=ApiResponse)
@router.post("/auth/login", response_model=ApiResponse)
def login(payload: LoginRequest) -> ApiResponse:
    try:
        return ApiResponse(data=login_user(payload.email, payload.password))
    except ValueError as e:
        raise HTTPException(401, str(e))


@router.post("/user/logout", response_model=ApiResponse)
@router.post("/auth/logout", response_model=ApiResponse)
def logout(authorization: Annotated[str | None, Header()] = None) -> ApiResponse:
    logout_user(authorization)
    return ApiResponse(data=None)


@router.get("/user/me", response_model=ApiResponse)
def get_me(authorization: Annotated[str | None, Header()] = None) -> ApiResponse:
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(401, "请先登录")
    return ApiResponse(data=user)


@router.put("/user/me", response_model=ApiResponse)
def update_me(payload: UpdateProfileRequest, authorization: Annotated[str | None, Header()] = None) -> ApiResponse:
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(401, "请先登录")
    return ApiResponse(data=update_profile(user["userId"], payload.model_dump(exclude_none=True)))
