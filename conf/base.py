import yaml
from pathlib import Path
from typing import Union, List, Type, TypeVar, ClassVar, Dict
from pydantic import BaseModel

from utils.functional import SimpleLazyObject
from utils.common import _merge_dict


class BaseConfig(BaseModel):
    # 在 config.yaml 中, 顶层 namespace
    """config.yaml
    namespace:
        item1: 
        item2:
        ...
    """
    config_namespace: ClassVar[Union[str, List[str]]] = None  # type: ignore[assignment]

    _config_data: ClassVar[Dict] = None  # type: ignore[assignment]

    def __init__(self):
        if not self.__class__.config_namespace:
            raise Exception(f"{self.__class__.__name__}.config_namespace not set.")

        if self.__class__._config_data is None:
            self.__class__._load_config_data()

        config_data = self._get_namespaced_data(self.__class__._config_data, self.__class__.config_namespace)
        super().__init__(**config_data)

    @classmethod
    def _get_namespaced_data(
        cls: Type["BaseConfig"], root: dict, namespace: Union[str, List[str]]
    ) -> Union[dict, Type["BaseConfig"]]:
        if isinstance(namespace, str):
            return root.get(namespace, {})
        elif isinstance(namespace, list):
            if len(namespace) == 0:
                return root
            return cls._get_namespaced_data(root.get(namespace[0], {}), namespace[1:])
        else:
            raise RuntimeError(f"{cls.__name__}.config_namespace must be str or list of str")

    @classmethod
    def _load_config_data(cls):
        local_config_data = cls._load_config_file(Path.cwd() / "global.config.yaml")
        cls._config_data = _merge_dict({}, local_config_data)

    @classmethod
    def _load_config_file(cls, file: Path) -> dict:
        if not file.exists():
            print(f"忽略不存在的配置文件: {file}")
            return {}

        try:
            with file.open(encoding="utf-8") as fp:
                data = yaml.safe_load(fp)
        except Exception:
            print(f"加载配置文件失败: {file}")
            raise

        env_data = {}

        data = _merge_dict(data, env_data)
        return data


ConfigType = TypeVar("ConfigType", bound=BaseConfig)


def lazy_init(ConfigClass: Type[ConfigType]) -> ConfigType:
    return SimpleLazyObject(lambda: ConfigClass())  # type: ignore[return-value,operator]
