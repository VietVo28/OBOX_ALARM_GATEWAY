from typing import Optional

from pydantic import BaseModel


class WirelessCreateDTO(BaseModel):
    name: str
    sn: str

class WirelessUpdateDTO(BaseModel):
    id: str
    name: Optional[str] = None
    sn: Optional[str] = None
    status: Optional[bool] = None
    v: Optional[float] = None
    percent: Optional[float] = None