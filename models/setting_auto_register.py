from tortoise.models import Model
from tortoise import fields


class SettingAutoRegister(Model):
    id = fields.UUIDField(pk=True)

    id_vms = fields.CharField(max_length=255)
    url_cloud_auto_register = fields.CharField(max_length=255)

    ip_media_mtx = fields.CharField(max_length=255, null=True)
    port_media_mtx = fields.IntField(default=80)
    relay_address = fields.CharField(max_length=255, null=True)
    relay_port = fields.IntField(default=80)
    is_enable = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "setting_auto_register"
