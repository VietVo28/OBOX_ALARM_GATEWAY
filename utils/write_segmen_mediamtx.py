import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import time

MTX_PATH = sys.argv[1]
MTX_SEGMENT_PATH = sys.argv[2]
MTX_SEGMENT_DURATION = float(sys.argv[3])
type = sys.argv[4]
path = sys.argv[5]
type_save = sys.argv[6]

current_working_directory = os.getcwd()
current_working_directory = current_working_directory.replace("\\", "/")
if type == "create":
    time.sleep(3)

try:
    with open(path, "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = []


# Regex để lấy thời gian từ đường dẫn
match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2}-\d+)", MTX_SEGMENT_PATH)
date_part = match.group(1)  # "2025-01-17"
time_part = match.group(2)  # "10-23-25-908175"

# Thay dấu '-' trong phần thời gian bằng dấu ':'
time_part = time_part.replace("-", ":", 2).replace("-", ".")

# Kết hợp thành chuỗi datetime
datetime_str = f"{date_part}T{time_part}"

# Chuyển chuỗi datetime thành đối tượng datetime
dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")

# Lấy offset múi giờ từ hệ thống
# Sử dụng time.timezone cho múi giờ chuẩn (UTC-)
# time.altzone là múi giờ vào mùa hè (DST)
offset_minutes = -time.timezone // 60  # time.timezone trả về giây, cần chia cho 60
if time.localtime().tm_isdst:
    offset_minutes = -time.altzone // 60  # Nếu là giờ mùa hè, sử dụng altzone

# Áp dụng offset vào datetime
dt_with_tz = dt.replace(tzinfo=timezone(timedelta(minutes=offset_minutes)))

# Chuyển đổi sang định dạng ISO 8601 với múi giờ
iso_8601 = dt_with_tz.isoformat()
iso_8601 = quote(iso_8601)

if type == "create":

    # Thêm dữ liệu mới
    data.append({
        "MTX_PATH": MTX_PATH,
        "MTX_SEGMENT_PATH": MTX_SEGMENT_PATH,
        "DURATION": MTX_SEGMENT_DURATION,
        "START_TIME": iso_8601,
        "current_working_directory": current_working_directory
    })
else:

    check = False
    # Cập nhật dữ liệu
    for item in data:
        if item["MTX_SEGMENT_PATH"] == MTX_SEGMENT_PATH:
            item["DURATION"] = MTX_SEGMENT_DURATION
            check = True
            break
    if not check:
        data.append({
            "MTX_PATH": MTX_PATH,
            "MTX_SEGMENT_PATH": MTX_SEGMENT_PATH,
            "DURATION": MTX_SEGMENT_DURATION,
            "START_TIME": iso_8601,
            "current_working_directory": current_working_directory
        })

if type_save == "default":
    for item in data:
        try:
            total, used, free = shutil.disk_usage(current_working_directory)
            gb = free // (1024 ** 3)
            mtx_path_save = current_working_directory + (item["MTX_SEGMENT_PATH"].replace("./", "/"))
            if not os.path.exists(mtx_path_save):
                data.remove(item)

            if gb < 2 and os.path.exists(mtx_path_save) and MTX_SEGMENT_PATH not in item["MTX_SEGMENT_PATH"]:
                print("Dung lượng ổ đĩa đã đạt ngưỡng 2GB, xóa file: ", mtx_path_save)
                data.remove(item)
                os.remove(mtx_path_save)
        except:
            continue

# Ghi lại vào file JSON
with open(path, "w") as file:
    json.dump(data, file, indent=4)

print("Dữ liệu đã được thêm thành công!")
