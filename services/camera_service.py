import asyncio
import os
import shutil

from fastapi import HTTPException
from tortoise.expressions import Q

from app.dto.camera_dto import CameraCreateDTO, CameraUpdateDTO
from app.models.camera import Camera
from app.models.timeline import Timeline
from app.services.mediamtx_service import media_mtx_service
from app.services.setting_auto_register_service import setting_auto_register_service
from app.utils.manager_public_camera import manager_public_camera
from app.utils.path_currrent_souce import current_source_path
from app.utils.read_time_line import read_time_line, get_video_duration, convert_time
from app.utils.rtsp import get_rtsp


class CameraService:

    async def create(self, data: CameraCreateDTO):
        camera_rtsp_exists = await Camera.filter(rtsp=data.rtsp).first()
        if camera_rtsp_exists:
            raise HTTPException(status_code=400, detail="RTSP đã tồn tại")

        camera_name_exists = await Camera.filter(name=data.name).first()
        if camera_name_exists:
            raise HTTPException(status_code=400, detail="Tên camera đã tồn tại")

        camera_ip_and_port_exists = await Camera.filter(ip=data.ip, port=data.port).first()
        if camera_ip_and_port_exists:
            raise HTTPException(status_code=400, detail="IP hoặc Port đã tồn tại")

        if not data.rtsp.startswith("rtsp://"):
            raise HTTPException(status_code=400, detail="RTSP không đúng định dạng")

        camera_sn_exists = await Camera.filter(sn=data.sn).first()
        if camera_sn_exists:
            raise HTTPException(status_code=400, detail="Serial number đã tồn tại")

        data = await Camera.create(**data.dict())
        if data:
            rtsp = get_rtsp(data.rtsp, data.username, data.password)
            asyncio.create_task(media_mtx_service.add_rtsp(id_camera=str(data.id), rtsp=rtsp, is_record=True))
        return data

    async def get_all(self, page: int, size: int, key_work=None):
        query = Q()
        if key_work:
            query = Q(name__icontains=key_work) | Q(sn__icontains=key_work)

        data = await Camera.filter(query).offset(page * size).limit(size).order_by("-created_at")
        total = await Camera.filter(query).count()

        return {
            "data": data,
            "total": total
        }

    async def update(self, data: CameraUpdateDTO):
        try:
            camera = await Camera.get(id=data.id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="ID không đúng định dạng")

        if not camera:
            raise HTTPException(status_code=404, detail="Không tìm thấy camera")

        update_data = data.dict(exclude_unset=True, exclude={})
        rtsp_current = camera.rtsp
        username_current = camera.username
        password_current = camera.password

        for field, value in update_data.items():
            setattr(camera, field, value)

        if not camera.rtsp.startswith("rtsp://"):
            raise HTTPException(status_code=400, detail="RTSP không đúng định dạng")

        camera_rtsp_exists = await Camera.filter(rtsp=camera.rtsp).exclude(id=camera.id).first()
        if camera_rtsp_exists:
            raise HTTPException(status_code=400, detail="RTSP đã tồn tại")

        camera_name_exists = await Camera.filter(name=camera.name).exclude(id=camera.id).first()
        if camera_name_exists:
            raise HTTPException(status_code=400, detail="Tên camera đã tồn tại")

        camera_ip_and_port_exists = await Camera.filter(ip=camera.ip, port=camera.port).exclude(id=camera.id).first()
        if camera_ip_and_port_exists:
            raise HTTPException(status_code=400, detail="IP hoặc Port đã tồn tại")

        camera_sn_exists = await Camera.filter(sn=camera.sn).exclude(id=camera.id).first()
        if camera_sn_exists:
            raise HTTPException(status_code=400, detail="Serial number đã tồn tại")

        if rtsp_current != camera.rtsp or username_current != camera.username or password_current != camera.password:
            rtsp = get_rtsp(camera.rtsp, camera.username, camera.password)
            asyncio.create_task(media_mtx_service.edit_rtsp(id_camera=str(camera.id), rtsp=rtsp))

        await camera.save()

    async def update_status_all(self, status: bool):
        await Camera.all().update(status=status)

    async def init_camera(self, list_camera=None):

        if list_camera is None:
            # lấy tất cả camera từ database
            list_camera = await Camera.all()

        # lấy tất cả camera từ media mtx
        list_camera_exists = await media_mtx_service.get_all()

        for camera in list_camera:
            # tạo rtsp từ camera nếu chưa có username và password thì sẽ tự động thêm vào
            rtsp = get_rtsp(camera.rtsp, camera.username, camera.password)

            """
                 - Thêm rtsp vào media mtx
                    + Nếu camera đã tồn tại rtsp như cũ thì không làm gì, rtsp khác thì sẽ cập nhật lại rtsp
                    + Nếu camera không tồn tại thì sẽ thêm mới rtsp
            """
            await media_mtx_service.add_rtsp(id_camera=str(camera.id), rtsp=rtsp, is_record=True)

            # xóa camera đã tồn tại trong list_camera_exists
            if str(camera.id) in list_camera_exists:
                list_camera_exists.remove(str(camera.id))

        # Nếu có camera tồn tại trong media mtx mà không có trong database thì xóa camera đó
        # Luu y: ham delete_rtsp se xoa ca file json chua timeline va file video
        for id_camera in list_camera_exists:
            await media_mtx_service.delete_rtsp(id_camera)

        list_camera_current = await Camera.all()
        for camera in list_camera_current:
            info = await media_mtx_service.get_info_camera(str(camera.id))
            if info is not None and info.get("recordPath") is not None:
                record_path = info.get("recordPath").replace("/%path/%Y-%m-%d_%H-%M-%S-%f", "")
                record_path = os.path.join(record_path, str(camera.id))
                if os.path.exists(record_path):
                    list_file = os.listdir(record_path)
                    list_file.sort()
                    try:
                        await self.save_time_line(camera, record_path, list_file)
                    except Exception as e:
                        print(f"Error save_time_line: {e}")

    async def save_time_line(self, camera, record_path, list_file):
        for i in range(len(list_file)):
            file = list_file[i]
            if file.endswith(".mp4"):
                path = os.path.join(record_path, file)
                time_line_exit = await Timeline.filter(name_file=file).first()
                if time_line_exit is None or time_line_exit.is_new:
                    duration = await asyncio.to_thread(get_video_duration, path)
                    start_time = convert_time(file)
                    is_new = False
                    if i == len(list_file) - 1:
                        is_new = True
                    if time_line_exit is None:
                        await Timeline.create(id_camera=camera, duration=duration, start_time=start_time,
                                              name_file=file, is_new=is_new)
                    else:
                        await Timeline.filter(id=time_line_exit.id).update(duration=duration, is_new=is_new)

        if self.check_disk() < 8:
            list_file = os.listdir(record_path)
            list_file.sort()
            for i in range(len(list_file)):
                file = list_file[i]
                if file.endswith(".mp4") and i < len(list_file) - 1:
                    path = os.path.join(record_path, file)
                    os.remove(path)
                    time_line = await Timeline.filter(name_file=file).first()
                    if time_line is not None:
                        await time_line.delete()
                    if self.check_disk() > 8:
                        break

    def check_disk(self):
        current_source = current_source_path.get()
        total, used, free = shutil.disk_usage(current_source)
        gb = free // (1024 ** 3)
        return gb

    async def get_time_line(self, id_camera):
        list_time_line = await Timeline.filter(id_camera=id_camera).order_by("start_time")
        return read_time_line(id_camera, list_time_line)

    async def get_by_id(self, id: str):
        try:
            return await Camera.get(id=id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Không tìm thấy camera")

    async def delete(self, id: str):
        try:
            camera = await Camera.get(id=id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="ID không đúng định dạng")

        if not camera:
            raise HTTPException(status_code=404, detail="Không tìm thấy camera")

        asyncio.create_task(media_mtx_service.delete_rtsp(id_camera=str(camera.id)))
        manager_public_camera.delete_camera(camera.id)
        await camera.delete()

        return "Xóa camera thành công"

    async def get_all_rtsp(self):
        return await Camera.all().values_list("rtsp", flat=True)


camera_service = CameraService()
