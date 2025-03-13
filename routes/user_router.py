from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.dto.user_dto import UserRegisterDTO, UserUpdateDTO
from app.models.user import User
from app.services.user_service import user_service

router = APIRouter()
prefix = "/user"
tags = ["user"]
current_user = Annotated[User, Depends(get_current_user)]


@router.post("/create")
async def create(request: UserRegisterDTO, user: current_user):
    return await user_service.register_user(request)


@router.put("/update")
async def update(request: UserUpdateDTO, user: current_user, id: str):
    return await user_service.update_user(request, id)


@router.post("/login")
async def create(request: UserRegisterDTO):
    return await user_service.login(request)


@router.get("/get-all")
async def get_all(user: current_user, page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                  key_work: Optional[str] = Query(None), ):
    return await user_service.get_all(page, size, key_work)

@router.delete("/delete")
async def delete(user: current_user, id: str):
    # user_service.__dir__()
    return await user_service.delete_user(id, user)