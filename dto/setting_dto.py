from typing import Optional

from pydantic import BaseModel


class SettingCreateDTO(BaseModel):
    key: str
    value: str


class TestDTO(BaseModel):
    sn : str
