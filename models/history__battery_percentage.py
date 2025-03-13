from tortoise.models import Model
from tortoise import fields


class HistoryBatteryPercentage(Model):
    id = fields.UUIDField(pk=True)
    wireless_button_id = fields.ForeignKeyField("models.WirelessButton", related_name="history_battery_percentage")
    v = fields.FloatField()
    percent = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = "history_battery_percentage"
