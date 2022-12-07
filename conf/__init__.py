from functools import cached_property
from pathlib import Path
from typing import ClassVar, Optional

from pydantic import BaseModel, Field, validator

from .base import BaseConfig, lazy_init
from utils.common import _merge_dict


class EmailConfig(BaseModel):
    """
    email 配置项
    """
    SERVER: str = Field(None)
    SENDER: str = Field(None)
    PORT: int = Field(None)
    TOKEN: str = Field(None)


class ConfigSettings(BaseConfig):
    config_namespace: ClassVar[str] = "global"

    class Config:
        keep_untouched = (cached_property,)

    @cached_property
    def BASE_DIR(self) -> Path:
        """
        项目的根目录。
        """
        cwd = Path.cwd()

        if not (cwd / "global.config.yaml").exists():
            raise RuntimeError("无法识别项目根目录, 请在根目录中启动进程, 根目录中要求存在 global.config.yaml 文件。")

        return cwd
    
    IS_INITIAL: bool = Field(False)
    SECRET: str = Field(None)



class APPSettings(BaseConfig):
    config_namespace: ClassVar[str] = "booking"

    class Config:
        keep_untouched = (cached_property,)


    @classmethod
    def _load_config_data(cls):
        local_config_data = cls._load_config_file(Path.cwd() / "config.yaml")
        cls._config_data = _merge_dict({}, local_config_data)


    @cached_property
    def BASE_DIR(self) -> Path:
        """
        项目的根目录。
        """
        cwd = Path.cwd()

        if not (cwd / "global.config.yaml").exists():
            raise RuntimeError("无法识别项目根目录, 请在根目录中启动进程, 根目录中要求存在 global.config.yaml 文件。")

        return cwd

    # DEBUG 模式。在 DEBUG 模式下, 会输出更多日志
    DEBUG_DB: bool = Field(default=True)

    # for encrypt password
    SECRET: str = Field("Gbqt-PqVXtbtRKioEeP1d8Vdy130epn6PtOEajVFu3E=")

    # 数据库配置
    DATABASE: str = Field(None)

    @validator("DATABASE", always=True, allow_reuse=True)
    def validate_database_dsn(cls, v: Optional[str]) -> str:
        if v is None:
            # 初始化时未提供 DATABASE 的值, 我们默认使用 sqlite
            print("[警告] 未设置 DATABASE, 默认使用: sqlite://")
            return "sqlite://"

        """
        TODO 检查 DATABASE 的值是否是 sqlalchemy 支持的 dsn, 
        见:https://docs.sqlalchemy.org/en/13/core/engines.html

        取值样例:
        * postgres: postgresql://{user}:{password}@{host}:{port}/{name}
        * mysql: mysql://{user}:{password}@{host}:{port}/{name}
        * sqlite (relative path): sqlite:///foo.db
        * sqlite (absolute path): sqlite:////path/to/foo.db
        * sqlite (:memory:): sqlite://
        """

        # 在 sqlalchemy 1.3 时, 支持 postgres://.. 的写法, 1.4 之后仅支持 postgresql://..
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://")
        return v

    EMAIL_CONFIG: EmailConfig = Field(default_factory=EmailConfig)


settings: APPSettings = lazy_init(APPSettings)
config_settings: ConfigSettings = ConfigSettings()

__all__ = ["settings", "config_settings", "BaseConfig", "lazy_init"]
