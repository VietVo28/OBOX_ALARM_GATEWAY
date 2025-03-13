from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ENVIRONMENT: str = "prod"
    PORT: int = 8004
    HOST_MEDIA: str = "localhost"

    HOST_LOCAL: str = "localhost"

    PORT_RTSP_MEDIA_MTX: int = 8554
    PORT_API_MEDIA_MTX: int = 9997
    PROTOCOL_MEDIA_MTX: str = "http"

    SECRET_KEY: str = "$2a$12$PaJpMSSZfZPVVXI1ZaperOR1EGxa9/NJGKe43D0AIwuUKnv3ix0nu"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30000

    URL_CLOUD_AUTO_REGISTER: str = "http://192.168.105.82:8000"

    MQTT_BROKER: str = "192.168.103.98"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = "linh"
    MQTT_PASSWORD: str = "1"




settings = Settings()
