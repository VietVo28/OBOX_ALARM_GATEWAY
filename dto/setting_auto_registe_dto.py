from pydantic import BaseModel


class SettingAutoRegisterDTO(BaseModel):
    id_vms: str
    url_cloud_auto_register: str
    is_enable: bool


