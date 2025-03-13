from fastapi import APIRouter, FastAPI
from app.routes import (
    camera_router, user_router, wireless_button_router,history_battery_percentage_router,history_alarm_router,setting_router,
setting_auto_register_router, wifi_router
)

app = FastAPI()
api_router = APIRouter()

# # Hàm tự động load tất cả routers từ thư mục routes
# def auto_load_routers(router: APIRouter, package: str):
#     # Duyệt qua các module trong package `routes`
#     package_path = package.replace('.', '/')
#     for module_info in pkgutil.iter_modules([package_path]):
#         module_name = f"{package}.{module_info.name}"
#         print(module_name)
#         module = importlib.import_module(module_name)
#
#         # Kiểm tra xem module có thuộc tính `router` không
#         if hasattr(module, 'router'):
#             # Lấy prefix và tags từ module, nếu không có thì dùng giá trị mặc định
#             prefix = getattr(module, 'prefix', f"/{module_info.name}")
#             tags = getattr(module, 'tags', [module_info.name])
#             # Thêm router vào api_router
#             router.include_router(
#                 getattr(module, 'router'),
#                 prefix=prefix,
#                 tags=tags
#             )


# Gọi hàm auto_load_routers để đăng ký tất cả các router
# auto_load_routers(api_router, 'app.routes')

# Đăng ký api_router vào ứng dụng
api_router.include_router(camera_router.router, prefix="/camera", tags=["camera"])
api_router.include_router(user_router.router, prefix="/user", tags=["user"])
api_router.include_router(wireless_button_router.router, prefix="/wireless-button", tags=["wireless-button"])

api_router.include_router(history_battery_percentage_router.router, prefix="/history-battery-percentage", tags=["history-battery-percentage"])

api_router.include_router(history_alarm_router.router, prefix="/history-alarm", tags=["history-alarm"])
api_router.include_router(setting_router.router, prefix="/setting", tags=["setting"])
api_router.include_router(setting_auto_register_router.router, prefix="/setting-auto-register", tags=["setting-auto-register"])
api_router.include_router(wifi_router.router, prefix="/wifi", tags=["wifi"])

app.include_router(api_router)
