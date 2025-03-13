from typing import Optional

from fastapi import Query, HTTPException
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.queryset import QuerySet
from unidecode import unidecode

from app.dto.history_alarm_dto import history_alarm_create_DTO, HistoryAlarmGetAllDTO, HistoryAlarmGetCountDTO
from app.models.history_alarm import HistoryAlarm
from app.models.wireless_button import WirelessButton

class HistoryAlarmService:
    async def create(self, data: history_alarm_create_DTO):
        try:
            button = await WirelessButton.get(id=data.wireless_button_id)
        except DoesNotExist:
            raise HTTPException(status_code=400, detail="WirelessButton không tồn tại")
        history_alarm = await HistoryAlarm.create(
            wireless_button_id=button
        )
        return history_alarm

    async def get_all(self, data: HistoryAlarmGetAllDTO):
        query: QuerySet = HistoryAlarm.all().prefetch_related("wireless_button_id")
        if data.key_word:
            key_word = unidecode(data.key_word).lower()
            query = query.filter(
                Q(wireless_button_id__id__icontains=key_word)|
                Q(wireless_button_id__name__icontains=key_word) |
                Q(wireless_button_id__sn__icontains=key_word)
            )
        if data.sort_order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="sort_by chỉ chấp nhận 'asc' hoặc 'desc'.")
        order_by_field = "created_at" if data.sort_order == "asc" else "-created_at"
        if data.filter_check:
            query = query.filter(wireless_button_id__id__in=data.filter_check)
        if data.is_full:
            history_alarm = await query.order_by(order_by_field)
        else:
            history_alarm = await query.order_by(order_by_field).offset(data.page * data.size).limit(data.size)
        result = []
        for item in history_alarm:
            item_dict = {
                'id': item.id,
                'wireless_button_id': item.wireless_button_id.id if item.wireless_button_id else None,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'WirelessButton': {
                    'name': item.wireless_button_id.name if item.wireless_button_id else None,
                    'sn': item.wireless_button_id.sn if item.wireless_button_id else None
                }
            }
            result.append(item_dict)
        return result
    async def get_by_wireless_button_id(self, key_word: str,
                      page: int = Query(0, ge=0),
                      size: int = Query(10, gt=0),
                      is_full: bool = False,
                      sort_order: Optional[str] = "desc"):
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="sort_order chỉ chấp nhận 'asc' hoặc 'desc'.")
        order_by_field = "created_at" if sort_order == "asc" else "-created_at"
        query: QuerySet = HistoryAlarm.all().prefetch_related("wireless_button_id")
        if key_word:
            key_word = unidecode(key_word).lower()
            query = query.filter(
                Q(wireless_button_id_id__icontains=key_word)|
                Q(wireless_button_id__name__icontains=key_word) |
                Q(wireless_button_id__sn__icontains=key_word)
            )
        if is_full:
            history_alarm = await query.order_by(order_by_field)
        else:
            history_alarm = await query.order_by(order_by_field).offset(page * size).limit(size)
        result = []
        for item in history_alarm:
            item_dict = {
                'id': item.id,
                'wireless_button_id': item.wireless_button_id.id if item.wireless_button_id else None,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'WirelessButton': {
                    'id': item.wireless_button_id.id if item.wireless_button_id else None,
                    'name': item.wireless_button_id.name if item.wireless_button_id else None,
                    'sn': item.wireless_button_id.sn if item.wireless_button_id else None
                }
            }
            result.append(item_dict)
        return result
    async def get_count_by_wireless_button_id(self, data: HistoryAlarmGetCountDTO):
        query: QuerySet = HistoryAlarm.all().prefetch_related("wireless_button_id")
        if data.filter_check:
            query = query.filter(wireless_button_id_id__in=data.filter_check)
        if data.key_word:
            key_word = unidecode(data.key_word).lower()
            query = query.filter(
                Q(wireless_button_id_id__icontains=key_word)|
                Q(wireless_button_id__name__icontains=key_word) |
                Q(wireless_button_id__sn__icontains=key_word)
            )
        return await query.count()
history_alarm_service = HistoryAlarmService()