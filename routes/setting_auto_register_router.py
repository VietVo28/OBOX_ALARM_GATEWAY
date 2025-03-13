from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.dto.camera_dto import GetRTSPCameraDTO, CameraCreateDTO, CameraUpdateDTO
from app.dto.setting_auto_registe_dto import SettingAutoRegisterDTO
from app.models.user import User
from app.services.camera_service import camera_service
from app.services.setting_auto_register_service import setting_auto_register_service
from app.utils.rtsp import get_retsp_onvif

router = APIRouter()
prefix = "/setting-auto-register"
tags = ["setting-auto-register"]

current_user = Annotated[User, Depends(get_current_user)]

# user: current_user
@router.post("/create")
async def create(request: SettingAutoRegisterDTO, ):
    return await setting_auto_register_service.create(request)
@router.get("/get-sn")
def get_sn( ):
    return  setting_auto_register_service.get_sn()
@router.get("/get-setting-auto-register")
async def get_setting_auto_register():
    return await setting_auto_register_service.get_auto_register()



