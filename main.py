import asyncio
import logging
import os
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.core.setting_env import settings
from app.main import api_router
from app.utils.common import checkIsAarch64, public_server_ip
from app.utils.path_currrent_souce import current_source_path

from app.utils.mqtt import mqtt_client

from app.utils.sync_data_to_cloud import sync_data_to_cloud
from app.websocket.websocket import router as api_router_ws
from starlette.middleware.cors import CORSMiddleware

# Chỉ định logger của httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI()


# Cấu hình thư mục tĩnh và template

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(sync_data_to_cloud.sync_data())
    asyncio.create_task(mqtt_client.connect())
    # asyncio.create_task(receive_data_button.receive_data())
    if checkIsAarch64():
        from app.utils.recieve_data_button import receive_data_button
        threading.Thread(target=receive_data_button.start,daemon=True).start()
    threading.Thread(target=public_server_ip,daemon=True).start()
    # threading.Thread(target=host_wifi,daemon=True).start()
    yield
    print("Shutting down the server")



app = FastAPI(
    title="Oryza metadata FastAPI Backend",
    docs_url="/docs",
    lifespan=lifespan,
)
app.include_router(api_router, prefix="")



app.include_router(api_router_ws, prefix="/ws")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/", StaticFiles(directory="templates", html=True), name="static")

if __name__ == "__main__":
    file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(file_path)
    current_source_path.set(current_directory)

    path = os.path.join(current_directory, "data")
    if not os.path.exists(path):
        os.makedirs(path)

    if settings.ENVIRONMENT == "dev":
        uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=False)
