from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.dto.setting_dto import SettingCreateDTO, TestDTO
from app.models.user import User
from app.services.setting_service import setting_service

router = APIRouter()
prefix = "/setting"
tags = ["setting"]

current_user = Annotated[User, Depends(get_current_user)]


@router.post("/create")
async def create(request: SettingCreateDTO, user: current_user):
    return await setting_service.create(request)


@router.get("/get-by-key")
async def get_by_key(key: str,user: current_user):
    return await setting_service.get_by_key(key)


@router.post("/test")
async def test(data:TestDTO):
    return await setting_service.test(data)