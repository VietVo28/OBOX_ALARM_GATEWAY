import json
import os
import socket
import subprocess
import time

import httpx
from zeroconf import ServiceInfo, Zeroconf

from app.core.setting_env import settings
import netifaces


def get_all_ipv4():
    ip_list = []
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
        for addr in addresses:
            if addr['addr'] != '127.0.0.1':
                ip_list.append(addr['addr'])
    return ip_list


# list_ip = get_all_ipv4()
# #convert list to string
# str_ip = ', '.join([str(elem) for elem in list_ip])
# print(f"List of IP: {str_ip}")

def get_local_ipv4():
    try:
        # Kết nối tới một máy chủ bên ngoài (Google DNS)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipv4 = s.getsockname()[0]
        s.close()
        return ipv4
    except Exception as e:
        if len(get_all_ipv4()) > 0:
            return get_all_ipv4()[0]
        return "localhost"


def get_local_ipv4_check_internet():
    try:
        # Kết nối tới một máy chủ bên ngoài (Google DNS)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipv4 = s.getsockname()[0]
        s.close()
        return ipv4, True
    except Exception as e:
        if len(get_all_ipv4()) > 0:
            return get_all_ipv4()[0], False
        return "localhost", False


def public_server_ip():
    ip_v4 = ""
    zeroconf = None
    check_host = None
    while True:
        try:
            ip, is_internet = get_local_ipv4_check_internet()
            if is_internet is False and (check_host is False or check_host is None):
                print(f"🌐 Đã phát sóng WiFi")
                check_host = True
                host_wifi()

            if is_internet and (check_host or check_host is None):
                print(f"🌐 Đã ngắt phát sóng WiFi")
                check_host = False
                stop_wifi()

            if ip != ip_v4:
                if zeroconf is not None:
                    try:
                        zeroconf.unregister_all_services()
                        zeroconf.close()
                    except:
                        pass
                print(f"🌐 Đã đăng ký IP {ip} tới mạng Zeroconf")

                zeroconf = Zeroconf()
                imei = get_imei()
                list_ip = get_all_ipv4()
                str_ip = ', '.join([str(elem) for elem in list_ip])
                ip_v4 = ip

                info = ServiceInfo(
                    "_http._tcp.local.",
                    f"box_alarm_{imei}._http._tcp.local.",
                    addresses=[ip_v4],
                    port=settings.PORT,
                    properties={"imei": imei, "ip": ip_v4, "list_ip": str_ip},
                )

                zeroconf.register_service(info)
                update_env_file()

        except Exception as e:
            print(f"❌ Lỗi khi đăng ký IP: {e}")
        time.sleep(10)


def update_env_file():
    ip = get_local_ipv4()
    # get path of file
    file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(file_path)
    # ra 2 folder
    current_directory = os.path.dirname(current_directory)
    current_directory = os.path.dirname(current_directory)
    path = os.path.join(current_directory, "templates")
    path = os.path.join(path, "__ENV.js")

    # read file replace localhost to 192.168.103.91
    filedata = 'window.__ENV = {"NEXT_PUBLIC_ACCESS_TOKEN_NAME":"c41bc368-f11d-47ab-99dd-ffd8367426b3","NEXT_PUBLIC_APP_URL":"http://localhost:3025","NEXT_PUBLIC_BACKEND_DOMAIN":"http://localhost:8004","NEXT_PUBLIC_REFESH_TOKEN_NAME":"e1b33c4e-c065-4f17-8a83-7a53e1f03dfb","NEXT_PUBLIC_SOCKET_DOMAIN":"ws://localhost:8004/ws/","NEXT_PUBLIC_VIDEO_DOMAIN":"http://localhost:9996","NEXT_PUBLIC_WEBRTC_DOMAIN":"http://localhost:8889"};'

    arr_data = filedata.split("=")
    data = json.loads(arr_data[1].replace(";", ""))
    data["NEXT_PUBLIC_APP_URL"] = f'http://{ip}:3025'
    data["NEXT_PUBLIC_BACKEND_DOMAIN"] = f'http://{ip}:8004'
    data["NEXT_PUBLIC_SOCKET_DOMAIN"] = f'ws://{ip}:8004/ws/'
    data["NEXT_PUBLIC_VIDEO_DOMAIN"] = f'http://{ip}:9996'
    data["NEXT_PUBLIC_WEBRTC_DOMAIN"] = f'http://{ip}:8889'

    data_str = str(arr_data[0]) + "=" + json.dumps(data) + ";"

    # write file
    with open(path, "w") as file:
        file.write(data_str)


async def get_ip_wan():
    try:
        url = "https://api64.ipify.org?format=json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json().get("ip")
    except Exception as e:
        return None


from uuid import getnode as get_mac


def get_imei():  # get imei number of device
    # Extract serial from conf file
    if checkIsAarch64():
        cpuserial = str(get_mac()).upper()
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = str(line[10:26]).upper()
            f.close()
        except:
            # cpuserial = "ERROR000000000"
            cpuserial = str(''.join(['D', str(get_mac()).upper()]))
        return cpuserial
    else:
        return str(get_mac()).upper()


def checkIsAarch64():
    import platform
    if platform.machine().lower() == "aarch64":
        return True
    return False


# nmcli device wifi hotspot ifname wlan0 ssid MyHotspot password 12345678


def host_wifi():
    try:
        ssid = "OBOX ALARM " + get_imei()  # Đảm bảo get_imei() trả về giá trị hợp lệ
        password = "12345678"

        result = subprocess.run(
            ["sudo", "nmcli", "device", "wifi", "hotspot", "ifname", "wlan0", "ssid", ssid, "password", password],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Hotspot WiFi đã được tạo thành công!")
            return True
        else:
            print(f"⚠️ Lỗi khi tạo Hotspot: {result.stderr}")
            return False

    except Exception as e:
        print(f"⚠️ Lỗi khi kết nối WiFi: {e}")
        return False


def stop_wifi():
    try:
        # Tắt hotspot bằng cách vô hiệu hóa kết nối WiFi
        result = subprocess.run(
            ["sudo", "nmcli", "device", "disconnect", "wlan0"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Hotspot WiFi đã được tắt!")
            return True
        else:
            print(f"⚠️ Lỗi khi tắt Hotspot: {result.stderr}")
            return False

    except Exception as e:
        print(f"⚠️ Lỗi khi ngắt WiFi: {e}")
        return False
# print(get_imei())
