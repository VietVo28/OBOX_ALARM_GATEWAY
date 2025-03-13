import socket
from time import sleep

from app.core.setting_env import settings
from app.services.camera_service import camera_service
import asyncio


class ConnectMediaMTX:
    is_connected = False

    def start(self):
        asyncio.run(self.connect())

    async def connect(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (settings.HOST_MEDIA, settings.PORT_RTSP_MEDIA_MTX)
                s.connect(server_address)
                self.set_is_connected(True)

                await  camera_service.init_camera()
                print("Connected to MediaMTX")

                while True:
                    data = s.recv(1024)
                    print('received {!r}'.format(data))
                    if not data:
                        print('closing socket')

                        break
            except Exception as e:
                # print("Error: connect to MediaMTX", e)
                self.set_is_connected(False)
                sleep(5)

    def set_is_connected(self, value):
        self.is_connected = value

    def get_is_connected(self):
        return self.is_connected


connect_media_mtx = ConnectMediaMTX()
