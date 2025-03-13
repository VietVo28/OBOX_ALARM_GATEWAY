from typing import Optional

from pydantic import BaseModel

class HistoryBatteryPercentageCreateDTO(BaseModel):
    wireless_button_id: str
    v: float
    percent: float
class HistoryBatteryPercentageGetAllDTO(BaseModel):
    page: int = 0
    size: int = 10
    is_full: bool = False
    key_word: str = None
    filter_check:  Optional[list[str]] = None
    sort_by: Optional[str] = "time"
    sort_order: Optional[str] = "desc"
class HistoryBatteryPercentageGetCountDTO(BaseModel):
    key_word: Optional[str] = None
    filter_check: Optional[list[str]] = None