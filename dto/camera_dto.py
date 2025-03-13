from typing import Optional

from pydantic import BaseModel


class CameraCreateDTO(BaseModel):
    name: str
    sn: Optional[str] = None
    ip: str
    port: Optional[int] = 554
    username: str
    password: str
    rtsp: str


class GetRTSPCameraDTO(BaseModel):
    ip: str
    port: Optional[int] = 80
    username: str
    password: str


class CameraUpdateDTO(BaseModel):
    id: str
    name: Optional[str] = None
    sn: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rtsp: Optional[str] = None
    status: Optional[bool] = None
