from typing import Optional

from pydantic import BaseModel

class history_alarm_create_DTO(BaseModel):
    wireless_button_id: str
class HistoryAlarmGetAllDTO(BaseModel):
    page: int = 0
    size: int = 10
    is_full: bool = False
    key_word: str = None
    filter_check:  Optional[list[str]] = None
    sort_order: Optional[str] = "desc"
class HistoryAlarmGetCountDTO(BaseModel):
    key_word: Optional[str] = None
    filter_check: Optional[list[str]] = None