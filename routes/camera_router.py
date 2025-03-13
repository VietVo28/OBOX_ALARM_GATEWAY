from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.dto.camera_dto import GetRTSPCameraDTO, CameraCreateDTO, CameraUpdateDTO
from app.models.user import User
from app.services.camera_service import camera_service
from app.utils.rtsp import get_retsp_onvif

router = APIRouter()
prefix = "/camera"
tags = ["camera"]

current_user = Annotated[User, Depends(get_current_user)]


@router.post("/create")
async def create(request: CameraCreateDTO, user: current_user):
    return await camera_service.create(request)


@router.put("/update")
async def update_camera(request: CameraUpdateDTO, user: current_user):
    return await camera_service.update(request)


@router.get("/get-all")
async def get_all(user: current_user, page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                  key_work: Optional[str] = Query(None), ):
    return await camera_service.get_all(page, size, key_work)


@router.post("/get-rtsp")
def get_rtsp(request: GetRTSPCameraDTO, user: current_user):
    return get_retsp_onvif(request)


@router.get("/get-time-line")
async def get_time_line(id_camera: str, user: current_user):
    return await camera_service.get_time_line(id_camera)


@router.get("/get-by-id")
async def get_by_id(id: str, user: current_user):
    return await camera_service.get_by_id(id)


@router.delete("/delete")
async def delete(id: str, user: current_user):
    return await camera_service.delete(id)
