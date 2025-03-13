from urllib.parse import quote

from fastapi import HTTPException

from app.dto.camera_dto import GetRTSPCameraDTO
from onvif import ONVIFCamera


def get_rtsp(rtsp, user_name, password):
    password = quote(password)
    start_rtsp = f"rtsp://{user_name}:{password}@"
    if start_rtsp in rtsp:
        return rtsp
    return rtsp.replace("rtsp://", start_rtsp)

def get_rtsp_not_encode(rtsp, user_name, password):
    start_rtsp = f"rtsp://{user_name}:{password}@"
    if start_rtsp in rtsp:
        return rtsp
    return rtsp.replace("rtsp://", start_rtsp)

def get_retsp_onvif(data: GetRTSPCameraDTO):
    try:
        camera = ONVIFCamera(data.ip, port=data.port, user=data.username, passwd=data.password)
        media_service = camera.create_media_service()
        profiles = media_service.GetProfiles()
        profile_token = profiles[0].token

        stream_setup = {
            'Stream': 'RTP-Unicast',
            'Transport': {'Protocol': 'RTSP'}
        }

        stream_uri = media_service.GetStreamUri({'StreamSetup': stream_setup, 'ProfileToken': profile_token})

        # print("RTSP URL:", stream_uri.Uri)
        print(data.ip)
        return stream_uri.Uri

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        raise HTTPException(status_code=400, detail="Không thể lấy RTSP từ camera")
        # pass

if __name__ == "__main__":
    import threading
    for i in range(1, 255):
        try:
            data = GetRTSPCameraDTO(ip=f"192.168.104.{i}", port=80, username="admin", password="Oryza@123")
            rtsp = threading.Thread(target=get_retsp_onvif, args=(data,))
            rtsp.start()
            # print(f"192.168.104.{i}")

        except Exception as e:
            # print(f"Lỗi xảy ra: {e}")
            pass
    while True:
        pass
