from fastapi import Query, HTTPException
from tortoise.exceptions import DoesNotExist
from unidecode import unidecode
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from typing_extensions import Optional

from app.dto.history_battery_percentage_dto import HistoryBatteryPercentageGetAllDTO, HistoryBatteryPercentageCreateDTO, HistoryBatteryPercentageGetCountDTO
from app.models.history__battery_percentage import HistoryBatteryPercentage
from app.models.wireless_button import WirelessButton


class HistoryBatteryPercentageService:
    async def create(self, data: HistoryBatteryPercentageCreateDTO):
        try:
            button = await WirelessButton.get(id=data.wireless_button_id)
        except DoesNotExist:
            raise HTTPException(status_code=400, detail="WirelessButton không tồn tại")
        history_battery_percentage = await HistoryBatteryPercentage.create(
            wireless_button_id=button,
            v=data.v,
            percent=data.percent
        )
        return history_battery_percentage

    async def get_all(self, data: HistoryBatteryPercentageGetAllDTO):
        if data.sort_by not in ["time", "percent"]:
            raise HTTPException(status_code=400, detail="sort_by chỉ chấp nhận 'time' hoặc 'percent'.")
        if data.sort_order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="sort_order chỉ chấp nhận 'asc' hoặc 'desc'.")

        order_by_field = "created_at" if data.sort_by == "time" else "percent"
        order_by_field = order_by_field if data.sort_order == "asc" else f"-{order_by_field}"
        query: QuerySet = HistoryBatteryPercentage.all().prefetch_related("wireless_button_id")
        if data.key_word:
            key_word = unidecode(data.key_word).lower()
            query = query.filter(
                Q(wireless_button_id_id__icontains=key_word)|
                Q(wireless_button_id__name__icontains=key_word) |
                Q(wireless_button_id__sn__icontains=key_word)
            )
        if data.filter_check:
            query = query.filter(wireless_button_id_id__in=data.filter_check)
        if data.is_full:
            history_battery = await query.order_by(order_by_field)
        else:
            history_battery = await query.order_by(order_by_field).offset(data.page * data.size).limit(data.size)
        result = []
        for item in history_battery:
            result.append({
                "id": item.id,
                "wireless_button_id": item.wireless_button_id_id,
                'WirelessButton': {
                    'name': item.wireless_button_id.name if item.wireless_button_id else None,
                    'sn': item.wireless_button_id.sn if item.wireless_button_id else None,
                    "v": item.v
                },
                "percent": item.percent,
                "created_at": item.created_at
            })
        return result

    async def get_by_wireless_button_id(
            self,
            key_word: Optional[str] = None,
            page: int = Query(0, ge=0),
            size: int = Query(10, gt=0),
            is_full: bool = False,
            sort_by: Optional[str] = "time",
            sort_order: Optional[str] = "desc"
    ):
        if sort_by not in ["time", "percent"]:
            raise HTTPException(status_code=400, detail="sort_by chỉ chấp nhận 'time' hoặc 'percent'.")
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="sort_order chỉ chấp nhận 'asc' hoặc 'desc'.")
        order_by_field = "created_at" if sort_by == "time" else "percent"
        order_by_field = order_by_field if sort_order == "asc" else f"-{order_by_field}"
        query: QuerySet = HistoryBatteryPercentage.all().prefetch_related("wireless_button_id")
        if key_word:
            key_word = unidecode(key_word).lower()
            query = query.filter(
                Q(wireless_button_id_id__icontains=key_word)|
                Q(wireless_button_id__name__icontains=key_word) |
                Q(wireless_button_id__sn__icontains=key_word)
            )
        if is_full:
            history_battery = await query.order_by(order_by_field)
        else:
            history_battery = await query.order_by(order_by_field).offset(page * size).limit(size)
        result = []
        for item in history_battery:
            result.append({
                "id": item.id,
                "wireless_button_id": item.wireless_button_id_id,
                'WirelessButton': {
                    'name': item.wireless_button_id.name if item.wireless_button_id else None,
                    'sn': item.wireless_button_id.sn if item.wireless_button_id else None,
                    "v": item.v
                },
                "percent": item.percent,
                "created_at": item.created_at
            })
        return result

    async def get_count_by_wireless_button_id(self, data: HistoryBatteryPercentageGetCountDTO):
        query: QuerySet = HistoryBatteryPercentage.all().prefetch_related("wireless_button_id")
        if data.filter_check:
            query = query.filter(wireless_button_id_id__in=data.filter_check)
        if data.key_word:
            key_word = unidecode(data.key_word).lower()
            query = query.filter(
                Q(wireless_button_id_id__icontains=key_word)|
                Q(wireless_button_id__name__icontains=key_word)|
                Q(wireless_button_id__sn__icontains=key_word)
            )
        return await query.count()
history_battery_percentage_service = HistoryBatteryPercentageService()