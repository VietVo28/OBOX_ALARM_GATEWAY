from tortoise.models import Model
from tortoise import fields


class Timeline(Model):
    id = fields.UUIDField(pk=True)
    id_camera = fields.ForeignKeyField("models.Camera", related_name="camera")
    duration = fields.FloatField()
    start_time = fields.CharField(max_length=255)
    name_file = fields.CharField(max_length=255)
    is_new = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "timeline"
