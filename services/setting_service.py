from app.dto.setting_dto import SettingCreateDTO, TestDTO
from app.models.setting import Setting
from app.websocket.ConnectionManager import connection_manager


class SettingService:

    async def create(self, data: SettingCreateDTO):
        extis_key = await Setting.filter(key=data.key).first()
        if extis_key:
            update_data = data.dict(exclude_unset=True, exclude={})
            for field, value in update_data.items():
                setattr(extis_key, field, value)

            return await extis_key.save()

        return await Setting.create(**data.dict())

    async  def get_by_key(self, key: str):
        return await Setting.filter(key=key).first()

    async def test(self,data:TestDTO):
        extis_key = await Setting.filter(key="CONNECT_MODE",value="ENABLE").first()
        if not extis_key:
            return "connect mode is disable"
        await connection_manager.send_all({"sn":data.sn,"type":"CONNECT_MODE "})


setting_service = SettingService()
