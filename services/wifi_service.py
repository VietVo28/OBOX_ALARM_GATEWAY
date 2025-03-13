import subprocess
import time
from fastapi import HTTPException
from app.dto.wifi_dto import WiFiConnectRequest
from app.utils.common import update_env_file


class WiFiService:

    def scan_wifi(self):
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL,SECURITY", "dev", "wifi"],
                capture_output=True,
                text=True,
                check=True  # Dừng chương trình nếu lệnh thất bại
            )

            if not result.stdout.strip():
                return []  # Không có kết quả, trả về danh sách rỗng

            wifi_dict = {}

            for line in result.stdout.strip().split("\n"):
                parts = line.split(":")
                if len(parts) < 4:
                    continue

                is_connected = parts[0] == "yes"
                ssid = parts[1].strip()
                if not ssid:  # Bỏ qua các SSID rỗng (Wi-Fi ẩn)
                    continue
                try:
                    signal = int(parts[2])  # Chuyển đổi tín hiệu sang số nguyên
                except ValueError:
                    continue  # Bỏ qua nếu tín hiệu không hợp lệ

                security = parts[3].strip()

                # Xác định số vạch tín hiệu (0-4)
                if signal >= 75:
                    bars = 4
                elif signal >= 50:
                    bars = 3
                elif signal >= 25:
                    bars = 2
                elif signal > 0:
                    bars = 1
                else:
                    bars = 0

                # Kiểm tra Wi-Fi có bảo mật hay không
                is_secure = security != "" and security != "--"  # Nếu SECURITY trống hoặc "--" thì là Wi-Fi mở

                if ssid not in wifi_dict or (
                        signal > wifi_dict[ssid]["Signal"] and wifi_dict[ssid]["isConnected"] is False):
                    wifi_dict[ssid] = {
                        "SSID": ssid,
                        "Signal": signal,
                        "Bars": bars,
                        "isConnected": is_connected,
                        "isSecure": is_secure,  # True = Có bảo mật, False = Mạng mở

                    }

            return list(wifi_dict.values())


        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi khi quét Wi-Fi: {e.stderr}")
            return []

    def connect_wifi(self, data: WiFiConnectRequest):
        try:
            # Chạy lệnh nmcli để kết nối WiFi
            result = subprocess.run(
                ["sudo", "nmcli", "device", "wifi", "connect", data.ssid, "password", data.password],
                capture_output=True, text=True)

            # Kiểm tra nếu kết nối thành công
            if "successfully activated" in result.stdout.lower():
                print(f"✅ Kết nối thành công tới {data.ssid}")
                update_env_file()
                return True
            else:
                # print(f"❌ Kết nối thất bại: {result.stderr.strip()}")
                # return False
                raise HTTPException(status_code=400, detail="Kết nối thất bại \n" + result.stderr.strip())

        except Exception as e:
            print(f"⚠️ Lỗi khi kết nối WiFi: {e}")
            return False

    def disconnect_wifi(self):
        try:
            # Lấy tên interface WiFi (thường là wlan0, wlp2s0, ...)
            interface_result = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
                                              capture_output=True, text=True)
            wifi_interface = None
            for line in interface_result.stdout.strip().split("\n"):
                parts = line.split(":")
                if len(parts) == 2 and parts[1] == "wifi":
                    wifi_interface = parts[0]
                    break

            if not wifi_interface:
                print("⚠️ Không tìm thấy interface WiFi!")
                return False

            # Ngắt kết nối WiFi
            result = subprocess.run(["sudo", "nmcli", "device", "disconnect", wifi_interface],
                                    capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Đã ngắt kết nối WiFi trên {wifi_interface}")
                return True
            else:
                print(f"❌ Ngắt kết nối thất bại: {result.stderr.strip()}")
                raise HTTPException(status_code=400, detail="Ngắt kết nối thất bại \n " + result.stderr.strip())
        except Exception as e:
            print(f"⚠️ Lỗi khi ngắt kết nối WiFi: {e}")
            raise HTTPException(status_code=400, detail="Ngắt kết nối thất bại")


wifi_service = WiFiService()
