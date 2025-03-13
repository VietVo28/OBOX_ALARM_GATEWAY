from fastapi import APIRouter, Depends, Query
from typing import Annotated

from typing_extensions import Optional

from app.models.user import User
from app.core.auth import get_current_user

from app.dto.history_alarm_dto import history_alarm_create_DTO, HistoryAlarmGetAllDTO, HistoryAlarmGetCountDTO
from app.services.history_alarm_service import history_alarm_service

router = APIRouter()
prefix = "/history-alarm"
tags = ["history-alarm"]

current_user = Annotated[User, Depends(get_current_user)]

@router.post("/create")
async def create(request: history_alarm_create_DTO ,user: current_user):
    return await history_alarm_service.create(request)
@router.post("/get-all", description="ASC: tăng dần, DESC: giảm dần")
async def get_all(request: HistoryAlarmGetAllDTO ,user: current_user):
    return await history_alarm_service.get_all(request)
@router.get("/get-by-wireless-button-id", description="ASC: tăng dần, DESC: giảm dần")
async def get_by_wireless_button_id(
        user: current_user,
        key_word: str,
        page: int = Query(0, ge=0),
        size: int = Query(10, gt=0),
        is_full: bool = False,
        sort_order: Optional[str] = "desc"):
    return await history_alarm_service.get_by_wireless_button_id(key_word, page, size, is_full, sort_order)
@router.post("/get-count-by-wireless-button-id")
async def get_count_by_wireless_button_id(request: HistoryAlarmGetCountDTO ,user: current_user):
    return await history_alarm_service.get_count_by_wireless_button_id(request)