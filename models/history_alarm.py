from tortoise.models import Model
from tortoise import fields


class HistoryAlarm(Model):
    id = fields.UUIDField(pk=True)
    wireless_button_id = fields.ForeignKeyField("models.WirelessButton", related_name="history_alarm")
    created_at = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = "history_alarm"
