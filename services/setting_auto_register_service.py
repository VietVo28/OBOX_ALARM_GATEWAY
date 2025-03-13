import httpcore
from fastapi import HTTPException

from app.core.setting_env import settings
from app.dto.setting_auto_registe_dto import SettingAutoRegisterDTO
from app.models.camera import Camera
from app.models.setting_auto_register import SettingAutoRegister
import httpx

from app.models.wireless_button import WirelessButton
from app.utils.common import get_ip_wan, get_imei
from app.utils.manager_public_camera import manager_public_camera
from app.utils.rtsp import get_rtsp_not_encode


class SettingAutoRegisterService:

    def __init__(self):
        self.hardwareId = get_imei()

    async def get_auto_register(self):
        data = await  SettingAutoRegister.get_or_none()
        if not data:
            return  SettingAutoRegister(id_vms="", url_cloud_auto_register=settings.URL_CLOUD_AUTO_REGISTER,
                                         ip_media_mtx="", port_media_mtx=80, relay_address="", relay_port=80, is_enable=False)

        return data
    def get_sn(self):
        return self.hardwareId

    async def create(self, data: SettingAutoRegisterDTO):

        update_save = data.dict(exclude_unset=True, exclude={})

        if data.is_enable:
            ip_wan = await get_ip_wan()
            if not ip_wan:
                raise HTTPException(status_code=400, detail="Không thể lấy được IP WAN")

            list_camera = []
            list_button = []

            cameras = await Camera.all()
            for camera in cameras:
                list_camera.append({
                    "name": camera.name,
                    "ip_address": camera.ip,
                    "port": camera.port,
                    "username": camera.username,
                    "password": camera.password,
                    "rtsp": {
                        "1": get_rtsp_not_encode(camera.rtsp, camera.username, camera.password)
                    },
                    "physicalId": camera.sn
                })
            buttons = await WirelessButton.all()
            for button in buttons:
                list_button.append({
                    "name": button.name,
                    "physicalId": button.sn
                })

            data_send = {
                "address": ip_wan,
                "hardwareId": self.hardwareId,
                "productCode": "Obox_Alarm",
                "parentId": data.id_vms,
                "cameras": list_camera,
                "devices": list_button
            }
            # print(data_send)
            url = f"{data.url_cloud_auto_register}/api/v1/server"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=data_send)
                    response = response.json()
                    if response.get("errorId") == "ok":
                        response = response.get("reply")[0]
                        # them vao data
                        update_save["ip_media_mtx"] = response.get("MediaAddress")
                        update_save["port_media_mtx"] = response.get("MediaPort")
                        update_save["relay_address"] = response.get("RelayAddress")
                        update_save["relay_port"] = response.get("RelayPort")

                        list_camera_response = response.get("cameras")
                        for camera in list_camera_response:
                            camera_obj = await Camera.get_or_none(sn=camera.get("physicalId"))
                            if camera_obj:
                                camera_obj.id_camera_product = camera.get("id")
                                await camera_obj.save()

                    elif response.get("errorId") == "conflict":
                        print("conflict")
                    elif response.get("errorString"):
                        raise HTTPException(status_code=400, detail=response.get("errorString"))
                    else:
                        raise HTTPException(status_code=400, detail="Không thể kết nối tới server")

            except Exception as e:
                print("123123", e)
                raise HTTPException(status_code=400, detail= str(e))

        else:
            url_delete = f"{data.url_cloud_auto_register}/api/v1/server?hardwareId={self.hardwareId}"
            try:
                async with httpx.AsyncClient() as client:
                    await client.delete(url_delete)
            except Exception as e:
                print("123123", e)

        extis_key = await SettingAutoRegister.get_or_none()

        if extis_key:
            for field, value in update_save.items():
                setattr(extis_key, field, value)
            await extis_key.save()
            return extis_key

        return await SettingAutoRegister.create(**update_save)

    async def get_data_from_cloud(self, url):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response = response.json()
                if response.get("errorId") == "ok":
                    response = response.get("reply")[0]
                # print(response)
                return response
        except Exception as e:
            return None

    async def add_camera_to_cloud(self, url, camera, serverId):
        try:
            data = {
                "serverId": serverId,
                "cameras": [
                    {
                        "name": camera.name,
                        "ip_address": camera.ip,
                        "port": camera.port,
                        "username": camera.username,
                        "password": camera.password,
                        "rtsp": {
                            "1": get_rtsp_not_encode(camera.rtsp, camera.username, camera.password),
                            "2": ""
                        },
                        "physicalId": camera.sn
                    }
                ]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                return response

        except httpx.ConnectError as e:
            return None

    async def update_camera_to_cloud(self, url, camera):
        try:
            data = {
                "name": camera.name,
                "ip_address": camera.ip,
                "port": camera.port,
                "username": camera.username,
                "password": camera.password,
                "rtsp": {
                    "1": get_rtsp_not_encode(camera.rtsp, camera.username, camera.password),
                    "2": ""
                }
            }
            print(data)

            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=data)
                print(response.json())
                return response

        except httpx.ConnectError as e:
            return None

    async def delete_to_cloud(self, url):
        try:

            async with httpx.AsyncClient() as client:
                response = await client.delete(url)
                return response

        except httpx.ConnectError as e:
            return None

    async def add_device_to_cloud(self, url, device, serverId):
        try:
            data = {
                "serverId": serverId,
                "devices": [
                    {
                        "name": device.name,
                        "physicalId": device.sn
                    }
                ]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                return response

        except httpx.ConnectError as e:
            return None

    async def update_device_to_cloud(self, url, device):
        try:
            data = {"name": device.name}
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=data)
                return response

        except httpx.ConnectError as e:
            return None

    async def sync_data_to_cloud(self, list_camera, list_button):
        try:

            auto_register_service = await setting_auto_register_service.get_auto_register()

            if not auto_register_service.is_enable:
                manager_public_camera.delete_all_camera()

            url = auto_register_service.url_cloud_auto_register


            data_cloud = await self.get_data_from_cloud(url=url + f"/api/v1/server?hardwareId={self.hardwareId}")
            if not data_cloud:
                return

            cameras = data_cloud.get("cameras")
            list_camera_ffmpeg = list(manager_public_camera.list_camera.keys())
            devices = data_cloud.get("devices")
            serverId = data_cloud.get("serverId")

            address = await get_ip_wan()
            if address != data_cloud.get("address"):
                print("update address vao cloud")

            if cameras is not None:
                for camera in list_camera:
                    check = False
                    for camera_cloud in cameras:
                        if camera.sn == camera_cloud.get("physicalId"):
                            check = True
                            cameras.remove(camera_cloud)
                            if (camera.name != camera_cloud.get("name")
                                    or camera.ip != camera_cloud.get("ip_address")
                                    or camera.port != camera_cloud.get("port")
                                    or camera.username != camera_cloud.get("username")
                                    or camera.password != camera_cloud.get("password")):
                                print("vào update camera")
                                await self.update_camera_to_cloud(
                                    url + f"/api/v1/camera/update/{camera_cloud.get('id')}", camera)

                            # cap nhat lai id product
                            if camera.id_camera_product is None or camera.id_camera_product != camera_cloud.get("id"):
                                camera.id_camera_product = camera_cloud.get("id")
                                await camera.save()
                            break

                    if check is False:
                        await self.add_camera_to_cloud(url + "/api/v1/cameras", camera, serverId)

                    if auto_register_service.is_enable and camera.id_camera_product is not None:
                        # neu id_camera_product thay doi ham nay co the update lai
                        # neu ko co thay doi ve id_camera_product va camera.id da ton tai thi ko lam gi ca
                        manager_public_camera.add_camera(camera.id, f"rtsp://localhost:8554/{str(camera.id)}",
                                                         auto_register_service.ip_media_mtx,
                                                         auto_register_service.port_media_mtx,
                                                         camera.id_camera_product + "_0")
                        if str(camera.id) in list_camera_ffmpeg:
                            list_camera_ffmpeg.remove(str(camera.id))

            for camera in cameras:
                await self.delete_to_cloud(url + f"/api/v1/camera/delete/{camera.get('id')}")

            for camera_ffmpeg in list_camera_ffmpeg:
                manager_public_camera.delete_camera(camera_ffmpeg)

            if devices is not None:
                for device in list_button:
                    check = False
                    for device_cloud in devices:
                        if device.sn == device_cloud.get("physicalId"):
                            check = True
                            devices.remove(device_cloud)
                            if device.name != device_cloud.get("name"):
                                await self.update_device_to_cloud(
                                    url + f"/api/v1/device/update/{device_cloud.get('id')}", device)
                            break

                    if check is False:
                        print("them moi device vao cloud")
                        await self.add_device_to_cloud(url + "/api/v1/devices", device, serverId)

            for device in devices:
                print("xoa device tren cloud")
                await self.delete_to_cloud(url + f"/api/v1/device/delete/{device.get('id')}")

        except Exception as e:
            print(f"Error sync_data_to_cloud: {e}")


setting_auto_register_service = SettingAutoRegisterService()
