import secrets

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from axionara import __version__

CONFIG_FILE = "config.yaml"
ENV_FILE = ".env"


class SysSetting(BaseSettings):
    # FastAPI
    VERSION: str = __version__
    PROJECT_NAME: str = "axionara"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 2
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False


class BasicSetting(BaseSettings):
    # database
    SQL_DATABASE_URI: str = ""
    SQL_POOL_PRE_PING: bool = True
    SQL_POOL_SIZE: int = 10
    SQL_MAX_OVERFLOW: int = 20
    SQL_POOL_TIMEOUT: int = 30
    SQL_POOL_RECYCLE: int = 1800

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ACCESS_TOKEN_SECRET_KEY: str = secrets.token_hex(32)


class LogSetting(BaseSettings):
    # logger
    LOG_ROOT: str = "./log"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_ENCODING: str = "utf-8"
    LOG_CONSOLE_OUTPUT: bool = True


class ServiceSetting(BaseSettings):
    # service
    GPT_PROMPT_FILEPATH: str = ""
    GPT_BASE_URL: str = ""
    GPT_API_KEY: str = ""
    GPT_DEFAULT_MODEL: str = "gpt-5-nano"
    GPT_TEMPERATURE: float = 0.8

    AGENT_MEMORY_SQL_TABLE: str = "chat_memory"
    AGENT_SYS_PROMPT_SUFFIX: str = ""
    AGENT_OPTIONAL_MODELS: list[str] = ["gpt-5-nano"]


class StorageSetting(BaseSettings):
    STORAGE_BACKEND: str = "minio"
    LOCAL_STORAGE_ROOT: str = "cache/storage"
    MINIO_ENDPOINT: str = "localhost:20005"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_RAW: str = "axionara-raw"
    MINIO_BUCKET_ANALYSIS: str = "axionara-analysis"
    MINIO_BUCKET_ARTIFACTS: str = "axionara-artifacts"


class Setting(SysSetting, BasicSetting, LogSetting, ServiceSetting, StorageSetting):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        _ = init_settings
        yaml_settings = YamlConfigSettingsSource(
            settings_cls=settings_cls, yaml_file=CONFIG_FILE, yaml_file_encoding="utf-8"
        )
        return yaml_settings, env_settings, dotenv_settings, file_secret_settings


settings = Setting()
