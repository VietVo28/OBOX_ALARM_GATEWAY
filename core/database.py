import importlib
import os

from tortoise import Tortoise

from app.dto.user_dto import UserRegisterDTO
from app.models.user import User
from app.services.user_service import user_service


def load_models():
    # Xác định thư mục chứa models từ thư mục hiện tại
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Lấy thư mục cha của "core"
    models_dir = os.path.join(base_dir, "models")  # Tạo đường dẫn tới thư mục models
    document_models = []
    # Duyệt qua các file trong thư mục models
    for filename in os.listdir(models_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"app.models.{filename[:-3]}"
            document_models.append(module_name)

    return document_models


async def init_db():
    # models = load_models()
    await Tortoise.init(
        db_url='sqlite://data/db.sqlite3',
        modules={'models': ['app.models.camera', 'app.models.history__battery_percentage', 'app.models.history_alarm',
                            'app.models.setting', 'app.models.user', 'app.models.wireless_button',"app.models.setting_auto_register","app.models.timeline"]},
    )
    await Tortoise.generate_schemas()

    list_user = await User.all()
    if len(list_user) == 0:
        await  user_service.register_user(UserRegisterDTO(username="admin", password="admin"))
