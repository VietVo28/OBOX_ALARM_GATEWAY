from app.dto.wifi_dto import WiFiConnectRequest
from app.services.wifi_service import wifi_service
from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()
current_user = Annotated[User, Depends(get_current_user)]

@router.get("/scan")
def scan_wifi():
    return wifi_service.scan_wifi()
@router.post("/connect")
def connect_wifi(request: WiFiConnectRequest):
    return wifi_service.connect_wifi(request)
@router.get("/disconnect")
def disconnect_wifi():
    return wifi_service.disconnect_wifi()