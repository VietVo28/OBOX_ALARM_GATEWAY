import asyncio
import json
import os
import shutil
from pathlib import Path
import aiofiles

import httpx
from app.core.setting_env import settings
from app.utils.path_currrent_souce import current_source_path


class MediaMTXService:
    list_info_camera = {}
    url = f"{settings.PROTOCOL_MEDIA_MTX}://{settings.HOST_MEDIA}:{settings.PORT_API_MEDIA_MTX}"

    async def add_rtsp(self, id_camera, rtsp, is_record=False, url_store=None, record_delete_after="24h"):
        current_source = current_source_path.get()

        # file_excute = current_source + "/app/utils/write_segmen_mediamtx.py"

        # file_save = current_source + "/data/" + id_camera + ".json"
        # type_save = "default"
        url_store = current_source + "/data/recordings/%path/%Y-%m-%d_%H-%M-%S-%f"

        # if url_store is None:
        #     url_store = "./recordings/%path/%Y-%m-%d_%H-%M-%S-%f"
        # else:
        #     type_save = "custom"
        #     url_store = url_store + "/%path/%Y-%m-%d_%H-%M-%S-%f"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.url}/v3/config/paths/get/{id_camera}")

            if response.status_code == 200:
                rtsp_old = response.json().get("source")
                if rtsp_old != rtsp:
                    return await self.edit_rtsp(id_camera, rtsp)
            else:
                data = {
                    "name": id_camera,
                    "source": rtsp,
                    "sourceFingerprint": "",
                    "sourceOnDemand": False,
                    "sourceOnDemandStartTimeout": "10s",
                    "sourceOnDemandCloseAfter": "10s",
                    "maxReaders": 0,
                    "srtReadPassphrase": "",
                    "fallback": "",
                    "record": is_record,
                    "playback": True,
                    "recordPath": url_store,
                    "recordFormat": "fmp4",
                    "recordPartDuration": "100ms",
                    "recordSegmentDuration": "5m",
                    "recordDeleteAfter": record_delete_after,
                    "overridePublisher": True,
                    "srtPublishPassphrase": "",
                    "rtspTransport": "tcp",
                    "rtspAnyPort": False,
                    "rtspRangeType": "",
                    "rtspRangeStart": "",
                    "sourceRedirect": "",
                    "rpiCameraCamID": 0,
                    "rpiCameraWidth": 1920,
                    "rpiCameraHeight": 1080,
                    "rpiCameraHFlip": False,
                    "rpiCameraVFlip": False,
                    "rpiCameraBrightness": 0,
                    "rpiCameraContrast": 1,
                    "rpiCameraSaturation": 1,
                    "rpiCameraSharpness": 1,
                    "rpiCameraExposure": "normal",
                    "rpiCameraAWB": "auto",
                    "rpiCameraAWBGains": [
                        0,
                        0
                    ],
                    "rpiCameraDenoise": "off",
                    "rpiCameraShutter": 0,
                    "rpiCameraMetering": "centre",
                    "rpiCameraGain": 0,
                    "rpiCameraEV": 0,
                    "rpiCameraROI": "",
                    "rpiCameraHDR": False,
                    "rpiCameraTuningFile": "",
                    "rpiCameraMode": "",
                    "rpiCameraFPS": 30,
                    "rpiCameraIDRPeriod": 60,
                    "rpiCameraBitrate": 1000000,
                    "rpiCameraProfile": "main",
                    "rpiCameraLevel": "4.1",
                    "rpiCameraAfMode": "continuous",
                    "rpiCameraAfRange": "normal",
                    "rpiCameraAfSpeed": "normal",
                    "rpiCameraLensPosition": 0,
                    "rpiCameraAfWindow": "",
                    "rpiCameraTextOverlayEnable": False,
                    "rpiCameraTextOverlay": "%Y-%m-%d %H:%M:%S - MediaMTX",
                    "runOnInit": "",
                    "runOnInitRestart": False,
                    "runOnDemand": "",
                    "runOnDemandRestart": False,
                    "runOnDemandStartTimeout": "10s",
                    "runOnDemandCloseAfter": "10s",
                    "runOnUnDemand": "",
                    # ffmpeg -i "rtsp://admin:Oryza123@192.168.103.210:554/cam/realmonitor?channel=1&subtype=0" -c copy -f rtsp rtsp://localhost:8554/another-path
                    "runOnNotReady": "",
                    "runOnReadyRestart": True,
                    "runOnReady": "",
                    "runOnRead": "",
                    "runOnReadRestart": False,
                    "runOnUnread": "",
                    # "runOnRecordSegmentCreate": f"python {file_excute} $MTX_PATH $MTX_SEGMENT_PATH -1 create {file_save} {type_save}",
                    # "runOnRecordSegmentComplete": f"python {file_excute} $MTX_PATH $MTX_SEGMENT_PATH $MTX_SEGMENT_DURATION update {file_save} {type_save}",
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{self.url}/v3/config/paths/add/{id_camera}", json=data)
                    return response
        except Exception as e:
            print(f"Lỗi xảy ra add rtsp: {e}")
            return None

    async def edit_rtsp(self, id_camera, rtsp):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(f"{self.url}/v3/config/paths/patch/{id_camera}", json={
                    "source": rtsp,
                })
                return response
        except Exception as e:
            print(f"Lỗi xảy ra edit rtsp: {e}")
            return None

    async def delete_file_async(self, path):
            try:
                path_remove = Path(path)
                if path_remove.exists():
                    # Xóa thư mục và nội dung bên trong
                    await asyncio.to_thread(shutil.rmtree, str(path_remove))
            except Exception as e:
                print(f"Error 11: {e}")

    async def delete_rtsp(self, id_camera):
        info_camera = await self.get_info_camera(id_camera)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{self.url}/v3/config/paths/delete/{id_camera}")
        except Exception as e:
            pass


        await asyncio.sleep(1)

        record_path = info_camera.get("recordPath").replace("/%path/%Y-%m-%d_%H-%M-%S-%f", "")
        record_path = os.path.join(record_path, str(id_camera))

        await self.delete_file_async(record_path)

        # remove info camera
        if id_camera in self.list_info_camera:
            del self.list_info_camera[id_camera]

    async def get_all(self):
        list_result = []
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/v3/config/paths/list")
            if response.status_code == 200:
                for item in response.json().get("items"):
                    if item.get("name") != "all_others":
                        list_result.append(item.get("name"))

        return list_result

    async def get_all_status_path(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/v3/paths/list")
            return response.json()

    async def get_info_camera(self, id_camera):
        id_camera = str(id_camera)
        if id_camera in self.list_info_camera:
            return self.list_info_camera[id_camera]
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.url}/v3/config/paths/get/{id_camera}")
                if response.status_code == 200:
                    self.list_info_camera[id_camera] = response.json()
                    return response.json()
            return None
        except Exception as e:
            print(f"Lỗi xảy ra get_info_camera: {e}")
            return None


media_mtx_service = MediaMTXService()
