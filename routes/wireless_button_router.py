from typing import Annotated, Optional

from fastapi import APIRouter, Request, Depends, Query
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core.auth import get_current_user
from app.dto.wireless_button_dto import WirelessCreateDTO, WirelessUpdateDTO
from app.models.user import User
from app.services.wireless_button_service import wireless_button_service

router = APIRouter()
prefix = "/wireless-button"
tags = ["wireless-button"]

current_user = Annotated[User, Depends(get_current_user)]


@router.post("/create")
async def create(request: WirelessCreateDTO, user: current_user):
    return await wireless_button_service.create(request)


@router.put("/update")
async def update(request: WirelessUpdateDTO, user: current_user):
    return await wireless_button_service.update(request)


@router.get("/get-all")
async def get_all(user: current_user, page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                  key_work: Optional[str] = Query(None),is_full: bool = False ):
    return await wireless_button_service.get_all(page, size, key_work,is_full)


@router.get("/get-by-id")
async def get_by_id(id: str, user: current_user):
    return await wireless_button_service.get_by_id(id)


@router.delete("/delete")
async def delete(id: str, user: current_user):
    return await wireless_button_service.delete(id)
