import asyncio
import uuid
import gmqtt

from app.core.setting_env import settings
from app.utils.common import get_imei


class MQTTClient:
    def __init__(self):
        self.MQTT_BROKER = settings.MQTT_BROKER
        self.MQTT_PORT = settings.MQTT_PORT
        CLIENT_ID = get_imei()

        MQTT_USERNAME = settings.MQTT_USERNAME
        MQTT_PASSWORD = settings.MQTT_PASSWORD

        self.client = gmqtt.Client(CLIENT_ID)
        self.client.set_auth_credentials(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.is_connected = False

    async def connect(self):
        while True:
            try:
                await self.client.connect(self.MQTT_BROKER, self.MQTT_PORT)  # Kết nối đến MQTT Broker
                self.is_connected = True
                break
            except Exception as e:
                print(f"❌ Failed to connect to MQTT broker: {e}")
                self.is_connected = False
                await asyncio.sleep(5)

    def on_connect(self, client, flags, rc, properties):
        print("✅ Connected to MQTT broker!")
        self.is_connected = True

    def on_disconnect(self, client, packet, exc=None):
        print("❌ Disconnected from MQTT broker!")
        self.is_connected = False

    async def send_mess(self, TOPIC, message, qos=0):
        if not self.is_connected:
            return
        for i in range(3):
            try:
                self.client.publish(TOPIC, message, qos=qos)
                break
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
                await asyncio.sleep(2)


mqtt_client = MQTTClient()
