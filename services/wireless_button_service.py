from fastapi import HTTPException
from tortoise.expressions import Q

from app.dto.wireless_button_dto import WirelessCreateDTO, WirelessUpdateDTO
from app.models.wireless_button import WirelessButton


class WirelessButtonService:

    async def create(self, data: WirelessCreateDTO):
        wireless_button = await WirelessButton.filter(sn=data.sn).first()
        if wireless_button:
            raise HTTPException(status_code=400, detail="Số serial đã tồn tại")

        wireless_button_name_exists = await WirelessButton.filter(name=data.name).first()
        if wireless_button_name_exists:
            raise HTTPException(status_code=400, detail="Tên nút bấm đã tồn tại")

        return await WirelessButton.create(**data.dict())

    async def update(self, data: WirelessUpdateDTO):
        try:
            wireless_button = await WirelessButton.get(id=data.id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="ID không đúng định dạng")

        if not wireless_button:
            raise HTTPException(status_code=404, detail="Không tìm thấy nút bấm")

        # check serial
        if data.sn:
            wireless_button_sn_exists = await WirelessButton.filter(sn=data.sn).first()
            if wireless_button_sn_exists and wireless_button_sn_exists.id != wireless_button.id:
                raise HTTPException(status_code=400, detail="Số serial đã tồn tại")

        # check name
        if data.name:
            wireless_button_name_exists = await WirelessButton.filter(name=data.name).first()
            if wireless_button_name_exists and wireless_button_name_exists.id != wireless_button.id:
                raise HTTPException(status_code=400, detail="Tên nút bấm đã tồn tại")

        update_data = data.dict(exclude_unset=True, exclude={})

        for field, value in update_data.items():
            setattr(wireless_button, field, value)

        await wireless_button.save()
        return wireless_button

    async def get_all(self, page: int, size: int, key_work=None, is_full=False):
        if not is_full:
            query = Q()
            if key_work:
                query = Q(name__icontains=key_work) | Q(sn__icontains=key_work)

            data = await WirelessButton.filter(query).offset(page * size).limit(size).order_by("-created_at")
            total = await WirelessButton.filter(query).count()

            return {
                "data": data,
                "total": total
            }
        else:
            data = await WirelessButton.all()
            total = await WirelessButton.all().count()
            return {
                "data": data,
                "total": total
            }

    async def get_by_id(self, id: str):
        try:
            return await WirelessButton.get(id=id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Không tìm thấy nút bấm")

    async def delete(self, id: str):
        try:
            wireless_button = await WirelessButton.get(id=id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Không tìm thấy nút bấm")

        if not wireless_button:
            raise HTTPException(status_code=404, detail="Không tìm thấy nút bấm")

        await wireless_button.delete()
        return wireless_button


wireless_button_service = WirelessButtonService()
