from tortoise.models import Model
from tortoise import fields


class WirelessButton(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    sn = fields.CharField(max_length=255)
    status = fields.BooleanField(default=True)
    v = fields.FloatField(null=True)
    percent = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "wireless_button"
