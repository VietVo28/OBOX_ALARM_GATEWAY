from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user"
