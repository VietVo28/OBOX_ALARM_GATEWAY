import subprocess
import time
import threading


class RTSPProcess:
    def __init__(self):
        self.is_running = True
        self.time_current = time.time()
        self.process = None

    def start_rtsp_process(self, rtsp_url, output_url):
        command = [
            "ffmpeg", "-rtsp_transport", "tcp", "-i", rtsp_url,
            "-c:v", "copy", "-f", "rtsp", output_url
        ]

        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def check_process(self):
        while self.is_running:
            if time.time() - self.time_current > 10:
                print("RTSP connection error detected. Restarting FFmpeg...")
                if self.process is not None:
                    self.process.kill()
                    self.process = None
                    self.time_current = time.time()

            time.sleep(1)

    def stop(self):
        self.is_running = False
        print("Stopping RTSP process...")
        if self.process is not None:
            self.process.kill()

    def monitor_process(self, rtsp_url, output_url):

        threading.Thread(target=self.check_process, daemon=True).start()

        while self.is_running:
            print(self.process,output_url)
            if self.process is None or self.process.poll() is not None:
                print("FFmpeg process exited, restarting...")
                self.process = self.start_rtsp_process(rtsp_url, output_url)

            if self.process.stderr:
                for line in iter(self.process.stderr.readline, ''):
                    if "size=N/A" in line.strip():
                        self.time_current = time.time()
                        # print("RTSP connection is OK")

            time.sleep(5)  # Kiểm tra trạng thái sau mỗi 5 giây


class ManagerPublicCamera:
    def __init__(self):
        self.list_camera = {}
        self.list_output_url = {}

    def get_list_camera(self):
        return self.list_camera

    def add_camera(self, id_camera, rtsp_url, ip_media_mtx, port_media_mtx,id_camera_product):
        id_camera = str(id_camera)

        output_url = f"rtsp://{ip_media_mtx}:{port_media_mtx}/{id_camera_product}"
        if id_camera in self.list_output_url and self.list_output_url[id_camera] != output_url:
            self.delete_camera(id_camera)

        if id_camera in self.list_camera:
            return

        rtsp_process = RTSPProcess()
        threading.Thread(target=rtsp_process.monitor_process, args=(rtsp_url, output_url), daemon=True).start()
        self.list_camera[id_camera] = rtsp_process
        self.list_output_url[id_camera] = output_url

    def delete_camera(self, id_camera):
        id_camera = str(id_camera)
        if id_camera in self.list_camera:
            self.list_camera[id_camera].stop()
            del self.list_camera[id_camera]
            del self.list_output_url[id_camera]

    def edit_camera(self, id_camera, rtsp_url, ip_media_mtx, port_media_mtx):
        id_camera = str(id_camera)
        output_url = f"rtsp://{ip_media_mtx}:{port_media_mtx}/{id_camera}"
        self.delete_camera(id_camera)
        self.add_camera(id_camera, rtsp_url, output_url)

    def delete_all_camera(self):
        for id_camera in self.list_camera:
            self.delete_camera(id_camera)




manager_public_camera = ManagerPublicCamera()
