import asyncio
import time
from datetime import timedelta, datetime

import httpx
from tortoise.timezone import now

from app.dto.camera_dto import CameraUpdateDTO
from app.models.camera import Camera
from app.models.wireless_button import WirelessButton
from app.services.camera_service import camera_service
from app.services.mediamtx_service import media_mtx_service
from app.services.setting_auto_register_service import setting_auto_register_service
from app.utils.common import get_imei
from app.utils.mqtt import mqtt_client


class SyncDataToCloud:

    # def start(self):
    #     asyncio.run(self.sync_data())

    async def sync_data(self):

        # bien de chi can update 1 lan khi mat ket noi voi mtx
        check_update = True
        self.hardwareId = get_imei()
        while True:
            try:

                list_camera = await Camera.all()
                list_button = await WirelessButton.all()

                await setting_auto_register_service.sync_data_to_cloud(list_camera=list_camera, list_button=list_button)

                await self.send_data_to_mqtt(list_camera=list_camera, list_button=list_button)

                await camera_service.init_camera(list_camera=list_camera)

                # cap nhat trang thai cho camera
                await self.sync_camera_to_mtx()
                check_update = True

            except Exception as e:
                # print(f"Error sync_data: {e}")
                # neu mat ket noi voi mtx thi cap nhat trang thai tat ca camera la false
                if check_update:
                    check_update = False
                    await camera_service.update_status_all(status=False)
            await asyncio.sleep(5)

    async def send_data_to_mqtt(self, list_camera, list_button):
        try:
            data = {"sn": self.hardwareId, "listCamera": [], "listWirelessButton": [], "timeStamp": time.time()}

            for camera in list_camera:
                data["listCamera"].append({
                    "sn": camera.sn,
                    "status": "ONLINE" if camera.status else "OFFLINE",
                })

            for button in list_button:
                status = "ONLINE"
                if now() - button.updated_at > timedelta(minutes=70):
                    status = "OFFLINE"
                    if button.status is True:
                        # update status button
                        await WirelessButton.filter(sn=button.sn).update(status=False)
                data["listWirelessButton"].append({
                    "sn": button.sn,
                    "v": button.v,
                    "percent": button.percent,
                    "status": status,
                })

            await mqtt_client.send_mess("device/status", data)
        except Exception as e:
            print(f"Error send_data_to_mqtt: {e}")


    async def sync_camera_to_mtx(self):
        path_cameras = await media_mtx_service.get_all_status_path()
        for item in path_cameras.get("items"):
            try:
                name = item.get("name")
                ready = item.get("ready")
                await camera_service.update(CameraUpdateDTO(id=name, status=ready))
            except Exception as e:
                print(f"Error sync_camera_to_mtx: {e}")


sync_data_to_cloud = SyncDataToCloud()
