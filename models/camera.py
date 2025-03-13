from tortoise.models import Model
from tortoise import fields


class Camera(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    ip = fields.CharField(max_length=255)
    sn = fields.CharField(max_length=255, null=True)
    status = fields.BooleanField(default=False)
    port = fields.IntField(default=80)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    rtsp = fields.CharField(max_length=255)

    id_camera_product = fields.CharField(max_length=255,null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "camera"
