from pydantic import BaseModel

class WiFiConnectRequest(BaseModel):
    ssid: str
    password: str