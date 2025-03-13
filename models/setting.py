from tortoise.models import Model
from tortoise import fields


class Setting(Model):
    id = fields.UUIDField(pk=True)
    key = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "setting"
