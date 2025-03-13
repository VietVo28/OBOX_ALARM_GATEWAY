import asyncio
import re

from app.dto.history_alarm_dto import history_alarm_create_DTO
from app.dto.history_battery_percentage_dto import HistoryBatteryPercentageCreateDTO
from app.dto.wireless_button_dto import WirelessUpdateDTO
from app.models.wireless_button import WirelessButton
from app.services.history_alarm_service import history_alarm_service
from app.services.history_battery_percentage_service import history_battery_percentage_service
from app.services.wireless_button_service import wireless_button_service
from app.services.camera_service import camera_service
from app.utils.mqtt import mqtt_client

from time import sleep
from SX127x.LoRa import *
from app.models.setting import Setting

from SX127x.board_config import BOARD
import datetime
import re
from app.websocket.ConnectionManager import connection_manager
import time
from app.utils.common import get_imei

BOARD.setup()


class ReceiveDataButton(LoRa):
    def __init__(self):
        super(ReceiveDataButton, self).__init__()
        self.pattern_battery = re.compile(r'^[A-F0-9]+:(\d+(\.\d+)?):(\d+(\.\d+)?)')
        self.pattern_alarm = re.compile(r'^[A-F0-9]+:alarm$')
        self.pattern_test = re.compile(r'^[A-F0-9]+:test$')

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.imei = get_imei()

    def start(self):
        try:
            self.set_mode(MODE.SLEEP)
            self.set_dio_mapping([0] * 6)

            self.set_mode(MODE.STDBY)
            self.set_freq(433.0)
            print(self.get_freq())

            self.receive_data()

        except Exception:
            sys.stdout.flush()
            print("thoat chuong trinh")
            sys.stderr.write("KeyboardInterrupt\n")
        finally:
            sys.stdout.flush()
            self.set_mode(MODE.SLEEP)
            BOARD.teardown()

    def stop(self):
        sys.stdout.flush()
        self.set_mode(MODE.SLEEP)
        BOARD.teardown()

    async def save_data_battery(self, data):
        parts = data.split(":")
        device_id = parts[0]
        percent = float(parts[1])
        voltage = float(parts[2])

        button = await WirelessButton.filter(sn=device_id).first()
        if button is not None:
            data_battery_save = HistoryBatteryPercentageCreateDTO(
                wireless_button_id=str(button.id),
                v=voltage,
                percent=percent,
            )
            data_save = await history_battery_percentage_service.create(data_battery_save)

            data_button_update = WirelessUpdateDTO(
                id=str(button.id),
                sn=device_id,
                v=voltage,
                percent=percent,
                name=button.name,
                status=True,
            )
            await wireless_button_service.update(data_button_update)
            await connection_manager.send_all(
                {"sn": device_id, "percent": percent, "voltage": voltage, "name": button.name, "id": str(data_save.id),
                 "id_button": str(button.id), "created_at": str(data_save.created_at), "type": "BATTERY"})

    async def save_data_alarm(self, data):
        device_id = data.split(":")[0]
        extis_key = await Setting.filter(key="CONNECT_MODE", value="ENABLE").first()
        button = await WirelessButton.filter(sn=device_id).first()
        print(data)

        if not extis_key:
            if button is not None:
                print("DA VAO ALARM")

                data_alarm_save = history_alarm_create_DTO(
                    wireless_button_id=str(button.id)
                )
                data_save = await history_alarm_service.create(data_alarm_save)
                # list_rtsp = await camera_service.get_all_rtsp()
                data_button_update = WirelessUpdateDTO(id=str(button.id), status=True)
                await wireless_button_service.update(data_button_update)
                payload = {"imei": self.imei, "time": time.time()}
                print(payload)
                await mqtt_client.send_mess("alarm/topic", payload)
                await connection_manager.send_all(
                    {"sn": device_id, "name": button.name, "id": str(data_save.id), "id_button": str(button.id),
                     "created_at": str(data_save.created_at), "type": "ALARM"})
            return

        print("DA VAO che do ket noi")

        await connection_manager.send_all({"sn": device_id, "is_exits": button is not None, "type": "CONNECT_MODE"})

    async def process_data(self, data):
        if self.pattern_battery.match(data):
            # print("DA VAO BATTERY")
            await self.save_data_battery(data)

        elif self.pattern_alarm.match(data):

            await self.save_data_alarm(data)

        elif self.pattern_test.match(data):
            print("test", data)

    def receive_data(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            try:
                sleep(.5)
                sys.stdout.flush()
            except Exception:
                continue

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        if not payload:
            return
        data = bytes(payload).decode("utf-8", 'ignore').replace("\x00", "").strip()
        data = re.sub(r'[^\x20-\x7E]', '', data)
        if not all(32 <= ord(c) <= 126 for c in data):
            data = re.sub(r'[^\x20-\x7E]', '', data)
        print(datetime.datetime.now(), repr(data))

        self.loop.run_until_complete(self.process_data(data))


receive_data_button = ReceiveDataButton()
