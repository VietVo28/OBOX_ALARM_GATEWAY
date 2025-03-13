import datetime
import os
import subprocess
import urllib.parse
import json
import re
import time
from datetime import datetime, timezone
from datetime import timedelta
from urllib.parse import quote
import ffmpeg

from app.utils.common import get_local_ipv4

# Constants
CONCATENATION_TOLERANCE = timedelta(milliseconds=500)


def convert_to_datetime(time_str):
    match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2}-\d+)", time_str)
    date_part = match.group(1)  # "2025-01-17"
    time_part = match.group(2)  # "10-23-25-908175"

    # Thay dấu '-' trong phần thời gian bằng dấu ':'
    time_part = time_part.replace("-", ":", 2).replace("-", ".")

    # Kết hợp thành chuỗi datetime
    datetime_str = f"{date_part}T{time_part}"

    # Chuyển chuỗi datetime thành đối tượng datetime
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")


def segment_fmp4_can_be_concatenated(prev_end, cur_start):
    return (
            not (cur_start < prev_end - CONCATENATION_TOLERANCE) and
            not (cur_start > prev_end + CONCATENATION_TOLERANCE)
    )


def convert_to_iso_8601(time_data_time):
    offset_minutes = -time.timezone // 60  # time.timezone trả về giây, cần chia cho 60
    if time.localtime().tm_isdst:
        offset_minutes = -time.altzone // 60  # Nếu là giờ mùa hè, sử dụng altzone

    # Áp dụng offset vào datetime
    dt_with_tz = time_data_time.replace(tzinfo=timezone(timedelta(minutes=offset_minutes)))

    # Chuyển đổi sang định dạng ISO 8601 với múi giờ
    iso_8601 = dt_with_tz.isoformat()
    iso_8601 = quote(iso_8601)
    return iso_8601


def get_video_duration(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        print(f"Lỗi: {e}")
        return 0


def convert_time(name_file):
    match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2}-\d+)", name_file)
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
    return iso_8601


def read_time_line(id_camera, list_time_line):
    ip_V4 = get_local_ipv4()

    prevStart = None
    out = []
    for item in list_time_line:
        start = convert_to_datetime(item.name_file)
        duration = item.duration

        start_iso_8601 = convert_to_iso_8601(start)

        if len(out) != 0 and duration != -1 and segment_fmp4_can_be_concatenated(
                prevStart + timedelta(seconds=out[-1]["duration"]), start):
            curEnd = start + timedelta(seconds=duration)
            d = curEnd - prevStart
            out[-1]["duration"] = d.total_seconds()
        else:
            out.append({"start": start_iso_8601, "duration": duration})
            prevStart = start


    for d in out:
        dur = d["duration"] if d["duration"] != -1 else 999999999
        d["url"] = f"http://{ip_V4}:9996/get?path={id_camera}&start={d['start']}&duration={dur}"
        d["start"] = urllib.parse.unquote(d["start"])

    return out
